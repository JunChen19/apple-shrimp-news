#!/bin/bash
# 前端启动脚本

cd "$(dirname "$0")/../frontend"

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装依赖..."
    npm install
fi

# 启动开发服务器
echo "启动前端开发服务器..."
echo "访问地址：http://localhost:3000"
npm run dev
