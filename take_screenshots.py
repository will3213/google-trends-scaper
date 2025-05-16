from playwright.sync_api import sync_playwright
import os
import re

# Configuration
SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "google_trends_screenshots")
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

def sanitize_filename(name):
    # Remove or replace characters not suitable for filenames
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    return name

def take_screenshots():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
        print(f"Created directory: {SCREENSHOT_DIR}")

    with sync_playwright() as p:
        # 使用有头浏览器模式，以便在需要时可以手动处理验证码
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_viewport_size({"width": 1280, "height": 800})
        
        # 增加随机等待时间函数，模拟人类行为
        def random_wait(min_seconds=3, max_seconds=7):
            import random
            wait_time = random.uniform(min_seconds, max_seconds) * 1000  # 转换为毫秒
            page.wait_for_timeout(wait_time)
            return wait_time / 1000  # 返回等待的秒数

        for i, group in enumerate(TREND_GROUPS):
            group_name_for_file = group["name"]
            group_description = group["description"]
            url = group["url"]
            filename_base = sanitize_filename(group_name_for_file)
            screenshot_path = os.path.join(SCREENSHOT_DIR, f"{filename_base}.png")
            
            print(f"Processing group {i+1}/{len(TREND_GROUPS)}: {group_description}")
            print(f"Navigating to URL: {url}")
            
            try:
                # 在每次请求之间增加较长的随机等待时间
                if i > 0:
                    wait_time = random_wait(8, 15)
                    print(f"Waiting {wait_time:.2f} seconds before next request...")
                
                page.goto(url, wait_until="networkidle", timeout=90000)
                random_wait()
                
                # 处理同意对话框
                consent_selectors = [
                    "button:has-text('Accept all')", 
                    "button:has-text('I agree')",
                    "button:has-text('同意')",
                    "form[action*='consent'] button[type='submit']",
                    "button:has-text('Alle akzeptieren')", # German for 'Accept all'
                    "button:has-text('Ich stimme zu')" # German for 'I agree'
                ]
                for selector in consent_selectors:
                    element = page.query_selector(selector)
                    if element and element.is_visible():
                        print(f"Found consent element: {selector}. Clicking it.")
                        element.click(timeout=5000)
                        random_wait()
                        break
                
                # 检查是否存在reCAPTCHA
                recaptcha_frames = page.locator('iframe[src*="recaptcha"]')
                recaptcha_count = recaptcha_frames.count()
                if recaptcha_count > 0:
                    print("\n*** reCAPTCHA detected! ***")
                    print("请在浏览器窗口中手动完成验证码，完成后按Enter继续...")
                    input()  # 等待用户手动处理验证码并按Enter
                    print("继续处理...")
                    random_wait()
                
                # 等待图表加载
                page.wait_for_timeout(8000)  # 增加等待时间，确保图表完全加载
                
                # 模拟人类行为：随机滚动
                page.mouse.wheel(0, random.randint(100, 300))
                random_wait()
                page.mouse.wheel(0, random.randint(-200, -50))
                random_wait()
                
                page.screenshot(path=screenshot_path)
                print(f"Screenshot saved to: {screenshot_path}")
            except Exception as e:
                print(f"Error taking screenshot for {group_description} ({url}): {e}")
                # 如果出错，尝试保存当前页面状态
                try:
                    error_screenshot_path = os.path.join(SCREENSHOT_DIR, f"error_{filename_base}.png")
                    page.screenshot(path=error_screenshot_path)
                    print(f"Error state screenshot saved to: {error_screenshot_path}")
                except:
                    pass
        
        browser.close()
    print("All screenshots processed.")

if __name__ == "__main__":
    take_screenshots()

