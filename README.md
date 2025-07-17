# Google Trends Scraper

一个自动化工具，用于抓取 Google Trends 热词趋势数据并发送到飞书群组。

## 项目概述

该项目是一个自动化系统，用于每日收集 Google Trends 上特定关键词的搜索趋势数据，并将这些数据以图片形式发送到飞书群组，便于团队跟踪和分析 AI 相关热词的搜索趋势变化。

### 核心功能

1. **数据获取**：使用 pytrends API 获取 Google Trends 数据并生成趋势图表
2. **飞书集成**：将图表上传到飞书并通过飞书机器人发送到指定群组
3. **自动化工作流**：提供完整的工作流脚本，确保数据获取和发送的顺序执行
4. **定时执行**：支持通过 cron 任务定时执行，实现每日自动汇报
5. **图片备份**：自动备份生成的趋势图表，并清理临时文件

## 项目结构

### 核心脚本

- `trends_api.py` - 获取 Google Trends 数据并生成趋势图表
- `feishu_sender.py` - 上传图表到飞书并发送消息
- `run_trends_workflow.sh` - 本地一键执行数据获取 + 发送的工作流脚本
- `scheduler.py` - 服务器常驻调度器，按设定间隔调用核心脚本
- `update_server.sh` - 服务器端一键更新脚本：拉取最新代码并重启 `scheduler.py`

### 目录结构

- `logs/` - 存储执行日志和备份的趋势图片
- `screenshots/` - 存储生成的趋势图表
- `venv/` - Python虚拟环境（推荐使用）

## 系统需求

- **操作系统**: macOS 或 Linux
- **Python**: 版本 3.7 或更高版本
- **依赖库**: 
  - pytrends
  - pandas
  - matplotlib
  - seaborn
  - requests
  - requests_toolbelt

## 安装步骤

1. 克隆或下载此仓库到您的计算机

2. 创建虚拟环境（可选）
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在 macOS/Linux 上
   # 或
   venv\Scripts\activate  # 在 Windows 上
   ```

3. 安装 Python 依赖
   ```bash
   pip install pytrends pandas matplotlib seaborn requests requests_toolbelt
   ```

4. 创建虚拟环境并安装依赖（推荐方式）
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # 在 macOS/Linux 上
   # 或
   venv\Scripts\activate  # 在 Windows 上
   pip install pytrends pandas matplotlib seaborn requests requests_toolbelt
   ```

   脚本会自动创建所需的目录结构（`screenshots/`和`logs/`）

## 配置

在使用前，您需要配置以下内容：

1. **飞书应用凭证**：在 `feishu_sender.py` 中设置您的飞书应用 ID 和密钥
   ```python
   APP_ID = "YOUR_APP_ID"  # 替换为您的飞书应用ID
   APP_SECRET = "YOUR_APP_SECRET"  # 替换为您的飞书应用密钥
   ```

2. **飞书机器人 Webhook**：在 `feishu_sender.py` 中设置您的飞书群组机器人 Webhook 地址
   ```python
   FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_KEY"
   ```

3. **热词分组**：根据需要修改 `feishu_sender.py` 和 `trends_api.py` 中的 `TREND_GROUPS` 列表

（配置步骤已在本 README 中完整说明）

## 使用方法

### 推荐方式：使用工作流脚本

使用工作流脚本可以确保数据获取和飞书发送按正确顺序执行。脚本已配置为使用虚拟环境：

```bash
# 运行完整工作流（数据获取 + 飞书发送 + 图片备份和清理）
./run_trends_workflow.sh
```

工作流脚本会：
1. 首先执行 `trends_api.py` 获取数据并生成图表
2. 检查数据获取是否成功
3. 如果成功，再执行 `feishu_sender.py` 发送到飞书
4. 将图片备份到 `logs/screenshots_YYYY-MM-DD_HH-MM-SS` 目录
5. 清理原始图片目录，避免磁盘空间浪费
6. 记录日志到 `logs` 目录

### 分步手动运行

如果您想分步手动运行，可以按以下顺序执行（建议使用虚拟环境）：

1. 运行数据获取脚本
   ```bash
   source venv/bin/activate  # 在 macOS/Linux 上
   python trends_api.py
   ```

2. 运行飞书发送脚本
   ```bash
   source venv/bin/activate  # 在 macOS/Linux 上
   python feishu_sender.py
   ```

### 设置定时任务

使用 crontab 设置定时任务，例如：

```bash
# 每日早上9:00执行完整工作流
0 9 * * * cd /path/to/google-trends-scraper && ./run_trends_workflow.sh
```

注意：脚本已配置为使用相对路径，所以需要先切换到项目目录再执行脚本。

## 日志和备份

工作流脚本会在 `logs` 目录下生成以下文件：

- `trends_YYYY-MM-DD_HH-MM-SS.log` - 数据获取脚本的日志
- `feishu_YYYY-MM-DD_HH-MM-SS.log` - 飞书发送脚本的日志
- `screenshots_YYYY-MM-DD_HH-MM-SS/` - 包含备份的趋势图片

这样您可以轻松查看每次执行的详细情况，并在需要时访问历史图表。

## 当前监控的热词

