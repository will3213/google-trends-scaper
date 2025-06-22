# Google Trends Scraper

English | [简体中文](README.md)

---

## Project Overview
Google Trends Scraper is an automation toolkit that collects Google Trends data for pre-defined keyword groups and posts the charts to a Feishu (Lark) chat via bot.  It is designed to run every day at **09:00 China Standard Time** on a tiny cloud instance (1 CPU / 1 GB RAM).

Key goals:
1. Track search-trend dynamics of the fast-moving AI ecosystem.
2. Produce publication-ready PNG charts with Chinese-compatible fonts.
3. Deliver the charts to your Feishu group automatically.

---

## Architecture at a Glance
```
┌────────────┐        ┌──────────────┐        ┌──────────────┐
│ scheduler  │──────▶│ run_trends…  │──────▶│ trends_api.py │
└────────────┘ 09:00 │ workflow     │        └──────────────┘
       ▲             │ (shell)                 │
       │             │                        ▼
       │             │        ┌──────────────┐
       │             └──────▶│ feishu_sender │──▶ Feishu group
       │                      └──────────────┘
       │ update_server.sh
       ▼ (one-click deploy)
    GitHub
```
* **`trends_api.py`** – Fetches Google Trends, draws Seaborn line chart, saves as `screenshots/<group>.png`.
* **`feishu_sender.py`** – Uploads PNGs to Feishu, assembles an interactive card, posts to webhook.
* **`run_trends_workflow.sh`** – One-shot local workflow: activates venv, runs the two Python scripts, backs-up & cleans images.
* **`scheduler.py`** – Long-running loop on server; wakes up at Beijing 09:00 each day and calls the workflow script.
* **`update_server.sh`** – Local helper that SSH-es into the server, pulls latest code, restarts `scheduler.py`.

---

## Directory Layout
```
.
├── trends_api.py            # main data-gathering script
├── feishu_sender.py         # main posting script
├── scheduler.py             # daily timer (server-side)
├── run_trends_workflow.sh   # orchestrates one complete run
├── update_server.sh         # one-click deploy helper
├── screenshots/             # png charts (auto-created)
├── logs/                    # run & image backups (auto-created)
└── venv/                    # python3 virtual-env (optional)
```

---

## Keyword Groups (`TREND_GROUPS`)
Both **`trends_api.py`** and **`feishu_sender.py`** contain an identical list named `TREND_GROUPS` with **15 groups**.  Each item is a dict with:
```python
{
    "name": "chat_models",            # unique slug, used in filenames
    "description": "Claude, Deepseek …",  # human-readable; used in Feishu card
    "keywords": ["claude", "deepseek", …] # (trends_api) list queried via pytrends
    "url": "…google.com/trends…"           # (feishu_sender) link displayed in card
}
```
Update **both** files when you add / rename groups to keep the workflow stable.

Current canonical list (2025-06-22):
1. chatgpt
2. gpt4o
3. chat_models – claude / deepseek / gemini / grok / qwen
4. ai_video_models – kling ai / pika ai / hailuo ai / veo ai / pixverse
5. ai_features – ai translate / ai write / chatpdf / ai content detector / pdf translator
6. ai_creative – ai video / ai image / animation
7. ai_tools – lovart / flowith / fellou / deepwiki / devin ai
8. ai_image_models – sora / midjourney / runway / freepik
9. platform_tools – civitai / flux ai / liblib / pollo ai
10. slide_tools – slidesgo / base44
11. ai_agents2 – trae ai / skywork / minimax agent
12. browser_tools – dia browser / arc browser / dify ai / coze
13. ai_platforms – poe ai / perplexity / notebooklm / notion / gamma
14. ai_agents – manus / genspark / lovable / cursor / n8n
15. dev_tools – windsurf / codex / v0 / zapier / claude code

---

