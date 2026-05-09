#!/usr/bin/env python3
"""
建筑动画生成一键工作流
change_project → upload_first_frame → create_session → 轮询 → 下载 → 输出本地路径

用法:
  python3 run_arch_video.py --first-frame /path/to.jpg --prompt "动画提示词" \
    --model seedance2.0 --duration 5 --ratio "16:9" --resolution 720p
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
LIBTV_BASE = os.path.dirname(SCRIPT_DIR)

# 从用户 .env 加载环境变量（支持 hermes-gateway 运行时注入的变量）
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
    print("  或确认 ~/.hermes/ai-workshop-bot/.env 中有 LIBTV_ACCESS_KEY", file=sys.stderr)
    sys.exit(1)


# ─── 辅助函数 ────────────────────────────────────────────────

def run(script_name, *args, capture=True):
    """执行 skill scripts 目录下的 Python 脚本"""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    cmd = ["python3", script_path] + list(args)
    env = os.environ.copy()
    env["LIBTV_ACCESS_KEY"] = ACCESS_KEY
    result = subprocess.run(
        cmd, capture_output=capture, text=True,
        env=env, cwd=SCRIPT_DIR
    )
    if result.returncode != 0:
        print(f"脚本执行失败 [{script_name}]: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def json_output(stdout):
    return json.loads(stdout)


def extract_preview_path(query_output):
    """从 query_session 输出中提取 previewPath（支持 JSON 和纯文本）"""
    data = json.loads(query_output)
    for msg in reversed(data.get("messages", [])):
        if msg.get("role") == "tool":
            content = msg.get("content", "")
            # 策略1：JSON 字段提取
            m = re.search(r'previewPath[\"\']?\s*:\s*[\"\'](https?://[^\"\']+)', content)
            if m:
                return m.group(1)
            # 策略2：从 task_result 结构提取
            try:
                c = json.loads(content)
                for vid in c.get("task_result", {}).get("videos", []):
                    p = vid.get("previewPath") or vid.get("url", "")
                    if p:
                        return p if p.startswith("http") else f"https://libtv-res.liblib.art{p}"
            except (json.JSONDecodeError, AttributeError):
                pass
    return None


def download(url, filepath):
    """下载文件（不覆盖已有文件）"""
    if os.path.exists(filepath):
        base, ext = os.path.splitext(filepath)
        from datetime import datetime
        filepath = f"{base}_{datetime.now().strftime('%H%M%S')}{ext}"
    req = urllib.request.Request(url, headers={"User-Agent": "LibTV-Skill/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(filepath, "wb") as f:
                while chunk := resp.read(8192):
                    f.write(chunk)
        return filepath
    except Exception as e:
        print(f"下载失败: {e}", file=sys.stderr)
        return None


# ─── 主流程 ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="建筑动画生成一键工作流（首帧图片 → 动画）",
        epilog="""
