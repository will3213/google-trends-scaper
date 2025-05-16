# Google Trends Scraper

一个自动化工具，用于抓取 Google Trends 热词趋势数据并发送到飞书群组。

## 项目概述

该项目是一个自动化系统，用于每日收集 Google Trends 上特定关键词的搜索趋势数据，并将这些数据以图片形式发送到飞书群组，便于团队跟踪和分析 AI 相关热词的搜索趋势变化。

### 核心功能

1. **数据获取**：使用 pytrends API 获取 Google Trends 数据并生成趋势图表
2. **网页截图**：使用 Playwright 访问 Google Trends 页面并截取指定关键词的趋势图表（备选方案）
3. **飞书集成**：将图表上传到飞书并通过飞书机器人发送到指定群组
4. **自动化工作流**：提供完整的工作流脚本，确保数据获取和发送的顺序执行
5. **定时执行**：支持通过 cron 任务定时执行，实现每日自动汇报

## 项目结构

### 核心脚本

- `trends_api.py` - **主要脚本**，使用 pytrends API 获取 Google Trends 数据并生成趋势图表
- `feishu_sender.py` - 负责将图表上传到飞书，组装消息内容，并通过飞书机器人 Webhook 发送到指定群组
- `run_trends_workflow.sh` - 协调脚本，按顺序执行数据获取和飞书发送，并记录日志

### 辅助脚本

- `take_screenshots.py` - 备选方案，使用 Playwright 访问 Google Trends 页面并截取趋势图表
- `trends_api_single.py` - 用于处理单个关键词组的辅助脚本，用于解决特定问题

## 系统需求

- **操作系统**: Linux (推荐 Ubuntu 20.04 LTS 或更高版本)
- **Python**: 版本 3.7 或更高版本 (脚本使用 Python 3.11 开发和测试)
- **依赖库**: 
  - playwright
  - requests
  - requests_toolbelt

## 安装步骤

1. 克隆或下载此仓库到您的服务器

2. 安装 Python 依赖
   ```bash
   pip3 install playwright requests requests_toolbelt
   ```

3. 安装 Playwright 浏览器依赖
   ```bash
   playwright install-deps
   playwright install
   ```

4. 创建截图保存目录
   ```bash
   mkdir -p /home/ubuntu/google_trends_screenshots
   # 或修改脚本中的 SCREENSHOT_DIR 变量为您希望的路径
   ```

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

3. **热词分组**：根据需要修改 `TREND_GROUPS` 列表（注意：需要同时修改 `take_screenshots.py` 和 `feishu_sender.py` 两个文件中的定义）

详细配置说明请参考 `config_guide.md`。

## 使用方法

### 推荐方式：使用工作流脚本

使用工作流脚本可以确保数据获取和飞书发送按正确顺序执行：

```bash
# 运行完整工作流（数据获取 + 飞书发送）
./run_trends_workflow.sh
```

工作流脚本会：
1. 首先执行 `trends_api.py` 获取数据并生成图表
2. 检查数据获取是否成功
3. 如果成功，再执行 `feishu_sender.py` 发送到飞书
4. 记录日志到 `logs` 目录

### 分步手动运行

如果您想分步手动运行，可以按以下顺序执行：

1. 运行数据获取脚本（使用 pytrends API）
   ```bash
   python3 trends_api.py
   ```

2. 运行飞书发送脚本
   ```bash
   python3 feishu_sender.py
   ```

3. （备选）如果 API 方法失效，可以使用截图方式
   ```bash
   python3 take_screenshots.py
   ```

### 设置定时任务

使用 crontab 设置定时任务，例如：

```bash
# 每日早上9:00执行完整工作流
0 9 * * * /path/to/google-trends-scraper/run_trends_workflow.sh >> /path/to/cron_workflow.log 2>&1
```

## 日志查看

工作流脚本会在 `logs` 目录下生成日志文件：

- `trends_YYYY-MM-DD_HH-MM-SS.log` - 数据获取脚本的日志
- `feishu_YYYY-MM-DD_HH-MM-SS.log` - 飞书发送脚本的日志

这样您可以轻松查看每次执行的详细情况，特别是当自动化运行时出现问题。

## 当前监控的热词

当前系统监控以下 AI 相关热词的搜索趋势：

- chatgpt
- 聊天模型：Claude/deepseek/gemini/grok
- AI 视频模型：Kling AI/Pika AI/Hailuo AI/Runway AI
- 功能词：ai translate/ai write/chatpdf
- 通用术语：ai video/ai image/animation
- gpt 4o
- AI agent 相关词：Manus/devin/genspark/lovable
- 新兴 AI 工具：lovart/flowith/fellou/deepwiki

## 故障排除

如果您遇到问题，请检查：

### 数据获取问题

- **429 错误**：如果遇到 "Google returned a response with code 429" 错误，这表示请求过多。脚本已包含重试机制，但如果仍然失败，请等待几小时后再试或使用 `take_screenshots.py` 作为备选方案。
- **中文字体问题**：如果图表中的中文显示不正确，请确保系统安装了支持中文的字体（如 Arial Unicode MS、SimHei 等）。
- **目录权限**：确保 `google_trends_screenshots` 目录存在且有写入权限。

### 飞书发送问题

- **凭证配置**：确保 `feishu_sender.py` 中的 APP_ID 和 APP_SECRET 正确配置。
- **Webhook 地址**：确认 FEISHU_WEBHOOK_URL 是有效的并且没有过期。
- **图片上传失败**：检查图片文件名是否与 `TREND_GROUPS` 中的 `name` 字段一致。

### 日志分析

- 查看 `logs` 目录中的日志文件以获取详细错误信息。
- 如果使用 cron 任务，请检查 cron 日志以确认脚本是否按计划执行。

### 网络问题

- 确保服务器可以访问 Google Trends 和飞书 API。
- 如果使用代理，请确认代理配置正确。

## 维护

- **更新热词**：同时修改 `trends_api.py` 和 `take_screenshots.py` 中的 `TREND_GROUPS` 列表
- **更新凭证**：直接修改 `feishu_sender.py` 中的配置变量
- **依赖更新**：定期运行 `pip3 install --upgrade pytrends pandas matplotlib seaborn requests requests_toolbelt playwright`