## Quick Start (local)
1. `git clone https://github.com/…/google-trends-scaper.git && cd google-trends-scaper`
2. `python3 -m venv venv && source venv/bin/activate`
3. `pip install -r <(echo "pytrends pandas matplotlib seaborn requests requests_toolbelt pytz")`
4. Configure Feishu creds in `feishu_sender.py`:
   ```python
   APP_ID = "cli_xxx"; APP_SECRET = "xxx"; FEISHU_WEBHOOK_URL = "https://open.feishu.cn/…"
   ```
5. Run once:
   ```bash
   ./run_trends_workflow.sh
   ```
   Charts will appear in `screenshots/` and Feishu chat.

---

## Deployment (Vultr Ubuntu 22.04)
1. Create a 1 vCPU / 1 GB instance, SSH in.
2. `git clone` the repo under `~/google-trends-scaper`.
3. Install Python >= 3.8 and run steps 2–3 of Quick Start.
4. Start the scheduler in the background:
   ```bash
   source venv/bin/activate
   nohup python3 scheduler.py > scheduler.log 2>&1 &
   ```
5. (Optional) Add to crontab `@reboot` to guarantee resurrection.

### One-click update
On your laptop run:
```bash
./update_server.sh
```
The script SSH-es, `git pull`, kills old scheduler, restarts it, and prints the process list.

---

## Logs & Back-ups
* `logs/trends_<timestamp>.log` – stdout / stderr of `trends_api.py`.
* `logs/feishu_<timestamp>.log` – stdout / stderr of `feishu_sender.py`.
* `logs/screenshots_<timestamp>/` – PNG copies before they are deleted from `screenshots/`.
* `scheduler.log` – combined log from the daily timer.

---

## Troubleshooting
| Symptom | Cause / Fix |
|---------|-------------|
| HTTP 429 from Google | IP rate-limited – script retries with exponential back-off; otherwise wait a few hours. |
| Chinese characters garbled | Install a font such as *SimHei* or *Arial Unicode MS* and rerun. |
| “Screenshot not found” in Feishu | Ensure filenames in `screenshots/` follow `<name>.png` and both scripts share identical `name`. |
| Feishu upload fails | Check APP_ID / APP_SECRET and `FEISHU_WEBHOOK_URL` validity. |

---

## Contributing
Pull-requests are welcome.  Please lint with `black` + `ruff`, and run the workflow script locally before submitting.

---

## License
MIT

---

# 项目简介 (中文)

## 项目概述
Google Trends Scraper 是一个自动化工具集，用于定时抓取预设关键词组的 Google Trends 数据，并将生成的趋势图表自动发送到飞书群（Lark）中。默认每天 **北京时间 09:00** 在云服务器上运行。

主要目标：
1. 跟踪 AI 生态系统高速变化的搜索热度。
2. 生成支持中文字体的高质量 PNG 折线图。
3. 全自动推送到飞书群，方便团队查看。

---

## 系统架构
```
┌────────────┐        ┌────────────────┐         ┌──────────────┐
│ scheduler  │──────▶│ run_trends…(sh)│ ───────▶│ trends_api.py │
└────────────┘ 09:00 │ 工作流脚本      │         └──────────────┘
       ▲             │                           │
       │             │                           ▼
       │             │         ┌──────────────┐
       │             └──────▶ │ feishu_sender │──▶ 飞书群
       │                        └──────────────┘
       │ update_server.sh
       ▼ 一键更新
    GitHub
```
各组件职责：
- **`trends_api.py`**：使用 pytrends 获取数据，调用 Seaborn 画图，保存在 `screenshots/<组名>.png`。
- **`feishu_sender.py`**：上传 PNG 至飞书，拼装卡片消息并通过 Webhook 推送。
- **`run_trends_workflow.sh`**：本地一次性运行流程（激活 venv → 获取数据 → 发送飞书 → 备份/清理图片）。
- **`scheduler.py`**：服务器常驻定时器，每天北京时间 09:00 调用工作流脚本。
- **`update_server.sh`**：本地辅助脚本，SSH 进入服务器，`git pull` 并重启 `scheduler.py`。

---

