import requests
import json
import os
from requests_toolbelt import MultipartEncoder
import datetime
import urllib.parse
import re

# --- Configuration (User will need to fill these) ---
APP_ID = "cli_a8ac64648375100d"  # Replace with your Feishu App ID
APP_SECRET = "1bE7tpruwApUkB9cViiyiecrNNjotNQ5"  # Replace with your Feishu App Secret
FEISHU_WEBHOOK_URL = "https://open.feishu.cn/open-apis/bot/v2/hook/7fae3ce0-7b6b-4822-ae29-58d84b8cb296" # Provided by user
# 使用脚本所在目录下的screenshots文件夹
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_DIR = os.path.join(SCRIPT_DIR, "screenshots")

# From take_screenshots.py, ensure this matches
TREND_GROUPS = [
        {"name": "chatgpt", "description": "ChatGPT 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=chatgpt&hl=zh-CN"},
    {"name": "gpt4o", "description": "GPT4o 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=gpt4o&hl=zh-CN"},
    {"name": "chat_models", "description": "Claude,Deepseek,Gemini,Grok,Qwen 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=claude,deepseek,gemini,grok,qwen&hl=zh-CN"},
    {"name": "ai_video_models", "description": "Kling AI,Pika AI,Hailuo AI,Veo AI,Pixverse 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=kling%20ai,pika%20ai,hailuo%20ai,veo%20ai,pixverse&hl=zh-CN"},
    {"name": "ai_features", "description": "AI Translate,AI Write,ChatPDF,AI Content Detector,PDF Translator 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=ai%20translate,ai%20write,chatpdf,ai%20content%20detector,pdf%20translator&hl=zh-CN"},
    {"name": "ai_creative", "description": "AI Video,AI Image,Animation 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=ai%20video,ai%20image,animation&hl=zh-CN"},
    {"name": "ai_tools", "description": "Lovart,Flowith,Fellou,Deepwiki,Devin AI 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=lovart,flowith,fellou,deepwiki,devin%20ai&hl=zh-CN"},
    {"name": "ai_image_models", "description": "Sora,Midjourney,Runway,Freepik 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=sora,midjourney,runway,freepik&hl=zh-CN"},
    {"name": "platform_tools", "description": "Civitai,Flux AI,Liblib,Pollo AI 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=civitai,flux%20ai,liblib,pollo%20ai&hl=zh-CN"},
    {"name": "slide_tools", "description": "Slidesgo,Base44 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=slidesgo,base44&hl=zh-CN"},
    {"name": "ai_agents2", "description": "Trae AI,Skywork,Minimax Agent 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=trae%20ai,skywork,minimax%20agent&hl=zh-CN"},
    {"name": "browser_tools", "description": "Dia Browser,Arc Browser,Dify AI,Coze 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=dia%20browser,arc%20browser,dify%20ai,coze&hl=zh-CN"},
    {"name": "ai_platforms", "description": "Poe AI,Perplexity,NotebookLM,Notion,Gamma 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=poe%20ai,perplexity,notebooklm,notion,gamma&hl=zh-CN"},
    {"name": "ai_agents", "description": "Manus,Genspark,Lovable,Cursor,N8N 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=manus,genspark,lovable,cursor,n8n&hl=zh-CN"},
    {"name": "dev_tools", "description": "Windsurf,Codex,Kiro,Zapier,Claude Code 热度趋势", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=windsurf,codex,kiro,zapier,claude%20code&hl=zh-CN"}
]


def get_tenant_access_token(app_id, app_secret):
    """Fetches tenant_access_token from Feishu API."""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret})
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 0:
            print("Successfully obtained tenant_access_token.")
            return data.get("tenant_access_token")
        else:
            print(f"Error getting tenant_access_token: {data.get('msg')}, code: {data.get('code')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed while getting tenant_access_token: {e}")
        return None