当前系统监控以下 15 组 AI 相关热词的搜索趋势（与 `TREND_GROUPS` 保持完全一致）：

1. **ChatGPT**（chatgpt）
2. **GPT-4o**（gpt4o）
3. **Chat 模型词**：claude, deepseek, gemini, grok, qwen
4. **AI 视频模型**：kling ai, pika ai, hailuo ai, veo ai, pixverse
5. **AI 功能词**：ai translate, ai write, chatpdf, ai content detector, pdf translator
6. **AI 创意工具**：ai video, ai image, animation
7. **AI 工具**：lovart, flowith, fellou, deepwiki, devin ai
8. **AI 图像模型**：sora, midjourney, runway, freepik
9. **平台工具**：civitai, flux ai, liblib, pollo ai
10. **幻灯片工具**：slidesgo, base44
11. **AI Agent 工具 II**：trae ai, skywork, minimax agent
12. **浏览器 / 工具**：dia browser, arc browser, dify ai, coze
13. **AI 平台**：poe, perplexity, notebooklm, notion, gamma
14. **AI Agent 工具**：manus, genspark, lovable, cursor, n8n
15. **开发工具**：windsurf, codex, kiro, zapier, claude code

## 更新日志

### 2025-06-04
- 重组所有监控关键词组，更清晰地分类和命名
- 添加新关键词：cursor、n8n、zapier、coze
- 更新各关键词组的搜索量数据
- 重命名部分组别："ai_agent" 改为 "ai_agent"，"ai_tools" 改为 "agentic_tools"
- 添加新组别 "dev_tools"

### 2025-05-27
- 添加新的关键词组：cursor/windsurf/codex
- cursor 全球月搜索量为 301K

## 服务器部署

本项目已部署在 Vultr 服务器上，配置如下：

- 服务器位置：Tokyo
- 操作系统：Ubuntu 22.04 x64
- 配置：1 vCPU, 1024.00 MB RAM, 25 GB NVMe存储
- 项目路径：~/google-trends-scaper

### 服务器快速更新

服务器已配置 `scheduler.py` 常驻进程运行定时任务，推荐使用仓库自带脚本 `update_server.sh` 完成热更新：

```bash
# 本地执行
./update_server.sh
```

脚本操作流程：
1. SSH 到服务器并切换到项目目录
2. `git pull` 拉取最新代码
3. 重启 `scheduler.py`（如果已在运行则先 kill 后重启）
4. 打印调度器状态

整个过程无需手动输入指令，几秒即可完成部署。

## 故障排除

如果您遇到问题，请检查：

### 数据获取问题

- **429 错误**：如果遇到 "Google returned a response with code 429" 错误，这表示请求过多。脚本已包含重试机制，但如果仍然失败，请等待几小时后再试。
- **中文字体问题**：如果图表中的中文显示不正确，请确保系统安装了支持中文的字体（如 Arial Unicode MS、SimHei 等）。
- **目录权限**：确保脚本目录下的 `screenshots` 目录有写入权限。

### 飞书发送问题

- **凭证配置**：确保 `feishu_sender.py` 中的 APP_ID 和 APP_SECRET 正确配置。
- **Webhook 地址**：确认 FEISHU_WEBHOOK_URL 是有效的并且没有过期。
- **图片上传失败**：检查 `feishu_sender.py` 中的代码是否能正确匹配带时间戳的图片文件名。

### 日志分析

- 查看 `logs` 目录中的日志文件以获取详细错误信息。
- 如果使用 cron 任务，请检查 cron 日志以确认脚本是否按计划执行。

### 网络问题

- 确保计算机可以访问 Google Trends 和飞书 API。
- 如果使用代理，请确认代理配置正确。

## 维护

### 更新热词

如果需要更新监控的热词，请同时修改以下两个文件中的 `TREND_GROUPS` 列表：

1. `trends_api.py` - 包含关键词和描述，用于获取数据和生成图表
2. `feishu_sender.py` - 包含关键词、描述和 URL，用于发送到飞书

注意：两个文件中的 `name` 字段必须保持一致，以确保正确匹配图片文件。

### 服务器部署

项目已优化为更适合服务器部署：

1. **目录结构**：所有文件都使用相对路径，图片和日志存储在项目目录下
2. **虚拟环境**：使用Python虚拟环境管理依赖
3. **自动创建目录**：脚本会自动创建所需的目录结构

部署步骤：

1. 将代码克隆到服务器：`git clone https://github.com/will3213/google-trends-scaper.git`
2. 创建虚拟环境并安装依赖：
   ```bash
   cd google-trends-scaper
   python3 -m venv venv
   source venv/bin/activate
   pip install pytrends pandas matplotlib seaborn requests requests_toolbelt
   ```
3. 配置飞书凭证和Webhook
4. 设置crontab定时任务

### 其他维护任务

- **更新凭证**：直接修改 `feishu_sender.py` 中的 APP_ID、APP_SECRET 和 FEISHU_WEBHOOK_URL
- **依赖更新**：定期运行 `source venv/bin/activate && pip install --upgrade pytrends pandas matplotlib seaborn requests requests_toolbelt`
- **日志清理**：定期清理 `logs` 目录中的旧日志和备份图片，以节省磁盘空间
