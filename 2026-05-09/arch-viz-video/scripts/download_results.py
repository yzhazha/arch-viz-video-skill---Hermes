#!/usr/bin/env python3
"""下载生成结果：从会话中提取图片/视频 URL 并批量下载"""
import argparse, json, os, re, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(__file__))
from _libtv_base import query_session


def extract_urls_from_messages(messages):
    urls = []
    for msg in messages:
        content = msg.get("content", "")
        if not content or not isinstance(content, str):
            continue
        if msg.get("role") == "tool":
            try:
                data = json.loads(content)
                task_result = data.get("task_result", {})
                for img in task_result.get("images", []):
                    preview = img.get("previewPath", "")
                    if preview:
                        urls.append(preview if preview.startswith("http") else f"https://libtv-res.liblib.art{preview}")
                for vid in task_result.get("videos", []):
                    preview = vid.get("previewPath", vid.get("url", ""))
                    if preview:
                        urls.append(preview if preview.startswith("http") else f"https://libtv-res.liblib.art{preview}")
            except (json.JSONDecodeError, AttributeError):
                pass
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def make_unique_path(filepath):
    if not os.path.exists(filepath):
        return filepath
    base, ext = os.path.splitext(filepath)
    from datetime import datetime
    ts = datetime.now().strftime("%H%M%S")
    return f"{base}_{ts}{ext}"


def download_file(url, filepath):
    filepath = make_unique_path(filepath)
    req = urllib.request.Request(url, headers={"User-Agent": "LibTV-Skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, "wb") as f:
                while chunk := resp.read(8192):
                    f.write(chunk)
        return filepath, None
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        return filepath, str(e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="下载会话中生成的图片/视频")
    parser.add_argument("session_id", nargs="?", default="", help="会话 ID")
    parser.add_argument("--urls", nargs="+", default=[], help="直接指定 URL 列表")
    parser.add_argument("--output-dir", default="", help="输出目录（默认 ~/Downloads/libtv_results/）")
    parser.add_argument("--prefix", default="", help="文件名前缀")
    parser.add_argument("--workers", type=int, default=5, help="并行线程数（默认5）")
    parser.add_argument("--limit", type=int, default=0, help="最多下载 N 个（0=不限）")
    args = parser.parse_args()

    urls = list(args.urls)
    if args.session_id:
        data = query_session(args.session_id)
        extracted = extract_urls_from_messages(data.get("messages", []))
        urls.extend(extracted)

    if not urls:
        print(json.dumps({"error": "未找到可下载的 URL", "downloaded": []}, ensure_ascii=False, indent=2))
        sys.exit(1)

    output_dir = args.output_dir or os.path.expanduser("~/Downloads/libtv_results")
    os.makedirs(output_dir, exist_ok=True)

    tasks = []
    for i, url in enumerate(urls[:args.limit or len(urls)], 1):
        ext = os.path.splitext(url.split("?")[0])[-1] or ".png"
        filename = f"{args.prefix}_{i:02d}{ext}" if args.prefix else f"{i:02d}{ext}"
        tasks.append((url, os.path.join(output_dir, filename)))

    results, errors = [], []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(download_file, url, fp): (url, fp) for url, fp in tasks}
        for future in as_completed(futures):
            fp, err = future.result()
            (errors if err else results).append({"file": fp, "error": err} if err else fp)

    results.sort()
    output = {"output_dir": output_dir, "downloaded": results, "total": len(results), "urls_found": len(urls)}
    if errors:
        output["errors"] = errors
    print(json.dumps(output, ensure_ascii=False, indent=2))