def upload_image_to_feishu(image_path, tenant_access_token):
    """Uploads an image to Feishu and returns its image_key."""
    if not tenant_access_token:
        print("Cannot upload image: tenant_access_token is missing.")
        return None
    
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    
    # 根据文件扩展名确定正确的MIME类型
    file_ext = os.path.splitext(image_path)[1].lower()
    mime_type = 'image/jpeg'  # 默认MIME类型
    if file_ext in ['.png']:
        mime_type = 'image/png'
    elif file_ext in ['.gif']:
        mime_type = 'image/gif'
    elif file_ext in ['.webp']:
        mime_type = 'image/webp'
    elif file_ext in ['.bmp']:
        mime_type = 'image/bmp'
    
    # 打印上传信息用于调试
    print(f"Uploading {os.path.basename(image_path)}...")
    
    try:
        # 确保文件存在且可读
        if not os.path.exists(image_path):
            print(f"Error: File {image_path} does not exist")
            return None
            
        # 准备表单数据
        form = {
            'image_type': 'message',
            'image': (os.path.basename(image_path), open(image_path, 'rb'), mime_type)
        }
        multi_form = MultipartEncoder(form)
        
        # 设置请求头
        headers = {
            'Authorization': f'Bearer {tenant_access_token}'
        }
        headers['Content-Type'] = multi_form.content_type
        
        # 发送请求
        response = requests.post(url, headers=headers, data=multi_form, timeout=30)
        
        # 打印响应的 X-Tt-Logid 用于调试
        if 'X-Tt-Logid' in response.headers:
            print(f"X-Tt-Logid: {response.headers['X-Tt-Logid']}")
            
        # 解析响应
        data = response.json()
        if data.get("code") == 0 and data.get("data", {}).get("image_key"):
            image_key = data["data"]["image_key"]
            print(f"Successfully uploaded {os.path.basename(image_path)}, image_key: {image_key}")
            return image_key
        else:
            print(f"Error uploading image {os.path.basename(image_path)}: {data.get('msg')}, code: {data.get('code')}")
            print(f"Response content: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed while uploading image {os.path.basename(image_path)}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response for {os.path.basename(image_path)}: {e}")
        print(f"Response content: {response.text if hasattr(response, 'text') else 'No response text available'}")
        return None
    except Exception as e:
        print(f"Unexpected error uploading {os.path.basename(image_path)}: {e}")
        return None

def prepare_feishu_message_content(trend_groups_with_keys):
    """Prepares the Feishu card message content."""
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    title = f"{today_date} Google trends 广告热词趋势查询"
    
    # 创建卡片消息
    elements = []
    
    # 添加标题
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**{title}**"
        }
    })
    
    # 添加分割线
    elements.append({
        "tag": "hr"
    })
    
    # 添加每个趋势组的信息
    for group_info in trend_groups_with_keys:
        cleaned_description = group_info['description'].replace('\\', '/')
        
        # 添加趋势组标题
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📊 {cleaned_description}**"
            }
        })
        
        # 添加图片或失败提示
        if group_info.get('image_key'):
            elements.append({
                "tag": "img",
                "img_key": group_info['image_key'],
                "alt": {
                    "tag": "plain_text",
                    "content": cleaned_description
                }
            })
            
        # 添加快捷链接（近7日/30日/90日）


        else:
            elements.append({
                "tag": "div",
                "text": {
                    "tag": "plain_text",
                    "content": "(图片上传失败)"
                }
            })
        
        # 添加快捷链接（近7日/30日/90日）
        original_url = group_info.get('url')
        if original_url:
            def _build_alt(u, date_param):
                if 'date=' in u:
                    return re.sub(r'date=[^&]+', f'date={date_param}', u)
                else:
                    sep = '&' if '?' in u else '?'
                    return f"{u}{sep}date={date_param}"
            url_7  = _build_alt(original_url, 'now%207-d')
            url_30 = _build_alt(original_url, 'today%201-m')
            url_90 = _build_alt(original_url, 'today%203-m')
            elements.append({
                "tag": "note",
                "elements": [{
                    "tag": "lark_md",
                    "content": f"[近7日]({url_7}) / [近30日]({url_30}) / [近90日]({url_90})"
                }]
            })
        
        # 添加分割线
        elements.append({
            "tag": "hr"
        })
    
    # 构建卡片消息结构
    message_body = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": "blue"
            },
            "elements": elements
        }
    }
    return message_body

def send_message_to_feishu_webhook(webhook_url, message_body):
    """Sends the prepared message to the Feishu Webhook URL."""
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(webhook_url, headers=headers, data=json.dumps(message_body), timeout=15)
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("StatusCode") == 0 or response_data.get("code") == 0 or response_data.get("ok") == True or response_data.get("StatusMessage") == "success": # Common success indicators
            print(f"Successfully sent message to Feishu webhook: {webhook_url}")
            print(f"Feishu response: {response_data}")
            return True
        else:
            print(f"Error sending message to Feishu webhook {webhook_url}: {response_data}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed while sending message to Feishu webhook {webhook_url}: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response from Feishu webhook {webhook_url}: {e}")
        print(f"Response content: {response.content.decode('utf-8', errors='ignore')}")
        return False

