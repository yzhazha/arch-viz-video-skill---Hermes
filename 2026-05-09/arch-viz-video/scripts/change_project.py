#!/usr/bin/env python3
"""切换当前 accessKey 绑定的项目：POST /openapi/session/change-project"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _libtv_base import change_project, build_project_url

data = change_project()
project_uuid = data.get("projectUuid", "")
if not project_uuid:
    print("错误：未返回 projectUuid", file=sys.stderr)
    sys.exit(1)
out = {"projectUuid": project_uuid, "projectUrl": build_project_url(project_uuid)}
print(json.dumps(out, ensure_ascii=False, indent=2))
