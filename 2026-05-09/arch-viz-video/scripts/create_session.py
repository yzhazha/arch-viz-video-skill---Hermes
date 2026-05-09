#!/usr/bin/env python3
"""创建会话 / 向会话发送消息：POST /openapi/session"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _libtv_base import create_session, build_project_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="创建会话或向已有会话发送消息（用于生图、生视频）")
    parser.add_argument("message", nargs="?", default="", help="要发送的消息内容")
    parser.add_argument("--session-id", default="", help="已有会话 ID，不传则创建新会话")
    args = parser.parse_args()
    data = create_session(session_id=args.session_id or "", message=args.message or "")
    project_uuid = data.get("projectUuid", "")
    session_id = data.get("sessionId", "")
    if not session_id:
        print("错误：未返回 sessionId", file=sys.stderr)
        sys.exit(1)
    out = {
        "projectUuid": project_uuid,
        "sessionId": session_id,
        "projectUrl": build_project_url(project_uuid),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