def main():
    print("Starting Feishu uploader and sender script...")
    
    # Check if screenshots exist first
    screenshots_exist = False
    for group in TREND_GROUPS:
        filename_base = re.sub(r'[\\/:*?"<>|]', '_', group["name"])
        # 查找匹配的文件（支持带时间戳的文件名）
        matching_files = [f for f in os.listdir(SCREENSHOT_DIR) if f == f"{filename_base}.png"]
        if matching_files:
            screenshots_exist = True
            break
    
    if not screenshots_exist:
        print(f"No screenshots found in {SCREENSHOT_DIR}. Will send card without images.")
        trend_groups_for_message = []
        for group in TREND_GROUPS:
            trend_groups_for_message.append({
                "description": group["description"],
                "image_key": None,
                "url": group["url"]
            })
        message_body = prepare_feishu_message_content(trend_groups_for_message)
        if FEISHU_WEBHOOK_URL:
            print("Sending placeholder card without images to Feishu...")
            send_message_to_feishu_webhook(FEISHU_WEBHOOK_URL, message_body)
        else:
            print("FEISHU_WEBHOOK_URL is not configured. Cannot send message.")
        print("Feishu script finished (sent card without screenshots).")
        return

    trend_groups_for_message = []

    if APP_ID == "" or APP_SECRET == "" or APP_ID == "YOUR_APP_ID" or APP_SECRET == "YOUR_APP_SECRET":
        print("APP_ID and APP_SECRET are not configured. Images will not be uploaded.")
        print("Message will be sent with placeholders or 'upload failed' messages for images.")
        for i, group in enumerate(TREND_GROUPS):
            filename_base = re.sub(r'[\\/:*?"<>|]', '_', group["name"])
            # 查找匹配的文件（支持带时间戳的文件名）
            matching_files = [f for f in os.listdir(SCREENSHOT_DIR) if f == f"{filename_base}.png"]
            if matching_files:
                screenshot_path = os.path.join(SCREENSHOT_DIR, matching_files[0])  # 使用找到的第一个匹配文件
                trend_groups_for_message.append({
                    "description": group["description"],
                    "image_key": f"mock_image_key_for_{filename_base}", # Placeholder
                    "url": group["url"]
                })
            else:
                print(f"Screenshot not found for group {group['name']} in {SCREENSHOT_DIR}")
                trend_groups_for_message.append({
                    "description": group["description"],
                    "image_key": None, # Actual upload would fail
                    "url": group["url"]
                })
    else:
        print(f"Attempting to get tenant_access_token with APP_ID: {APP_ID[:5]}...")
        token = get_tenant_access_token(APP_ID, APP_SECRET)
        if token:
            print(f"Tenant access token obtained: {token[:10]}...")
            for group in TREND_GROUPS:
                filename_base = re.sub(r'[\\/:*?"<>|]', '_', group["name"])
                # 查找匹配的文件（支持带时间戳的文件名）
                matching_files = [f for f in os.listdir(SCREENSHOT_DIR) if f == f"{filename_base}.png"]
                
                image_key_to_use = None
                if matching_files:
                    image_file = matching_files[0]  # 使用找到的第一个匹配文件
                    image_path = os.path.join(SCREENSHOT_DIR, image_file)
                    print(f"Uploading {image_file}...")
                    image_key_to_use = upload_image_to_feishu(image_path, token)
                else:
                    print(f"Screenshot not found for group {group['name']} in {SCREENSHOT_DIR}")
                
                trend_groups_for_message.append({
                    "description": group["description"],
                    "image_key": image_key_to_use,
                    "url": group["url"]
                })
        else:
            print("Failed to obtain tenant_access_token. Images will not be uploaded.")
            print("Message will be sent with placeholders or 'upload failed' messages for images.")
            for i, group in enumerate(TREND_GROUPS):
                filename_base = re.sub(r'[\\/:*?"<>|]', '_', group["name"])
                # 查找匹配的文件（支持带时间戳的文件名）
                matching_files = [f for f in os.listdir(SCREENSHOT_DIR) if f == f"{filename_base}.png"]
                if matching_files:
                    trend_groups_for_message.append({
                        "description": group["description"],
                        "image_key": f"mock_image_key_for_{filename_base}_no_token", # Placeholder
                        "url": group["url"]
                    })
                else:
                    print(f"Screenshot not found for group {group['name']} at {screenshot_path}")
                    trend_groups_for_message.append({
                        "description": group["description"],
                        "image_key": None,
                        "url": group["url"]
                    })

    if trend_groups_for_message:
        feishu_message = prepare_feishu_message_content(trend_groups_for_message)
        print("\nPrepared Feishu Message:")
        print(json.dumps(feishu_message, indent=2, ensure_ascii=False))
        
        if FEISHU_WEBHOOK_URL:
            print(f"\nSending message to Feishu webhook: {FEISHU_WEBHOOK_URL}")
            send_message_to_feishu_webhook(FEISHU_WEBHOOK_URL, feishu_message)
        else:
            print("FEISHU_WEBHOOK_URL is not configured. Cannot send message.")
    else:
        print("No trend groups processed or screenshots found. No message will be sent.")

    print("Feishu uploader and sender script finished.")

if __name__ == "__main__":
    main()

