#!/bin/bash

# 存储优化系统启动脚本
# 版本: v2.0
# 日期: 2025-07-10

echo "🚀 启动存储优化系统..."

# 检查Python环境
if ! command -v python &> /dev/null; then
    echo "❌ Python未安装，请先安装Python 3.9+"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python -c "import uvicorn, fastapi, langchain_core" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ 缺少必要依赖，请运行: pip install -r requirements.txt"
    exit 1
fi

# 设置环境变量
export ENABLE_SHARDED_STORAGE=true
export SHARD_COUNT=100
export STORAGE_BASE_PATH=data/conversations
export CACHE_MAX_SIZE=500
export CACHE_TTL=3600

echo "✅ 环境配置完成"
echo "   - 分片存储: 启用"
echo "   - 分片数量: 100"
echo "   - 缓存大小: 500"
echo "   - 缓存TTL: 3600秒"

# 创建必要目录
mkdir -p data/conversations
mkdir -p logs
mkdir -p backup

echo "📁 目录结构已创建"

# 启动服务器
echo "🌟 启动FastAPI服务器..."
echo "   - 地址: http://localhost:8000"
echo "   - 管理API: http://localhost:8000/api/admin/storage/health"
echo "   - 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=========================="

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
