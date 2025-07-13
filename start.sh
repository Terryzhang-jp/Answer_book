#!/bin/bash

# 答案之书系统启动脚本

echo "🚀 启动答案之书系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📚 安装依赖包..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "⚠️  .env 文件不存在，请复制 .env.example 并配置API密钥"
    cp .env.example .env
    echo "📝 请编辑 .env 文件并添加您的API密钥："
    echo "   - ANTHROPIC_API_KEY"
    echo "   - OPENAI_API_KEY"
    echo ""
    echo "配置完成后，请重新运行此脚本"
    exit 1
fi

# 启动服务器
echo "🌟 启动FastAPI服务器..."
echo "📍 服务地址: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"

python main.py
