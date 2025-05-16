import requests
import json
import os
from requests_toolbelt import MultipartEncoder

# --- Configuration (User will need to fill these) ---
APP_ID = "YOUR_APP_ID"  # Replace with your Feishu App ID
APP_SECRET = "YOUR_APP_SECRET"  # Replace with your Feishu App Secret
SCREENSHOT_DIR = "/home/ubuntu/google_trends_screenshots"

# From take_screenshots.py, ensure this matches
TREND_GROUPS = [
    {"name": "chatgpt", "description": "chatgpt", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=chatgpt&hl=zh-CN"},
    {"name": "chat_models_Claude_deepseek_gemini_grok", "description": "chat模型词：Claude/deepseek/gemini/grok", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=Claude,deepseek,gemini,grok&hl=zh-CN"},
    {"name": "ai_video_models_Kling_Pika_Hailuo_Runway", "description": "ai video 模型词：Kling AI/Pika AI/Hailuo AI/Runway AI", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=Kling%20AI,Pika%20AI,Hailuo%20AI,Runway%20AI&hl=zh-CN"},
    {"name": "function_terms_ai_translate_ai_write_chatpdf", "description": "功能词：ai translate/ai write/chatpdf", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=ai%20translate,ai%20write,chatpdf&hl=zh-CN"},
    {"name": "ai_video_ai_image_animation", "description": "ai video/ai image/animation", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=ai%20video,ai%20image,animation&hl=zh-CN"},
    {"name": "gpt_4o", "description": "gpt 4o", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=gpt%204o&hl=zh-CN"},
    {"name": "ai_agent_terms_Manus_devin_genspark_lovable", "description": "AI agent词：Manus\\devin\\genspark\\lovable", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=Manus,devin,genspark,lovable&hl=zh-CN"},
    {"name": "lovart_flowith_fellou_deepwiki", "description": "lovart\\flowith\\fellou\\deepwiki", "url": "https://trends.google.com/trends/explore?date=now%207-d&q=lovart,flowith,fellou,deepwiki&hl=zh-CN"}
]

def get_tenant_access_token(app_id, app_secret):
    """Fetches tenant_access_token from Feishu API."""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret})
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
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
    form = {'image_type': 'message',
            'image': (os.path.basename(image_path), open(image_path, 'rb'), 'image/png')}
    multi_form = MultipartEncoder(form)
    headers = {
        'Authorization': f'Bearer {tenant_access_token}',
        'Content-Type': multi_form.content_type
    }
    try:
        response = requests.post(url, headers=headers, data=multi_form, timeout=30)
        response.raise_for_status()
        data = response.json()
        if data.get("code") == 0 and data.get("data", {}).get("image_key"):
            image_key = data["data"]["image_key"]
            print(f"Successfully uploaded {image_path}, image_key: {image_key}")
            return image_key
        else:
            print(f"Error uploading image {image_path}: {data.get('msg')}, code: {data.get('code')}")
            print(f"Response content: {response.content}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed while uploading image {image_path}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON response for {image_path}: {e}")
        print(f"Response content: {response.content}")
        return None

def prepare_feishu_message_content(trend_groups_with_keys):
    """Prepares the Feishu rich text message content."""
    import datetime
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    title = f"{today_date} Google trends 热词趋势查询"
    
    content_list = []
    # First element is the main title
    content_list.append([{"tag": "text", "text": title}])
    content_list.append([{"tag": "text", "text": " "}]) # Add an empty line for spacing

    for group_info in trend_groups_with_keys:
        description_elements = []
        # Handle potential backslashes in description for Feishu
        cleaned_description = group_info['description'].replace('\\', '/') 
        description_elements.append({"tag": "text", "text": f"{cleaned_description}:"})
        content_list.append(description_elements)
        
        if group_info.get('image_key'):
            content_list.append([{"tag": "image", "image_key": group_info['image_key']}])
        else:
            content_list.append([{"tag": "text", "text": "(图片上传失败)"}])
        content_list.append([{"tag": "text", "text": " "}]) # Add an empty line for spacing after each group

    message_body = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": content_list
                }
            }
        }
    }
    return message_body


if __name__ == "__main__":
    print("Starting Feishu uploader script...")
    # This part is for testing and will require APP_ID and APP_SECRET
    # For now, it will just print a message if they are not set.
    if APP_ID == "YOUR_APP_ID" or APP_SECRET == "YOUR_APP_SECRET":
        print("APP_ID and APP_SECRET are not configured. Please set them to test image uploading.")
        print("Simulating message preparation without actual image upload.")
        
        trend_groups_with_mock_keys = []
        for i, group in enumerate(TREND_GROUPS):
            # Sanitize filename as done in take_screenshots.py
            import re
            filename_base = re.sub(r'[\\/:*?"<>|]', '_', group["name"])
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{filename_base}.png")
            if os.path.exists(screenshot_path):
                 trend_groups_with_mock_keys.append({
                    "description": group["description"],
                    "image_key": f"mock_image_key_{i+1}" # Using mock key for now
                })
            else:
                print(f"Screenshot not found for group {group['name']} at {screenshot_path}")
                trend_groups_with_mock_keys.append({
                    "description": group["description"],
                    "image_key": None # Simulate upload failure
                })

        if trend_groups_with_mock_keys:
            feishu_message = prepare_feishu_message_content(trend_groups_with_mock_keys)
            print("\nPrepared Feishu Message (simulation):")
            print(json.dumps(feishu_message, indent=2, ensure_ascii=False))
        else:
            print("No trend groups to process or screenshots found.")

    else:
        print(f"Attempting to get tenant_access_token with APP_ID: {APP_ID[:5]}...")
        token = get_tenant_access_token(APP_ID, APP_SECRET)
        if token:
            print(f"Tenant access token obtained: {token[:10]}...")
            trend_groups_with_actual_keys = []
            for i, group in enumerate(TREND_GROUPS):
                import re
                filename_base = re.sub(r'[\\/:*?"<>|]', '_', group["name"])
                image_file = f"{filename_base}.png"
                image_path = os.path.join(SCREENSHOT_DIR, image_file)
                
                if os.path.exists(image_path):
                    print(f"Uploading {image_file}...")
                    image_key = upload_image_to_feishu(image_path, token)
                    trend_groups_with_actual_keys.append({
                        "description": group["description"],
                        "image_key": image_key
                    })
                else:
                    print(f"Screenshot not found: {image_path}")
                    trend_groups_with_actual_keys.append({
                        "description": group["description"],
                        "image_key": None
                    })
            
            if trend_groups_with_actual_keys:
                feishu_message = prepare_feishu_message_content(trend_groups_with_actual_keys)
                print("\nPrepared Feishu Message (with actual image uploads if successful):")
                print(json.dumps(feishu_message, indent=2, ensure_ascii=False))
            else:
                print("No trend groups to process or screenshots found for upload.")
        else:
            print("Failed to obtain tenant_access_token. Cannot proceed with image uploads.")

    print("Feishu uploader script finished.")


