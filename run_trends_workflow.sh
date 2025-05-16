#!/bin/bash

# 设置工作目录
SCRIPT_DIR="/Users/willhu/Desktop/google-trends-scraper"
LOG_DIR="${SCRIPT_DIR}/logs"
SCREENSHOT_DIR="$(cd ~ && pwd)/Desktop/google_trends_screenshots"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# 创建日志目录
mkdir -p "$LOG_DIR"

# 日志文件
TRENDS_LOG="${LOG_DIR}/trends_${TIMESTAMP}.log"
FEISHU_LOG="${LOG_DIR}/feishu_${TIMESTAMP}.log"

echo "===== Google Trends 工作流开始执行 - $(date) ====="

# 步骤 1: 运行 trends_api.py 获取数据
echo "开始执行数据获取脚本..."
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/trends_api.py" > "$TRENDS_LOG" 2>&1

# 检查第一个脚本的执行状态
if [ $? -eq 0 ]; then
    echo "数据获取脚本执行成功，日志保存在: $TRENDS_LOG"
    
    # 步骤 2: 运行 feishu_sender.py 发送数据到飞书
    echo "开始执行飞书发送脚本..."
    python3 "$SCRIPT_DIR/feishu_sender.py" > "$FEISHU_LOG" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "飞书发送脚本执行成功，日志保存在: $FEISHU_LOG"
        
        # 步骤 3: 清理图片文件夹
        echo "开始清理图片文件夹..."
        if [ -d "$SCREENSHOT_DIR" ]; then
            # 备份当前日期的图片到日志目录，文件名加上时间戳
            BACKUP_DIR="${LOG_DIR}/screenshots_${TIMESTAMP}"
            mkdir -p "$BACKUP_DIR"
            
            # 遍历所有PNG文件，复制并重命名为带时间戳的文件
            for img in "$SCREENSHOT_DIR"/*.png; do
                if [ -f "$img" ]; then
                    filename=$(basename "$img")
                    base_name="${filename%.*}"
                    cp "$img" "$BACKUP_DIR/${base_name}_${TIMESTAMP}.png"
                fi
            done
            
            # 删除图片文件夹中的所有PNG文件
            rm -f "$SCREENSHOT_DIR"/*.png
            echo "图片文件夹清理完成。"
        else
            echo "警告: 图片文件夹不存在: $SCREENSHOT_DIR"
        fi
        
        echo "===== 完整工作流执行成功 - $(date) ====="
    else
        echo "错误: 飞书发送脚本执行失败，请查看日志: $FEISHU_LOG"
        echo "===== 工作流执行失败 - $(date) ====="
        exit 1
    fi
else
    echo "错误: 数据获取脚本执行失败，请查看日志: $TRENDS_LOG"
    echo "===== 工作流执行失败 - $(date) ====="
    exit 1
fi
