#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import datetime
import subprocess
import logging
import sys
import pytz
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scheduler.log'))
    ]
)
logger = logging.getLogger('trends_scheduler')

def get_script_dir():
    """获取脚本所在目录的绝对路径"""
    return os.path.dirname(os.path.abspath(__file__))

def run_workflow():
    """运行Google Trends工作流脚本"""
    script_dir = get_script_dir()
    workflow_script = os.path.join(script_dir, "run_trends_workflow.sh")
    
    # 确保脚本有执行权限
    os.chmod(workflow_script, 0o755)
    
    logger.info(f"开始执行工作流脚本: {workflow_script}")
    try:
        # 在脚本目录中执行工作流脚本
        process = subprocess.Popen(
            [workflow_script],
            cwd=script_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            logger.info("工作流脚本执行成功")
            logger.debug(f"输出: {stdout}")
        else:
            logger.error(f"工作流脚本执行失败，返回码: {process.returncode}")
            logger.error(f"错误输出: {stderr}")
    except Exception as e:
        logger.error(f"执行工作流脚本时发生错误: {e}")

def wait_until_next_run(target_hour=9, target_minute=0):
    """
    等待直到下一个指定的运行时间
    默认为每天东八区（北京/上海时间）早上9:00
    无论服务器在哪个时区，都会在东八区的早上9点运行
    """
    # 使用东八区时间
    china_tz = pytz.timezone('Asia/Shanghai')  # 东八区时间区
    
    # 获取当前的东八区时间
    now = datetime.datetime.now(china_tz)
    
    # 设置目标时间为东八区的早上9点
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    # 如果当前时间已经过了今天的目标时间，则设置为明天的目标时间
    if now >= target_time:
        target_time += datetime.timedelta(days=1)
    
    # 计算等待时间（秒）
    wait_seconds = (target_time - now).total_seconds()
    
    logger.info(f"当前东八区时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"下次运行时间(东八区): {target_time.strftime('%Y-%m-%d %H:%M:%S')} (上午9点)")
    logger.info(f"等待时间: {wait_seconds/3600:.2f}小时")
    
    # 添加更明确的日志信息
    am_pm = "上午" if target_hour < 12 else "下午"
    logger.info(f"脚本设置为每天东八区(北京/上海时间){am_pm}{target_hour % 12 or 12}点{target_minute:02d}分运行")
    
    # 显示服务器当前时区信息
    local_now = datetime.datetime.now()
    local_now_aware = datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).astimezone()
    china_now = datetime.datetime.now(china_tz)
    
    # 计算时差（小时）
    time_diff_hours = (china_now.replace(tzinfo=None) - local_now.replace(tzinfo=None)).total_seconds() / 3600
    
    logger.info(f"服务器当前时间: {local_now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"服务器时区: {local_now_aware.tzinfo}")
    logger.info(f"东八区时间: {china_now.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"服务器与东八区时差: {time_diff_hours:.2f}小时")
    
    return wait_seconds

def main():
    """主函数，实现定时运行功能"""
    logger.info("Google Trends 定时器已启动")
    logger.info(f"脚本目录: {get_script_dir()}")
    
    try:
        while True:
            # 计算到下一次运行的等待时间
            wait_seconds = wait_until_next_run(target_hour=9, target_minute=0)
            
            # 等待到指定时间
            time.sleep(wait_seconds)
            
            # 运行工作流
            run_workflow()
            
            # 短暂休息，避免可能的重复运行
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("定时器已手动停止")
    except Exception as e:
        logger.error(f"定时器运行时发生错误: {e}")
        raise

if __name__ == "__main__":
    main()
