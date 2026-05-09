---
name: arch-viz-video
description: "建筑动画效果图生成 Skill — 专注于建筑可视化效果图和动画视频的全流程工作台。覆盖场景：以首帧图片生成建筑动画（5-15秒，16:9，Seedance 2.0 / Kling 3.0 等）、建筑效果图生成（MIR竞赛风/写实风）、批量分镜图生成。当用户提到「建筑动画」「效果图」「首帧动画」「建筑可视化」「来段建筑动画」时必须触发此技能。"
user-invocable: true
version: 1.0.0
category: media
metadata:
  hermes:
    tags: [archviz, architecture-visualization, video-generation, seedance, kling, libtv, 建筑动画, 效果图]
    primaryEnv: LIBTV_ACCESS_KEY
    requires:
      bins: [python3, curl]
      env: [LIBTV_ACCESS_KEY]
---

# arch-viz-video — 建筑动画效果图生成

建筑可视化效果图和动画视频的 AI 生成全流程工作台。专注于建筑效果图（竞赛风/商业风/写实风）和建筑动画视频（图生视频/首帧动画）。

**核心能力：**
- 以首帧图片生成建筑动画（Seedance 2.0 / Kling 3.0）
- 建筑效果图生成（MIR国际竞赛风、写实渲染风）
- 批量分镜图 / 故事板生成
- 建筑动画续写和风格调整

---

## 工作流（每次生成必须完整执行）

### 标准首帧动画工作流（最常用）

```
Step 1: 新建项目画布（change_project）
Step 2: 上传首帧图片（upload_file → OSS URL）
Step 3: 创建新会话（create_session → sessionId + projectUuid）
Step 4: 发送生成指令（create_session + message + sessionId）
Step 5: 轮询等待（query_session，增量轮询找 previewPath）
Step 6: curl 下载视频到 ~/Downloads/libtv_results/
Step 7: 复制到用户本地目录 + 通过飞书发送（MEDIA: 格式）
```

> ⚠️ **必须先 change_project 再 create_session**，禁止复用旧 session。session 绑定旧项目会导致生成结果写入错误的画布。

---

## 脚本说明

| 脚本 | 作用 |
|------|------|
| `scripts/run_arch_video.py` | **一键建筑动画工作流**：change_project → upload → create_session → 轮询 → 下载 → 推送 |
| `scripts/run_arch_image.py` | **建筑效果图工作流**：change_project → create_session → 轮询 → 下载 → 推送 |
| `scripts/_libtv_base.py` | LibTV API 公共模块（鉴权、请求、项目URL构建） |
| `scripts/upload_file.py` | 上传本地图片/视频到 OSS |
| `scripts/download_results.py` | 下载生成结果到本地 |

---

## 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `LIBTV_ACCESS_KEY` | ✅ | LibTV 平台的 Access Key，从 liblib.tv 获取 |
| `OPENAPI_IM_BASE` | 可选 | API 地址，默认 `https://im.liblib.tv` |

---

## 使用方式

### 方式一：一键脚本（推荐）

```bash
SKILL_DIR="/home/aatu/.hermes/skills/arch-viz-video"

# 首帧动画（建筑动画）
python3 "$SKILL_DIR/scripts/run_arch_video.py" \
  --first-frame /path/to/first_frame.jpg \
  --prompt "你的动画提示词" \
  --model seedance2.0 \
  --duration 5 \
  --ratio "16:9" \
  --resolution 720p

# 建筑效果图（MIR风）
python3 "$SKILL_DIR/scripts/run_arch_image.py" \
  --prompt "现代风格实训楼，MIR国际竞赛风，砖红色陶板..." \
  --model "nebula-ultra" \
  --ratio "16:9" \
  --count 1
```

### 方式二：逐步执行（调试用）

```bash
SKILL_DIR="/home/aatu/.hermes/skills/arch-viz-video"

# Step 1: 新建项目
python3 "$SKILL_DIR/scripts/change_project.py"

# Step 2: 上传首帧图片
python3 "$SKILL_DIR/scripts/upload_file.py" /path/to/first_frame.jpg

# Step 3 & 4: 创建会话并发送生成指令
python3 "$SKILL_DIR/scripts/create_session.py" \
  "底图URL：https://libtv-res.liblib.art/.../xxx.jpg
  请以首帧图片生成5秒动画，16:9，Seedance 2.0模型，720P。提示词：..."

# Step 5: 轮询（每60秒查一次，约等待2-4分钟）
python3 "$SKILL_DIR/scripts/query_session.py" SESSION_ID

# Step 6: 下载（从返回的 tool 消息 content JSON 中提取 previewPath）
curl -L "https://libtv-res.liblib.art/..." -o ~/Downloads/libtv_results/video.mp4
```

