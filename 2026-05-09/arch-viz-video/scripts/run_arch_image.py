#!/usr/bin/env python3
"""
建筑效果图生成一键工作流
change_project → create_session → 轮询 → 下载 → 输出本地路径

用法:
  python3 run_arch_image.py --prompt "MIR国际竞赛风，现代建筑..." \
    --model nebula-ultra --ratio "16:9" --count 1
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_FILE = os.path.expanduser("~/.hermes/ai-workshop-bot/.env")
def load_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

load_env()

ACCESS_KEY = os.environ.get("LIBTV_ACCESS_KEY", "")
if not ACCESS_KEY:
    print("错误：请设置 LIBTV_ACCESS_KEY 环境变量", file=sys.stderr)
    sys.exit(1)


def run(script_name, *args):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    cmd = ["python3", script_path] + list(args)
    env = os.environ.copy()
    env["LIBTV_ACCESS_KEY"] = ACCESS_KEY
    result = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=SCRIPT_DIR)
    if result.returncode != 0:
        print(f"脚本执行失败 [{script_name}]: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def json_output(stdout):
    return json.loads(stdout)


def extract_preview_paths(query_output):
    """从 query_session 输出中提取所有图片 previewPath"""
    data = json.loads(query_output)
    urls = []
    for msg in reversed(data.get("messages", [])):
        if msg.get("role") == "tool":
            content = msg.get("content", "")
            try:
                c = json.loads(content)
                for img in c.get("task_result", {}).get("images", []):
                    p = img.get("previewPath", "")
                    if p:
                        urls.append(p if p.startswith("http") else f"https://libtv-res.liblib.art{p}")
            except (json.JSONDecodeError, AttributeError):
                pass
            # 也尝试正则
            for m in re.finditer(r'previewPath[\"\']?\s*:\s*[\"\'](https?://[^\"\']+\.(?:png|jpg|jpeg|webp))', content):
                urls.append(m.group(1))
    # 去重
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def download(url, filepath):
    if os.path.exists(filepath):
        base, ext = os.path.splitext(filepath)
        from datetime import datetime
        filepath = f"{base}_{datetime.now().strftime('%H%M%S')}{ext}"
    req = urllib.request.Request(url, headers={"User-Agent": "LibTV-Skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(filepath, "wb") as f:
                while chunk := resp.read(8192):
                    f.write(chunk)
        return filepath
    except Exception as e:
        print(f"下载失败: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="建筑效果图生成一键工作流（文生图）",
        epilog="""
示例:
  python3 run_arch_image.py --prompt "现代风格实训楼，MIR国际竞赛风..." \\
    --model nebula-ultra --ratio "16:9" --count 1
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--prompt", required=True, help="效果图提示词")
    parser.add_argument("--model", required=True,
                        help="模型: nebula-ultra(Lib Nano Pro) / seedance2.0 / kling-o3")
    parser.add_argument("--ratio", required=True,
                        choices=["16:9", "4:3", "1:1", "3:4"],
                        help="画面比例")
    parser.add_argument("--count", type=int, default=1,
                        help="生成数量（默认1）")
    parser.add_argument("--project-name", default="建筑效果图",
                        help="生成结果子目录名")
    args = parser.parse_args()

    print("=" * 50)
    print("  建筑效果图生成工作流")
    print("=" * 50)
    print(f"  提示词: {args.prompt[:60]}...")
    print(f"  模型: {args.model}  |  比例: {args.ratio}  |  数量: {args.count}")
    print("=" * 50)

    # Step 1: 新建项目画布
    print("\n[1/6] 新建项目画布...")
    step1 = json_output(run("change_project.py"))
    project_uuid = step1["projectUuid"]
    project_url = step1["projectUrl"]
    print(f"  项目ID: {project_uuid}")

    # Step 2: 创建新会话
    print("\n[2/6] 创建新会话...")
    step2 = json_output(run("create_session.py"))
    session_id = step2["sessionId"]
    if step2.get("projectUuid") != project_uuid:
        step2 = json_output(run("create_session.py", "--session-id", session_id))
    print(f"  SessionID: {session_id}")

    # Step 3: 发送生成指令
    print("\n[3/6] 提交生成任务...")
    model_label = args.model if args.model != "nebula-ultra" else "Lib Nano Pro"
    message = f"""请生成一张建筑效果图。

要求：
- 画面比例：{args.ratio}
- 数量：{args.count}张

提示词：
{args.prompt}"""

    run("create_session.py", message, "--session-id", session_id)
    print("  任务已提交...")

    # Step 4: 轮询等待
    print("\n[4/6] 轮询等待生成结果...")
    print("  (图片生成约需 30-90 秒)")

    time.sleep(20)

    POLL_INTERVAL = 15
    MAX_POLLS = 8

    for poll_round in range(1, MAX_POLLS + 1):
        print(f"  轮询 #{poll_round}/{MAX_POLLS}...")
        query_out = run("query_session.py", session_id, "--project-id", project_uuid)
        urls = extract_preview_paths(query_out)
        if urls:
            print(f"\n  ✅ 找到 {len(urls)} 个结果!")
            break
        print(f"  结果尚未出现，等待 {POLL_INTERVAL} 秒...")
        if poll_round < MAX_POLLS:
            time.sleep(POLL_INTERVAL)
    else:
        print("\n  ⚠️ 超过最大等待时间，请在项目画布查看:")
        print(f"  {project_url}")
        sys.exit(1)

    # Step 5: 下载
    print("\n[5/6] 下载图片到本地...")
    output_dir = os.path.expanduser(f"~/Downloads/libtv_results/{args.project_name}")
    os.makedirs(output_dir, exist_ok=True)

    downloaded_files = []
    urls_to_fetch = urls[:args.count] if args.count else urls

    for i, url in enumerate(urls_to_fetch, 1):
        if not url.startswith("http"):
            url = "https://libtv-res.liblib.art" + url
        ext = os.path.splitext(url.split("?")[0])[-1] or ".png"
        filename = f"{args.model}_{i:02d}{ext}"
        filepath = os.path.join(output_dir, filename)
        result = download(url, filepath)
        if result:
            size_kb = os.path.getsize(result) / 1024
            print(f"  [{i}/{len(urls_to_fetch)}] {result} ({size_kb:.0f} KB)")
            downloaded_files.append(result)

    # Step 6: 输出
    print("\n[6/6] 生成完成!")
    print("=" * 50)
    print(f"\n🏗️ 建筑效果图生成完成 ({len(downloaded_files)}张)\n")
    print(f"🎞️ 项目画布: {project_url}")
    print(f"💾 本地目录: {output_dir}")
    print(f"\n📋 生成参数:")
    print(f"  - ✅ 模型: {model_label}")
    print(f"  - ✅ 尺寸: {args.ratio}")
    print(f"  - ✅ 数量: {args.count}张")
    for f in downloaded_files:
        print(f"  📄 {f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
