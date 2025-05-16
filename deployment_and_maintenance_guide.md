# Google Trends热词趋势汇报部署与维护指南

本文档旨在帮助您部署和维护每日自动发送Google Trends热词趋势到飞书群组的自动化脚本。

## 1. 系统需求与环境准备

在部署脚本之前，请确保您的服务器环境满足以下要求：

*   **操作系统**: Linux (推荐 Ubuntu 20.04 LTS 或更高版本)
*   **Python**: 版本 3.7 或更高版本 (脚本使用 Python 3.11 开发和测试)
*   **pip**: Python 包安装器
*   **Playwright 及其浏览器依赖**: 用于网页截图
*   **网络连接**: 能够访问 Google Trends 和飞书开放平台 API

### 1.1 安装 Python 和 pip

如果您的系统中没有安装 Python 和 pip，请根据您的 Linux 发行版进行安装。例如，在 Ubuntu 上：

```bash
sudo apt update
sudo apt install python3 python3-pip -y
```

### 1.2 安装 Playwright 浏览器依赖

Playwright 需要特定的浏览器依赖库才能正常运行。您可以通过以下命令自动安装这些依赖：

```bash
sudo playwright install-deps
```

如果您在运行 `playwright install-deps` 时遇到问题，或者该命令不可用，您可能需要先通过 pip 安装 Playwright（见下一节），然后再运行此命令。

## 2. 脚本部署与依赖安装

1.  **上传脚本**：将 `take_screenshots.py` 和 `feishu_sender.py` 两个脚本文件上传到您服务器的同一目录下，例如 `/opt/google-trends-feishu-bot/`。

2.  **创建截图目录**：根据您在脚本中配置的 `SCREENSHOT_DIR` (默认为 `/home/ubuntu/google_trends_screenshots`，建议修改为部署目录下的子目录，如 `/opt/google-trends-feishu-bot/screenshots/`)，创建该目录并确保运行脚本的用户有读写权限。

    ```bash
    # 假设部署在 /opt/google-trends-feishu-bot/
    sudo mkdir -p /opt/google-trends-feishu-bot/screenshots
    sudo chown your_user:your_group /opt/google-trends-feishu-bot/screenshots # 将 your_user:your_group 替换为实际运行脚本的用户和组
    ```
    并相应修改脚本中的 `SCREENSHOT_DIR` 变量。

3.  **安装 Python 依赖库**：
    进入脚本所在目录，使用 pip 安装所需的 Python 库。

    ```bash
    cd /opt/google-trends-feishu-bot/ # 或者您选择的部署目录
    pip3 install playwright requests requests_toolbelt
    ```

4.  **安装 Playwright 浏览器内核**：
    首次运行或更新 Playwright 后，需要下载浏览器内核文件。

    ```bash
    playwright install
    ```
    此命令会下载 Chromium, Firefox 和 WebKit 的浏览器内核。

## 3. 配置脚本

请参照《自动化Google Trends热词趋势汇报配置指南》（`config_guide.md`）完成对 `feishu_sender.py` 脚本中的 `APP_ID`, `APP_SECRET`, `FEISHU_WEBHOOK_URL` 以及两个脚本中 `TREND_GROUPS` 的配置。

## 4. 手动测试运行

在设置定时任务之前，强烈建议手动运行脚本以确保一切配置正确。

1.  **运行截图脚本**：

    ```bash
    python3 /opt/google-trends-feishu-bot/take_screenshots.py
    ```
    检查截图是否已成功保存在您配置的 `SCREENSHOT_DIR` 目录中，并且每个分组都有一张图片。

2.  **运行飞书发送脚本** (确保已正确配置 `APP_ID` 和 `APP_SECRET`)：

    ```bash
    python3 /opt/google-trends-feishu-bot/feishu_sender.py
    ```
    检查您的飞书群组是否收到了包含说明文字和对应图片的消息。注意，如果 `APP_ID` 和 `APP_SECRET` 未配置或配置错误，图片可能无法正常上传和显示，但脚本仍会尝试发送文本内容（或模拟图片key）。

## 5. 设置定时任务 (Cron Job)

为了实现每日自动发送，您可以使用 cron（Linux 系统中的定时任务调度器）。

1.  **编辑 crontab**：
    打开当前用户的 crontab 编辑器：

    ```bash
    crontab -e
    ```
    如果是首次使用，系统可能会提示您选择一个文本编辑器。