## 目录结构
```
.
├── trends_api.py            # 数据抓取脚本
├── feishu_sender.py         # 发送脚本
├── scheduler.py             # 定时器
├── run_trends_workflow.sh   # 工作流脚本
├── update_server.sh         # 一键更新脚本
├── screenshots/             # PNG 图片（自动创建）
├── logs/                    # 日志与图片备份（自动创建）
└── venv/                    # Python 虚拟环境（可选）
```

---

## 关键词组（`TREND_GROUPS`）
`trends_api.py` 和 `feishu_sender.py` 均包含同名列表 `TREND_GROUPS`，共 **15** 组。字段：
- `name`：唯一英文 slug，用于文件名
- `description`：中文/英文描述（飞书卡片中显示）
- `keywords`：关键词数组（仅在 `trends_api.py` 用来查询）
- `url`：Google Trends 链接（仅在 `feishu_sender.py` 用来展示）
> 修改关键词时务必同时更新两个脚本。

当前列表（2025-06-22）：
1. chatgpt
2. gpt4o
3. chat_models – claude / deepseek / gemini / grok / qwen
4. ai_video_models – kling ai / pika ai / hailuo ai / veo ai / pixverse
5. ai_features – ai translate / ai write / chatpdf / ai content detector / pdf translator
6. ai_creative – ai video / ai image / animation
7. ai_tools – lovart / flowith / fellou / deepwiki / devin ai
8. ai_image_models – sora / midjourney / runway / freepik
9. platform_tools – civitai / flux ai / liblib / pollo ai
10. slide_tools – slidesgo / base44
11. ai_agents2 – trae ai / skywork / minimax agent
12. browser_tools – dia browser / arc browser / dify ai / coze
13. ai_platforms – poe ai / perplexity / notebooklm / notion / gamma
14. ai_agents – manus / genspark / lovable / cursor / n8n
15. dev_tools – windsurf / codex / v0 / zapier / claude code

---

## 本地快速开始
```bash
# 克隆仓库并进入
git clone https://github.com/.../google-trends-scaper.git
cd google-trends-scaper

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install pytrends pandas matplotlib seaborn requests requests_toolbelt pytz

# 配置飞书凭证（编辑 feishu_sender.py）
APP_ID="cli_xxx"
APP_SECRET="xxx"
FEISHU_WEBHOOK_URL="https://open.feishu.cn/..."

# 运行完整工作流
./run_trends_workflow.sh
```
生成的 PNG 会出现在 `screenshots/`，并自动推送到飞书群。

---

## 服务器部署（Ubuntu 22.04）
```bash
# 服务器上
git clone https://github.com/.../google-trends-scaper.git
cd google-trends-scaper
python3 -m venv venv && source venv/bin/activate
pip install pytrends pandas matplotlib seaborn requests requests_toolbelt pytz
nohup python3 scheduler.py > scheduler.log 2>&1 &
```
可选：向 crontab 添加 `@reboot` 以保证开机自启。

### 一键更新
在本地运行：
```bash
./update_server.sh
```
脚本会执行 SSH、`git pull`、重启 `scheduler.py` 并打印进程列表。

---

## 日志与备份
- `logs/trends_<时间>.log` – 数据脚本输出
- `logs/feishu_<时间>.log` – 发送脚本输出
- `logs/screenshots_<时间>/` – 清理前的 PNG 备份
- `scheduler.log` – 定时器日志

---

## 常见问题
| 症状 | 可能原因 / 解决方案 |
|------|---------------------|
| Google 返回 429 | IP 被限速，脚本已带指数退避；可等待数小时后重试 |
| 中文乱码 | 安装 *SimHei* 或 *Arial Unicode MS* 字体后重新运行 |
| 飞书提示找不到截图 | 确认文件名 `<name>.png` 与 `TREND_GROUPS` 的 `name` 完全一致 |
| 飞书上传失败 | 检查 APP_ID / APP_SECRET / Webhook 是否正确 |

---

## 贡献
欢迎 PR。提交前请使用 `black` + `ruff` 格式化，并本地跑通工作流。

## 许可证
MIT

