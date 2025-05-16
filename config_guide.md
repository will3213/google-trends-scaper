# 自动化Google Trends热词趋势汇报配置指南

本文档将指导您如何配置每日自动发送Google Trends热词趋势到飞书群组的脚本。

## 1. 概述

本自动化方案包含两个核心Python脚本：

1.  `take_screenshots.py`: 负责访问Google Trends链接并截取页面首屏。
2.  `feishu_sender.py`: 负责将截图上传到飞书，组装消息内容，并通过飞书机器人Webhook发送到指定群组。

为了使脚本正常工作，您需要进行以下配置。

## 2. 脚本配置 (`feishu_sender.py`)

打开 `feishu_sender.py` 文件，您会看到顶部的配置区域。请根据您的实际情况修改以下变量：

### 2.1 飞书应用凭证

这些凭证用于获取 `tenant_access_token`，从而允许脚本上传图片到飞书服务器。

```python
APP_ID = "YOUR_APP_ID"  # 将 "YOUR_APP_ID" 替换为您的飞书应用ID
APP_SECRET = "YOUR_APP_SECRET"  # 将 "YOUR_APP_SECRET" 替换为您的飞书应用密钥
```

-   **如何获取 `APP_ID` 和 `APP_SECRET`**：
    1.  登录 [飞书开放平台](https://open.feishu.cn/)。
    2.  进入“开发者后台”。
    3.  选择或创建一个“自建应用”。
    4.  在应用的“凭证与基础信息”页面，您可以找到 `App ID` 和 `App Secret`。
    5.  确保您的应用已启用“机器人”能力，并已获取“上传图片” (`im:image`) 和 “获取与发送单聊、群聊消息” (`im:message`) 等相关权限。

### 2.2 飞书机器人Webhook地址

此Webhook地址用于将最终组装好的消息发送到指定的飞书群组。

```python
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_KEY" # 将 YOUR_WEBHOOK_KEY 替换为您的实际Webhook Key
```

-   **如何获取Webhook地址**：
    1.  在您希望接收消息的飞书群组中，打开群设置。
    2.  选择“群机器人”。
    3.  点击“添加机器人”，然后选择“自定义机器人”。
    4.  给机器人命名，阅读并同意相关协议后，点击“添加”。
    5.  复制生成的Webhook地址，并将其粘贴到脚本的 `FEISHU_WEBHOOK_URL`变量中。

### 2.3 截图保存目录

此目录用于存放 `take_screenshots.py` 脚本生成的截图文件。

```python
SCREENSHOT_DIR = "/home/ubuntu/google_trends_screenshots"
```

-   默认路径为 `/home/ubuntu/google_trends_screenshots`。如果您在 `take_screenshots.py` 中修改了此路径，请确保在 `feishu_sender.py` 中也进行相应修改，以保证脚本能找到截图文件。
-   确保运行脚本的用户对该目录有读写权限。

## 3. 热词分组与链接配置

热词的分组名称、描述文字以及对应的Google Trends链接在 `take_screenshots.py` 和 `feishu_sender.py` 两个脚本中都有定义（变量名为 `TREND_GROUPS`）。

```python
# 示例 (位于 take_screenshots.py 和 feishu_sender.py 中)
TREND_GROUPS = [
    {"name": "chatgpt", "description": "chatgpt", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=chatgpt&hl=zh-CN"},
    {"name": "chat_models_Claude_deepseek_gemini_grok", "description": "chat模型词：Claude/deepseek/gemini/grok", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=Claude,deepseek,gemini,grok&hl=zh-CN"},
    # ...更多分组
]
```

-   **`name`**: 用于生成截图文件名，建议使用英文和下划线，避免特殊字符。
-   **`description`**: 将作为消息中该组图片的说明文字显示。
-   **`url`**: 对应的Google Trends链接。

**重要提示**：如果您需要修改、添加或删除热词分组，**必须同时修改 `take_screenshots.py` 和 `feishu_sender.py` 两个文件中的 `TREND_GROUPS` 列表**，并确保两者的内容和顺序完全一致，否则可能导致截图与说明文字不匹配或处理错误。

## 4. 总结

完成以上配置后，您的脚本应该可以正常运行。请参考《部署与维护指南》进行脚本的部署和定时执行设置。

如果您在配置过程中遇到任何问题，请检查：

-   `APP_ID` 和 `APP_SECRET` 是否正确且应用权限充足。
-   `FEISHU_WEBHOOK_URL` 是否为有效的机器人Webhook地址。
-   截图目录是否存在且权限正确。
-   两个脚本中的 `TREND_GROUPS` 定义是否一致。

