# Google Trends Scraper

一个自动化工具，用于抓取 Google Trends 热词趋势数据并发送到飞书群组。

## 项目概述

该项目是一个自动化系统，用于每日收集 Google Trends 上特定关键词的搜索趋势数据，并将这些数据以图片形式发送到飞书群组，便于团队跟踪和分析 AI 相关热词的搜索趋势变化。

### 核心功能

1. **自动截图**：使用 Playwright 访问 Google Trends 页面并截取指定关键词的趋势图表
2. **飞书集成**：将截图上传到飞书并通过飞书机器人发送到指定群组
3. **定时执行**：支持通过 cron 任务定时执行，实现每日自动汇报

## 项目结构

- `take_screenshots.py` - 负责访问 Google Trends 链接并截取页面首屏
- `feishu_sender.py` - 负责将截图上传到飞书，组装消息内容，并通过飞书机器人 Webhook 发送到指定群组
- `feishu_uploader.py` - 提供飞书图片上传功能的独立模块
- `config_guide.md` - 详细的配置指南
- `deployment_and_maintenance_guide.md` - 部署和维护指南

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

### 手动运行

1. 运行截图脚本
   ```bash
   python3 take_screenshots.py
   ```

2. 运行飞书发送脚本
   ```bash
   python3 feishu_sender.py
   ```

### 设置定时任务

使用 crontab 设置定时任务，例如：

```bash
# 每日早上9:00执行截图脚本
0 9 * * * /usr/bin/python3 /path/to/take_screenshots.py >> /path/to/cron_screenshot.log 2>&1

# 每日早上9:01执行飞书消息发送脚本
1 9 * * * /usr/bin/python3 /path/to/feishu_sender.py >> /path/to/cron_feishu_sender.log 2>&1
```

详细部署和维护说明请参考 `deployment_and_maintenance_guide.md`。

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

- 截图目录是否存在且权限正确
- 飞书应用凭证是否正确配置
- 飞书 Webhook 地址是否有效
- 网络连接是否正常
- 日志文件中的详细错误信息

## 维护

- **更新热词**：同时修改两个脚本中的 `TREND_GROUPS` 列表
- **更新凭证**：直接修改 `feishu_sender.py` 中的配置变量
- **依赖更新**：定期运行 `pip3 install --upgrade playwright requests requests_toolbelt`