示例:
  python3 run_arch_video.py --first-frame ./test.jpg \\
    --prompt "相机缓慢向前推进，蓝天白云，建筑光影锐利" \\
    --model seedance2.0 --duration 5 --ratio "16:9" --resolution 720p
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--first-frame", required=True, help="首帧图片路径")
    parser.add_argument("--prompt", required=True, help="动画提示词")
    parser.add_argument("--model", required=True, choices=["seedance2.0", "kling-o3"],
                        help="模型：seedance2.0 或 kling-o3")
    parser.add_argument("--duration", required=True, type=int,
                        help="视频时长（秒），4-15秒")
    parser.add_argument("--ratio", required=True, choices=["16:9", "9:16", "1:1", "4:3"],
                        help="画面比例")
    parser.add_argument("--resolution", required=True, choices=["480p", "720p", "1080p"],
                        help="分辨率")
    parser.add_argument("--project-name", default="建筑动画",
                        help="生成结果保存的子目录名（默认: 建筑动画）")
    args = parser.parse_args()

    first_frame = os.path.abspath(args.first_frame)
    if not os.path.isfile(first_frame):
        print(f"错误：首帧图片不存在: {first_frame}", file=sys.stderr)
        sys.exit(1)

    print("=" * 50)
    print("  建筑动画生成工作流")
    print("=" * 50)
    print(f"  首帧: {first_frame}")
    print(f"  模型: {args.model}  |  时长: {args.duration}s  |  比例: {args.ratio}  |  分辨率: {args.resolution}")
    print("=" * 50)

    # ── Step 1: 新建项目画布 ──
    print("\n[1/7] 新建项目画布...")
    step1 = json_output(run("change_project.py"))
    project_uuid = step1["projectUuid"]
    project_url = step1["projectUrl"]
    print(f"  项目ID: {project_uuid}")
    print(f"  画布: {project_url}")

    # ── Step 2: 上传首帧图片 ──
    print("\n[2/7] 上传首帧图片...")
    step2 = json_output(run("upload_file.py", first_frame))
    first_frame_url = step2["url"]
    print(f"  OSS URL: {first_frame_url}")

    # ── Step 3: 创建新会话 ──
    print("\n[3/7] 创建新会话...")
    step3 = json_output(run("create_session.py"))
    session_id = step3["sessionId"]
    # 确保 session 绑定到新项目
    if step3.get("projectUuid") != project_uuid:
        print("  重新绑定到新项目...")
        step3 = json_output(run("create_session.py", "--session-id", session_id))
    print(f"  SessionID: {session_id}")

    # ── Step 4: 发送生成指令 ──
    print("\n[4/7] 提交生成任务...")
    model_display = "Seedance 2.0" if args.model == "seedance2.0" else "Kling 3.0"
    message = f"""底图URL：{first_frame_url}

请以首帧图片作为首帧，生成一段{args.duration}秒的动画，画面比例为{args.ratio}，采用{model_display}模型，{args.resolution}。

提示词如下：
{args.prompt}"""

    run("create_session.py", message, "--session-id", session_id)
    print("  任务已提交，等待后端处理...")

    # ── Step 5: 轮询等待 ──
    print("\n[5/7] 轮询等待生成结果...")
    print("  (视频生成约需 2-5 分钟，请耐心等待)")
    print("  等待 45 秒后开始轮询...")

    time.sleep(45)  # 首次等待

    POLL_INTERVAL = 60  # 每 60 秒轮询一次
    MAX_POLLS = 8       # 最多轮询 8 次（约 8 分钟）
    base_msg_count = 0

    for poll_round in range(1, MAX_POLLS + 1):
        print(f"\n  轮询 #{poll_round}/{MAX_POLLS}...")
        query_out = run("query_session.py", session_id, "--project-id", project_uuid)
        data = json.loads(query_out)
        msg_count = len(data.get("messages", []))

        preview_url = extract_preview_path(query_out)
        if preview_url:
            print(f"\n  ✅ 找到生成结果!")
            print(f"  预览URL: {preview_url}")
            break

        if poll_round == 1:
            base_msg_count = msg_count
        print(f"  当前消息数: {msg_count}，结果尚未出现，继续等待...")
        if poll_round < MAX_POLLS:
            print(f"  等待 {POLL_INTERVAL} 秒...")
            time.sleep(POLL_INTERVAL)
    else:
        print("\n  ⚠️ 超过最大等待时间，请在项目画布查看进度:")
        print(f"  {project_url}")
        sys.exit(1)

    # ── Step 6: 下载到本地 ──
    print("\n[6/7] 下载视频到本地...")

    # 修正完整 URL
    if not preview_url.startswith("http"):
        preview_url = "https://libtv-res.liblib.art" + preview_url

    output_dir = os.path.expanduser(f"~/Downloads/libtv_results/{args.project_name}")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{args.model}_{args.duration}s_{args.ratio}_{args.resolution}.mp4"
    filepath = os.path.join(output_dir, filename)

    downloaded = download(preview_url, filepath)
    if not downloaded:
        print("  下载失败，请手动复制预览URL:", preview_url)
        sys.exit(1)

    size_mb = os.path.getsize(downloaded) / 1024 / 1024
    print(f"  已保存: {downloaded}")
    print(f"  文件大小: {size_mb:.1f} MB")

    # ── Step 7: 输出结果 ──
    print("\n[7/7] 生成完成!")
    print("=" * 50)
    print("\n🎬 建筑动画生成完成\n")
    print(f"📹 视频链接: {preview_url}")
    print(f"🎞️ 项目画布: {project_url}")
    print(f"💾 本地路径: {downloaded}")
    print(f"\n📋 生成参数:")
    print(f"  - ✅ 模型: {model_display}")
    print(f"  - ✅ 尺寸: {args.ratio}")
    print(f"  - ✅ 分辨率: {args.resolution}")
    print(f"  - ✅ 时长: {args.duration}秒")
    print(f"  - ✅ 首帧参考: {os.path.basename(first_frame)}")
    print("=" * 50)

    # 输出飞书推送所需信息（供调用方提取）
    print(f"\n[FEISHU_MEDIA] {downloaded}")
    print(f"[FEISHU_URL] {preview_url}")
    print(f"[FEISHU_CANVAS] {project_url}")


if __name__ == "__main__":
    main()