---

## 结果提取与推送

### 提取 previewPath

从 `role=tool` 消息的 `content` JSON 中提取：

```python
import re, json

data = query_session(session_id)
for msg in data["messages"]:
    if msg.get("role") == "tool":
        content_str = msg.get("content", "")
        # 提取 previewPath
        m = re.search(r'previewPath[\"\']?\s*:\s*[\"\'](https?://[^\"\']+)', content_str)
        if m:
            url = m.group(1)
            # 拼接完整URL（如需要）
            if not url.startswith("http"):
                url = "https://libtv-res.liblib.art" + url
            print("视频URL:", url)
```

### 飞书推送（必须严格遵守）

```
1. curl 下载到 ~/Downloads/libtv_results/
2. 复制到 /mnt/c/Users/admin/.openclaw/media/tool-image-generation/（WSL绝对路径）
3. send_message + MEDIA:/mnt/c/... 格式发送
4. 附上标准格式文字消息
```

#### 视频推送格式

```
🎬 **Seedance 2.0 建筑动画 — 生成完成**

📹 视频链接：https://libtv-res.liblib.art/.../xxx.mp4

🎞️ 项目画布：https://www.liblib.tv/canvas?projectId=...

📋 生成参数：
- ✅ 模型：Seedance 2.0
- ✅ 尺寸：16:9
- ✅ 分辨率：720P
- ✅ 时长：5秒
- ✅ 首帧参考：用户提供图片
```

#### 图片推送格式

```
🏗️ **建筑效果图 — 生成完成**

图片链接：https://libtv-res.liblib.art/.../xxx.png

项目画布：https://www.liblib.tv/canvas?projectId=...

📋 生成参数：
- ✅ 模型：Lib Nano Pro
- ✅ 尺寸：16:9
- ✅ 分辨率：2K
- ✅ 张数：1张
- ✅ 风格：MIR国际竞赛风
```

---

## 轮询策略

| 类型 | 生成时间 | 轮询策略 |
|------|---------|---------|
| 图片 | ~20-60秒 | 每15秒轮询一次 |
| 视频 | ~2-5分钟 | 每60秒轮询一次 |

**等待节奏（视频）：**
1. 提交后立即等待 **45秒**
2. 开始轮询，每60秒查一次
3. 连续 **6次**（约6分钟）无 `previewPath` → 告知用户稍后再查看画布

**判断完成：** `role=tool` 消息中出现 `previewPath` 字段 → 拼接完整URL → 下载。

---

## 核心原则

1. **每次生成必须新建项目**：`change_project()` → 新 projectUuid → 新 sessionId
2. **用户侧只做搬运工**：原封不动传用户 prompt，不扩写、不润色、不翻译
3. **结果必须推送给用户**：生成完毕后通过飞书发送链接 + 本地文件路径
4. **不允许覆盖历史结果**：文件名冲突时加时间戳后缀

---

## 支持的模型

| 模型 | 类型 | 分辨率 | 时长 |
|------|------|--------|------|
| Seedance 2.0 | 图生视频 | 480p / 720p | 4-15秒 |
| Kling 3.0 / O3 | 图生视频 | 720p / 1080p | 5-15秒 |
| Lib Nano Pro | 文生图 | 1K / 2K / 4K | — |

---

## 目录结构

```
arch-viz-video/
├── SKILL.md                      ← 本文件
├── README.md                     ← 安装配置说明
└── scripts/
    ├── _libtv_base.py            ← 公共模块（API请求、鉴权）
    ├── change_project.py         ← 新建项目画布
    ├── upload_file.py            ← 上传图片/视频到OSS
    ├── create_session.py         ← 创建会话/发送消息
    ├── query_session.py          ← 轮询查询会话进展
    ├── download_results.py       ← 批量下载生成结果
    ├── run_arch_video.py         ← 一键建筑动画工作流（推荐）
    └── run_arch_image.py         ← 一键建筑效果图工作流
```
