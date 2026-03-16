#!/bin/bash
# 本地部署脚本

set -e

echo "🚀 开始本地部署..."

cd "$(dirname "$0")/.."

# 1. 启动后端
echo "📦 启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# 确保数据目录存在
mkdir -p data logs public/images

# 启动后端（后台运行）
echo "后端启动中..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID)"

cd ..

# 2. 等待后端就绪
echo "⏳ 等待后端就绪..."
sleep 5

# 检查后端健康
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ 后端健康检查通过"
else
    echo "❌ 后端启动失败，查看日志：logs/backend.log"
    exit 1
fi

# 3. 启动前端（静态文件服务）
echo "📦 启动前端服务..."
cd frontend

# 检查是否已构建
if [ ! -d "out" ]; then
    echo "构建前端..."
    npm install --silent
    npm run build
fi

# 使用 Python 简单 HTTP 服务器
echo "前端启动中..."
cd out
nohup python3 -m http.server 3000 > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID)"

cd ../..

# 4. 输出访问信息
echo ""
echo "=========================================="
echo "🎉 部署完成！"
echo "=========================================="
echo ""
echo "📱 访问地址:"
echo "   前端：http://localhost:3000"
echo "   后端：http://localhost:8000"
echo "   API 文档：http://localhost:8000/docs"
echo ""
echo "📋 进程信息:"
echo "   后端 PID: $BACKEND_PID"
echo "   前端 PID: $FRONTEND_PID"
echo ""
echo "🛑 停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📄 查看日志:"
echo "   tail -f logs/backend.log"
echo "   tail -f logs/frontend.log"
echo ""
echo "=========================================="

# 保存 PID 以便停止
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
