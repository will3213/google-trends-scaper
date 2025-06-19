#!/bin/bash

# 服务器更新脚本

echo "开始更新服务器上的Google Trends Scraper项目..."

# SSH连接到服务器并执行更新操作
# 使用-t选项分配伪终端
ssh -t root@45.77.129.59 << 'EOF'
  echo "已连接到服务器，开始更新..."
  
  # 进入项目目录
  cd ~/google-trends-scaper
  
  # 显示当前目录和分支状态
  pwd
  git status
  
  # 拉取最新代码
  echo "正在拉取最新代码..."
  git pull
  
  # 确保Python虚拟环境已激活（如果使用虚拟环境）
  if [ -d "venv" ]; then
    echo "激活Python虚拟环境..."
    source venv/bin/activate
  fi
  
  # 停止当前运行的调度器进程
  echo "停止当前运行的调度器进程..."
  ps aux | grep scheduler.py | grep -v grep | awk '{print $2}' | xargs -r kill -9
  
  # 等待进程完全停止
  sleep 2
  
  # 重新启动调度器
  echo "重新启动调度器..."
  nohup python3 scheduler.py > scheduler_output.log 2>&1 &
  
  # 验证调度器是否成功启动
  sleep 2
  ps aux | grep scheduler.py | grep -v grep
  
  # 显示确认信息
  echo "更新完成，调度器已重启"
  echo "当前时间: $(date)"
EOF

echo "服务器更新脚本执行完毕"
