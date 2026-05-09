# arch-viz-video 建筑动画效果图生成 Skill

**一句话总结：** 基于 liblib.tv（LibTV）平台，以首帧图片生成建筑动画视频，或直接生成建筑效果图的一站式 AI 工作台。

---

## 功能概览

| 功能 | 说明 |
|------|------|
| 首帧动画生成 | 以建筑效果图作为首帧，生成 5-15 秒建筑动画 |
| 建筑效果图生成 | MIR 国际竞赛风、写实渲染风效果图，支持 2K/4K |
| 多模型支持 | Seedance 2.0、Kling 3.0、Lib Nano Pro 等 |
| 飞书推送 | 生成完成后自动推送到飞书群/私聊 |

---

## 安装配置

### 1. 环境要求

- Python 3.8+
- curl
- WSL（Windows Subsystem for Linux）环境，脚本在 WSL 中运行
- liblib.tv 账号（需要 Access Key）

### 2. 获取 LibTV Access Key

1. 访问 [liblib.tv](https://www.liblib.tv) 并登录
2. 进入「开放平台」或「API」页面
3. 创建一个新的 Access Key（有效期、使用权限等）
4. 复制 Key，格式类似 `sk-lib...`

### 3. 配置环境变量

编辑 `~/.hermes/ai-workshop-bot/.env`（或通过 `hermes config edit`）：

```bash
LIBTV_ACCESS_KEY="你的Access Key"
```

**验证是否配置成功：**

```bash
python3 -c "import os; k=os.getenv('LIBTV_ACCESS_KEY',''); print(f'长度: {len(k)}')"
# 正常：长度 > 20
# 异常：长度 < 20（可能 key 被截断，需要重新获取）
```

### 4. 目录结构确认

```
~/.hermes/skills/arch-viz-video/
├── SKILL.md
├── README.md
└── scripts/
    ├── _libtv_base.py
    ├── change_project.py
    ├── upload_file.py
    ├── create_session.py
    ├── query_session.py
    ├── download_results.py
    ├── run_arch_video.py      ← 一键动画工作流
    └── run_arch_image.py      ← 一键效果图工作流
```

---

## 快速开始

### 方式一：使用一键脚本（推荐）

#### 生成建筑动画（首帧图片 → 动画）

```bash
SKILL_DIR="/home/aatu/.hermes/skills/arch-viz-video"

python3 "$SKILL_DIR/scripts/run_arch_video.py" \
  --first-frame /path/to/building.jpg \
  --prompt "现代风格实训楼，砖红色陶板搭配金属格栅与大面积玻璃幕墙。晴朗白昼，光影对比清晰锐利，蓝天白云。相机缓慢向前推进，匀速移动，模仿手持相机的轻微抖动。" \
  --model seedance2.0 \
  --duration 5 \
  --ratio "16:9" \
  --resolution 720p
```

#### 生成建筑效果图

```bash
SKILL_DIR="/home/aatu/.hermes/skills/arch-viz-video"

python3 "$SKILL_DIR/scripts/run_arch_image.py" \
  --prompt "现代风格实训楼，MIR国际竞赛风，砖红色陶板，金属格栅，玻璃幕墙，晴朗白昼，蓝天白云，建筑光影锐利，8K超高清，写实渲染" \
  --model nebula-ultra \
  --ratio "16:9" \
  --count 1
```

### 方式二：逐步执行（调试用）

```bash
SKILL_DIR="/home/aatu/.hermes/skills/arch-viz-video"
source ~/.hermes/ai-workshop-bot/.env

# Step 1: 新建项目画布
python3 "$SKILL_DIR/scripts/change_project.py"
# 输出: {"projectUuid": "xxx", "projectUrl": "https://..."}

# Step 2: 上传首帧图片
python3 "$SKILL_DIR/scripts/upload_file.py" /path/to/building.jpg
# 输出: {"url": "https://libtv-res.liblib.art/claw/..."}

# Step 3: 创建会话（拿到 sessionId）
python3 "$SKILL_DIR/scripts/create_session.py"
# 输出: {"sessionId": "xxx", "projectUuid": "xxx"}

# Step 4: 发送生成指令
python3 "$SKILL_DIR/scripts/create_session.py" \
  "底图URL：https://libtv-res.liblib.art/claw/xxx.jpg
  请以首帧图片生成5秒动画，16:9，Seedance 2.0模型，720P。
  提示词：现代风格实训楼..." \
  --session-id SESSION_ID

# Step 5: 轮询等待（每60秒查一次）
python3 "$SKILL_DIR/scripts/query_session.py" SESSION_ID
# 当看到 previewPath 时表示生成完成

# Step 6: 下载结果
curl -L "https://libtv-res.liblib.art/..." -o ~/Downloads/libtv_results/video.mp4
```

---

## 飞书推送配置

### 本地目录映射

生成完成后，文件需要复制到指定目录，飞书才能通过 OpenClaw 发送：

| 用途 | 路径 |
|------|------|
| 临时下载 | `~/Downloads/libtv_results/` |
| 飞书发送目录 | `/mnt/c/Users/admin/.openclaw/media/tool-image-generation/` |

```bash
# 复制到飞书发送目录（WSL路径）
cp ~/Downloads/libtv_results/video.mp4 \
   /mnt/c/Users/admin/.openclaw/media/tool-image-generation/video.mp4
```

### 通过 Hermes Agent 发送

在 Hermes Agent 中使用 `send_message` 工具：

```
发送目标：feishu:oc_36fc46ac3098b43dbfd94c3c62691515

消息格式：
MEDIA:/mnt/c/Users/admin/.openclaw/media/tool-image-generation/video.mp4

🎬 **建筑动画 — 生成完成**

📹 视频链接：https://libtv-res.liblib.art/.../xxx.mp4
🎞️ 项目画布：https://www.liblib.tv/canvas?projectId=...

📋 生成参数：
- ✅ 模型：Seedance 2.0
- ✅ 尺寸：16:9
- ✅ 分辨率：720P
- ✅ 时长：5秒
```

---

## 常见问题

### Q: 视频生成需要多久？

| 模型 | 通常时间 |
|------|---------|
| Seedance 2.0（5秒） | 2-4 分钟 |
| Kling 3.0（5秒） | 3-6 分钟 |

建议耐心等待，脚本会自动轮询直到出现 `previewPath`。

### Q: `LIBTV_ACCESS_KEY` 无效怎么办？

```bash
# 检查 key 实际长度
python3 -c "import os; print(len(os.getenv('LIBTV_ACCESS_KEY','')))"
# 正常 > 20位，如果只有 13 位说明被截断

# 修复：从 liblib.tv 重新获取完整 key，更新到 .env 文件
```

### Q: 轮询很久都没结果怎么办？

视频生成可能需要 3-5 分钟。如果轮询超过 6 分钟仍无结果：
- 告知用户稍后去「项目画布」查看
- 项目画布链接：`https://www.liblib.tv/canvas?projectId=xxx`

### Q: `afterSeq=0` 返回所有历史消息？

是的，这是 LibTV 的行为。轮询时需要从**当前消息数**作为基准点，每次查询 `afterSeq=基准点`，只关注新增消息。详见 `SKILL.md` 轮询策略部分。

---

## 提示词参考

### 建筑动画提示词模板

```
1. 主体与场景：[建筑类型]，[主要材质]，[结构特点]。精致建筑细节，清晰结构，完整建筑主体，无多余杂物

2. 光影与氛围：[时间]，[天气]，[光影描述]，[环境氛围]。营造出专业、现代、宁静的学术/商业氛围

3. 运镜与动画：相机[运动方式]，[速度描述]，[镜头描述]，展示建筑全貌

4. 画质与风格：照片级写实渲染，[分辨率]超高清分辨率，建筑可视化风格，细节精致，质感真实

5. 环境与配景：图面中的人物[活动描述]，马路上车辆[通行状态]，[景观描述]，天空干净，无杂乱元素，画面干净高级
```

### 建筑效果图提示词模板

```
[建筑类型]，[材质描述]，[颜色基调]，[时间]，[天气]，[光影描述]，[渲染风格]，建筑可视化风格，[氛围描述]，[分辨率]
```

---

## 脚本参数说明

### run_arch_video.py

| 参数 | 必填 | 说明 |
|------|------|------|
| `--first-frame` | ✅ | 首帧图片路径 |
| `--prompt` | ✅ | 动画提示词 |
| `--model` | ✅ | 模型名：`seedance2.0` / `kling-o3` |
| `--duration` | ✅ | 时长：4-15秒 |
| `--ratio` | ✅ | 比例：`"16:9"` / `"9:16"` / `"1:1"` |
| `--resolution` | ✅ | 分辨率：`480p` / `720p` / `1080p` |

### run_arch_image.py

| 参数 | 必填 | 说明 |
|------|------|------|
| `--prompt` | ✅ | 图片提示词 |
| `--model` | ✅ | 模型名：`nebula-ultra`（Lib Nano Pro）|
| `--ratio` | ✅ | 比例：`"16:9"` / `"4:3"` / `"1:1"` |
| `--count` | 否 | 生成数量，默认 1 |
