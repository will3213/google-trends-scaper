from pytrends.request import TrendReq
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import datetime
import time
import random
import re
import requests
import sys
import matplotlib.font_manager as fm
from requests.exceptions import RequestException

# 配置中文字体支持
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Microsoft YaHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 配置
SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Desktop", "google_trends_screenshots")

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
BASE_WAIT_TIME = 60  # 基础等待时间（秒）
MAX_WAIT_TIME = 300  # 最大等待时间（秒）

# 只处理一个关键词组
TREND_GROUP = {"name": "chat_models_Claude_deepseek_gemini_grok", "description": "chat模型词：Claude/deepseek/gemini/grok", "keywords": ["Claude", "deepseek", "gemini", "grok"]}

def sanitize_filename(name):
    # 移除或替换不适合文件名的字符
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    return name

def random_sleep(min_seconds=5, max_seconds=15):
    """随机等待一段时间，避免请求过于频繁"""
    sleep_time = random.uniform(min_seconds, max_seconds)
    print(f"等待 {sleep_time:.2f} 秒...")
    time.sleep(sleep_time)

def exponential_backoff(retry_count):
    """指数退避算法，随着重试次数增加等待时间"""
    wait_time = min(MAX_WAIT_TIME, BASE_WAIT_TIME * (2 ** retry_count) + random.uniform(0, 10))
    print(f"遇到限制，等待 {wait_time:.2f} 秒后重试...")
    time.sleep(wait_time)

def get_trends_data_single():
    """获取单个关键词组的 Google Trends 数据并生成图表"""
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)
        print(f"创建目录: {SCREENSHOT_DIR}")

    # 连接到 Google Trends
    print("连接到 Google Trends...")
    
    # 尝试不同的请求头，模拟真实浏览器
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://trends.google.com/',
        'DNT': '1'
    }
    
    # 创建 TrendReq 实例，添加请求头
    pytrends = TrendReq(hl='zh-CN', tz=480, timeout=(10, 25),
                        requests_args={'headers': request_headers})
    
    group = TREND_GROUP
    group_name = group["name"]
    group_description = group["description"]
    keywords = group["keywords"]
    filename_base = sanitize_filename(group_name)
    chart_path = os.path.join(SCREENSHOT_DIR, f"{filename_base}.png")
    
    print(f"处理: {group_description}")
    print(f"关键词: {', '.join(keywords)}")
    
    retry_count = 0
    success = False
    
    while retry_count < MAX_RETRIES and not success:
        try:
            # 构建请求
            pytrends.build_payload(
                kw_list=keywords,
                cat=0,
                timeframe='now 7-d',
                geo='',
                gprop=''
            )
            
            # 获取兴趣随时间变化数据
            interest_over_time_df = pytrends.interest_over_time()
            
            if interest_over_time_df.empty:
                print(f"警告: 未找到 {group_description} 的数据")
                break
                
            success = True
            
            # 创建图表
            plt.figure(figsize=(12, 6))
            
            # 设置样式
            sns.set_style("whitegrid")
            
            # 绘制每个关键词的趋势线
            for keyword in keywords:
                if keyword in interest_over_time_df.columns:
                    plt.plot(interest_over_time_df.index, interest_over_time_df[keyword], marker='o', linewidth=2, label=keyword)
            
            # 添加标题和标签
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            plt.title(f"{current_date} Google Trends: {group_description}", fontsize=16)
            plt.xlabel('日期', fontsize=12)
            plt.ylabel('搜索兴趣 (相对值)', fontsize=12)
            plt.legend(fontsize=10)
            plt.grid(True)
            
            # 保存图表
            plt.tight_layout()
            plt.savefig(chart_path, dpi=100)
            plt.close()
            
            print(f"图表已保存到: {chart_path}")
            
        except Exception as e:
            error_message = str(e)
            print(f"获取 {group_description} 数据时出错: {e}")
            
            # 检查是否是 429 错误
            if "429" in error_message or "too many requests" in error_message.lower():
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    exponential_backoff(retry_count)
                    # 尝试重新创建 pytrends 实例，使用不同的请求头
                    new_user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 122)}.0.0.0 Safari/537.36"
                    request_headers['User-Agent'] = new_user_agent
                    pytrends = TrendReq(hl='zh-CN', tz=480, timeout=(10, 25),
                                       requests_args={'headers': request_headers})
                else:
                    print(f"达到最大重试次数，无法获取 {group_description} 的数据")
                    break
            else:
                # 其他类型的错误，不重试
                break
    
    print("处理完成。")

def main():
    try:
        print(f"开始运行单个关键词组的 Google Trends 数据获取脚本 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        get_trends_data_single()
        print(f"脚本执行完成 - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except KeyboardInterrupt:
        print("\n用户中断执行")
        sys.exit(0)
    except Exception as e:
        print(f"脚本执行过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
