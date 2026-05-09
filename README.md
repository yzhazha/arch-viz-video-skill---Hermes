# skill-数智工作组-Hermes

> Hermes Agent 动画静帧优化 Skill 备份仓库

存储 `arch-viz-video` 等建筑可视化相关 Skill 的完整配置与历史版本，支持跨设备完整恢复。

---

## 📁 仓库结构

```
skill-数智工作组-Hermes/
├── README.md              ← 仓库总览（本文）
├── 2026-05-09/            ← 按日期组织的备份
│   ├── README.md          ← 当日备份详细说明
│   └── arch-viz-video/    ← Skill 完整代码
│       ├── SKILL.md
│       ├── README.md
│       └── scripts/
└── ...
```

---

## 🎯 备份说明

每次备份包含：
- **Skill 完整代码**：`SKILL.md` + `README.md` + `scripts/` 下所有脚本
- **当日详细设置**：系统环境、Python 版本、关键路径、飞书配置
- **记忆内容完整记录**：USER PROFILE + MEMORY 工作笔记

---

## 🔄 恢复方法

### 方式一：恢复到最新版本

```bash
git clone https://github.com/yzhazha/skill-数智工作组-Hermes.git
cd skill-数智工作组-Hermes

# 取最新备份日期
LATEST=$(ls -d 20*/ | sort | tail -1)
echo "最新备份: $LATEST"

# 复制到 Hermes skills 目录
cp -r "$LATEST/arch-viz-video/" ~/.hermes/skills/arch-viz-video/
```

### 方式二：恢复到指定日期

```bash
# 查看所有备份
ls -d 20*/

# 恢复指定日期
DATE="2026-05-09"
cp -r "$DATE/arch-viz-video/" ~/.hermes/skills/arch-viz-video/
```

---

## 🔧 恢复后配置

备份恢复后，仍需配置以下环境变量：

```bash
# 必填：LibTV Access Key
LIBTV_ACCESS_KEY="你的Access Key"

# 可选：如使用飞书发送
FEISHU_APP_ID="..."
FEISHU_APP_SECRET="..."

# 飞书发送路径（WSL 环境）
# 媒体文件复制到：/mnt/c/Users/admin/.openclaw/media/tool-image-generation/
```

---

## 📦 当前包含的 Skill

### arch-viz-video（建筑动画效果图）

专注于建筑可视化效果图和动画视频的全流程工作台。

**功能：**
- 以首帧图片生成建筑动画（Seedance 2.0 / Kling 3.0）
- 建筑效果图生成（MIR 国际竞赛风、写实渲染风）
- 批量分镜图 / 故事板生成

**一键命令：**
```bash
SKILL_DIR="~/.hermes/skills/arch-viz-video"

# 建筑动画（首帧 → 动画）
python3 "$SKILL_DIR/scripts/run_arch_video.py" \
  --first-frame /path/to/building.jpg \
  --prompt "相机缓慢向前推进..." \
  --model seedance2.0 --duration 5 --ratio "16:9" --resolution 720p

# 建筑效果图
python3 "$SKILL_DIR/scripts/run_arch_image.py" \
  --prompt "MIR国际竞赛风，现代建筑..." \
  --model nebula-ultra --ratio "16:9" --count 1
```

**详细文档：** 见各日期备份目录下的 `README.md`

---

## 📅 版本记录

| 日期 | Skill | 版本 | 备注 |
|------|-------|------|------|
| 2026-05-09 | arch-viz-video | v1.0.0 | 首次备份 |

---

## 🔗 相关链接

- **GitHub 仓库**：https://github.com/yzhazha/skill-数智工作组-Hermes
- **LibTV 平台**：https://www.liblib.tv
- **Hermes Agent 文档**：https://hermes-agent.nousresearch.com/docs

---

## 📝 新增备份

如需新增备份，按以下格式操作：

```bash
# 1. 在 skills 目录打包
DATE=$(date +%Y-%m-%d)
mkdir -p ~/github_backup/skill-数智工作组-Hermes/$DATE
cp -r ~/.hermes/skills/arch-viz-video/ ~/github_backup/skill-数智工作组-Hermes/$DATE/

# 2. 写入当日 README（参考 2026-05-09/README.md 格式）
# 3. 提交推送
cd ~/github_backup/skill-数智工作组-Hermes
git add $DATE/
git commit -m "Backup: $DATE"
git push origin master
```
