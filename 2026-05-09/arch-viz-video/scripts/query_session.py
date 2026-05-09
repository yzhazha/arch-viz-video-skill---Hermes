#!/usr/bin/env python3
"""查询会话进展：GET /openapi/session/:sessionId"""
import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _libtv_base import query_session, build_project_url

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="查询会话消息列表（轮询进展）")
    parser.add_argument("session_id", help="会话 ID")
    parser.add_argument("--after-seq", type=int, default=0, help="增量拉取起点（默认0=全量）")
    parser.add_argument("--project-id", default="", help="项目ID，传入则结果附带projectUrl")
    args = parser.parse_args()
    data = query_session(args.session_id, after_seq=args.after_seq)
    messages = data.get("messages", [])
    out = {"messages": messages}
    if args.project_id:
        out["projectUrl"] = build_project_url(args.project_id)
    print(json.dumps(out, ensure_ascii=False, indent=2))