2.  **添加定时任务条目**：
    在 crontab 文件中添加以下两行，以设置每日早上9点执行脚本。请确保将 `/opt/google-trends-feishu-bot/` 替换为您的实际脚本路径，并将 `python3` 替换为您的 Python 3解释器的完整路径（可以通过 `which python3` 命令查找）。

    ```cron
    # 每日早上9:00执行Google Trends截图脚本，并将日志输出到指定文件
    0 9 * * * /usr/bin/python3 /opt/google-trends-feishu-bot/take_screenshots.py >> /opt/google-trends-feishu-bot/cron_screenshot.log 2>&1

    # 每日早上9:01执行飞书消息发送脚本 (在截图完成后执行)，并将日志输出到指定文件
    1 9 * * * /usr/bin/python3 /opt/google-trends-feishu-bot/feishu_sender.py >> /opt/google-trends-feishu-bot/cron_feishu_sender.log 2>&1
    ```

    **解释**：
    *   `0 9 * * *`: 表示每天的9点0分执行。
    *   `1 9 * * *`: 表示每天的9点1分执行 (给截图脚本留出1分钟执行时间)。您可以根据实际截图所需时间调整。
    *   `/usr/bin/python3`: Python 3 解释器的绝对路径。**强烈建议使用绝对路径**。
    *   `/opt/google-trends-feishu-bot/take_screenshots.py`: 截图脚本的绝对路径。
    *   `/opt/google-trends-feishu-bot/feishu_sender.py`: 发送脚本的绝对路径。
    *   `>> /opt/google-trends-feishu-bot/cron_screenshot.log 2>&1`: 将标准输出和标准错误都追加到指定的日志文件中。建议为每个脚本使用不同的日志文件。

3.  **保存并退出 crontab**。

4.  **验证 crontab 设置** (可选)：
    您可以使用以下命令查看已设置的 cron 任务：

    ```bash
    crontab -l
    ```

## 6. 日志与异常处理

*   **脚本日志**：两个脚本在执行过程中会在控制台打印日志信息。当通过 cron 运行时，这些日志会重定向到您在 crontab 条目中指定的日志文件（例如 `cron_screenshot.log` 和 `cron_feishu_sender.log`）。定期检查这些日志文件可以帮助您监控脚本的运行状态和排查问题。
*   **异常捕获**：脚本内部已包含基本的异常捕获机制。如果发生错误（例如网络问题、API调用失败、文件未找到等），脚本会尝试打印错误信息到日志中。

## 7. 维护与更新

*   **更新热词分组**：如需修改热词分组、描述或链接，请参照 `config_guide.md` 中的说明，**同时修改 `take_screenshots.py` 和 `feishu_sender.py` 两个文件中的 `TREND_GROUPS` 列表**。
*   **更新飞书凭证或Webhook**：如果您的飞书应用凭证 (`APP_ID`, `APP_SECRET`) 或机器人Webhook地址发生变更，请直接修改 `feishu_sender.py` 脚本顶部的配置部分。
*   **更新依赖库**：定期更新 Python 依赖库可能有助于获取新功能或安全修复。但请注意，更新后最好进行一次手动测试，以确保兼容性。
    ```bash
    pip3 install --upgrade playwright requests requests_toolbelt
    ```
*   **Playwright 浏览器更新**：Playwright 自身更新后，可能需要重新运行 `playwright install` 来获取匹配的浏览器内核。

## 8. 常见问题与故障排除

*   **截图失败**：
    *   检查 `playwright install-deps` 和 `playwright install` 是否已成功执行。
    *   检查 Google Trends 网站结构是否有变动，或是否有新的人机验证机制。
    *   查看 `cron_screenshot.log` 获取详细错误信息。
*   **图片上传飞书失败**：
    *   检查 `APP_ID` 和 `APP_SECRET` 是否正确，以及对应飞书应用是否具有上传图片的权限。
    *   检查服务器网络是否能正常访问飞书API (`open.feishu.cn`)。
    *   查看 `cron_feishu_sender.log` 获取详细错误信息。
*   **消息未发送到飞书群组**：
    *   检查 `FEISHU_WEBHOOK_URL` 是否正确。
    *   检查飞书机器人是否仍在群组中且未被禁用。
    *   查看 `cron_feishu_sender.log` 获取详细错误信息。
*   **Cron 任务未执行**：
    *   检查 crontab 条目语法是否正确。
    *   检查 cron 服务是否正在运行 (`sudo systemctl status cron`)。
    *   检查脚本和 Python 解释器的路径是否为绝对路径且正确无误。
    *   检查运行 cron 任务的用户是否具有执行脚本和读写相关目录的权限。

通过以上步骤，您应该能够成功部署并维护这套自动化汇报系统。

