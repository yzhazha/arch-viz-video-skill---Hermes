# 2026-05-09 备份 — arch-viz-video Skill

> 备份时间：2026-05-09
> 备份内容：arch-viz-video Skill 完整配置
> Hermes Agent 版本：MiniMax-M2.7 / provider: minimax-cn

---

## 📦 备份内容

```
arch-viz-video/
├── SKILL.md          ← Skill 工作流说明（Agent 调用规范）
├── README.md         ← 安装配置指南
└── scripts/
    ├── _libtv_base.py       ← API 公共模块
    ├── change_project.py    ← 新建项目画布
    ├── create_session.py    ← 创建会话/发送消息
    ├── download_results.py  ← 批量下载结果
    ├── query_session.py     ← 轮询查询进展
    ├── run_arch_image.py    ← 一键建筑效果图工作流
    ├── run_arch_video.py    ← 一键建筑动画工作流
    └── upload_file.py       ← 上传首帧图片
```

---

## 🖥️ 当前运行环境详细设置

### 系统环境
- **操作系统**：WSL（Windows Subsystem for Linux）
- **WSL 挂载点**：`/mnt/c/` = C:\ 驱动器
- **Python 版本**：Python 3.x
- **工作目录**：`/home/aatu/.hermes/ai-workshop-bot/`

### Hermes Agent 配置
- **模型**：MiniMax-M2.7
- **Provider**：minimax-cn
- **Home Channel**：feishu（飞书）
- **Session Source**：Feishu DM（用户 ID：3gcd5882）

### 关键环境变量（需配置）
```bash
LIBTV_ACCESS_KEY="sk-lib..."     # LibTV 平台 Access Key（必填）
OPENAPI_IM_BASE="https://im.liblib.tv"   # 默认值，可不设置
FEISHU_APP_ID="..."             # 飞书应用 App ID（如使用飞书发送）
FEISHU_APP_SECRET="..."         # 飞书应用 App Secret
```

### 飞书发送配置
- **发送方式**：`send_message` + `MEDIA:/mnt/c/Users/admin/.openclaw/media/tool-image-generation/` + WSL 绝对路径
- **默认目标 Chat ID**：`oc_36fc46ac3098b43dbfd94c3c62691515`
- **本地媒体目录**：`C:\Users\admin\.openclaw\media\tool-image-generation\`
- **下载缓存目录**：`~/Downloads/libtv_results/`

### libTV 生图工作流（标准规范）
1. `change_project()` → 新建项目，获取新 projectUuid
2. `upload_file.py` → 上传底图获取 OSS URL
3. `create_session` → 发送任务（带底图 URL + 提示词）
4. `query_session` → 全量查询找 previewPath（轮询策略：视频每60秒，图片每15秒）
5. `curl` 下载 previewPath → `~/Downloads/libtv_results/`
6. 复制到 `/mnt/c/Users/admin/.openclaw/media/tool-image-generation/`
7. `send_message` + `MEDIA:/mnt/c/...` 发送

---

## 🧠 当前 Hermes Agent 记忆内容

### USER PROFILE（用户档案）
```
主人身份：AIGC艺术总监，名称姚博龙，专业建筑可视化效果图总监
沟通风格：专业、直接、高效，不喜欢绕弯子
图片/视频交付方式：
  - 下载到 ~/Downloads/libtv_results/
  - 复制到 /mnt/c/Users/admin/.openclaw/media/tool-image-generation/
  - 用 send_message + MEDIA:/mnt/c/... 格式发送到飞书
  - OpenClaw 自动处理上传，无需 drive 权限
  - 图片和视频均用 WSL 绝对路径 /mnt/c/...
Vision API（MiniMax）鉴权有问题，401 报错，但不影响 libTV 生图
```

### MEMORY（工作笔记）
```
libTV生图工作流（标准流程）：
  1. 切换新项目 → change_project() → 获取新projectUuid和新projectUrl
  2. 上传底图 → upload_file.py → 获取OSS URL
  3. 创建会话 → create_session.py（带上底图OSS URL和详细prompt）
  4. 轮询等待 → query_session.py（每8秒轮询，增量拉取）
  5. 生成完成后下载 → curl下载previewPath的PNG
  6. 推送结果格式严格按标准格式

libTV图片/视频交付流程（必须严格遵守）：
  1. 下载到 ~/Downloads/libtv_results/
  2. 复制到 /mnt/c/Users/admin/.openclaw/media/tool-image-generation/
  3. 用 send_message + MEDIA:/mnt/c/... 发送（OpenClaw自动处理，无需drive权限）
  4. 推送标准格式：媒体链接（原图/原视频URL）+ 项目画布 + 生成参数

Feishu视频发送已解决（2026-05-09）：
  - 根因：之前尝试用send_message的MEDIA格式，但路径格式错误（Windows vs WSL）
  - 方案：MEDIA:/mnt/c/Users/admin/.openclaw/media/tool-image-generation/视频名.mp4
  - 关键：必须用WSL绝对路径 /mnt/c/...，不能用Windows路径 C:\...
  - OpenClaw自动处理上传和发送，无需drive权限
```

---

## 🔄 恢复步骤

### 完整恢复（在新机器上）

```bash
# 1. 克隆仓库
git clone https://github.com/yzhazha/skill-数智工作组-Hermes.git
cd skill-数智工作组-Hermes

# 2. 取出最新备份
LATEST=$(ls -d 20*/ | sort | tail -1)
cp -r "$LATEST/arch-viz-video/" ~/.hermes/skills/arch-viz-video/

# 3. 配置环境变量
# 编辑 ~/.hermes/ai-workshop-bot/.env 或通过 hermes config edit
LIBTV_ACCESS_KEY="你的Access Key"

# 4. 验证
python3 ~/.hermes/skills/arch-viz-video/scripts/change_project.py
```

### 恢复到指定日期
```bash
# 查看所有备份
ls -d 20*/

# 恢复指定日期（如 2026-05-09）
cp -r 2026-05-09/arch-viz-video/ ~/.hermes/skills/arch-viz-video/
```

---

## 📅 版本记录

| 日期 | 备份内容 | 备注 |
|------|---------|------|
| 2026-05-09 | arch-viz-video v1.0.0 | 首次备份，包含建筑动画+效果图一键工作流 |

---

## 🔗 相关链接

- **GitHub 仓库**：https://github.com/yzhazha/skill-数智工作组-Hermes
- **LibTV 平台**：https://www.liblib.tv
- **Hermes Agent**：https://hermes-agent.nousresearch.com/docs
