#!/bin/bash

# Room Protocol 快速部署脚本
# 使用方法: ./deploy.sh

set -e

echo "🚀 Room Protocol 部署脚本"
echo "=========================="

# 检查必要工具
check_tools() {
    echo "📋 检查必要工具..."
    
    if ! command -v gcloud &> /dev/null; then
        echo "❌ Google Cloud CLI 未安装，请先安装: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v vercel &> /dev/null; then
        echo "❌ Vercel CLI 未安装，正在安装..."
        npm install -g vercel
    fi
    
    echo "✅ 工具检查完成"
}

# 部署后端
deploy_backend() {
    echo ""
    echo "🔧 部署后端到 Google Cloud Run..."
    
    cd room_protocol_backend
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        echo "⚠️  .env 文件不存在，请先配置环境变量"
        echo "   复制 .env.example 为 .env 并填入你的 API 密钥"
        exit 1
    fi
    
    # 部署到 Cloud Run
    echo "📦 正在部署到 Cloud Run..."
    gcloud run deploy room-protocol-backend \
        --source . \
        --region us-central1 \
        --platform managed \
        --allow-unauthenticated \
        --memory 1Gi \
        --cpu 1 \
        --max-instances 10 \
        --set-env-vars DEBUG=false,HOST=0.0.0.0,PORT=8000
    
    # 获取后端URL
    BACKEND_URL=$(gcloud run services describe room-protocol-backend --region us-central1 --format 'value(status.url)')
    echo "✅ 后端部署完成！"
    echo "   URL: $BACKEND_URL"
    
    cd ..
    echo "$BACKEND_URL" > backend_url.txt
}

# 部署前端
deploy_frontend() {
    echo ""
    echo "🎨 部署前端到 Vercel..."
    
    cd room_protocol_frontend
    
    # 读取后端URL
    if [ -f "../backend_url.txt" ]; then
        BACKEND_URL=$(cat ../backend_url.txt)
        echo "📡 使用后端URL: $BACKEND_URL"
        
        # 设置环境变量
        vercel env add NEXT_PUBLIC_API_URL production <<< "$BACKEND_URL"
    else
        echo "⚠️  未找到后端URL，请手动设置 NEXT_PUBLIC_API_URL"
    fi
    
    # 部署前端
    echo "📦 正在部署到 Vercel..."
    vercel --prod
    
    echo "✅ 前端部署完成！"
    cd ..
}

# 更新CORS配置
update_cors() {
    echo ""
    echo "🔄 更新后端CORS配置..."
    
    echo "请输入你的前端URL (例如: https://your-app.vercel.app):"
    read FRONTEND_URL
    
    if [ -n "$FRONTEND_URL" ]; then
        CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000,$FRONTEND_URL"
        
        gcloud run services update room-protocol-backend \
            --region us-central1 \
            --set-env-vars CORS_ALLOWED_ORIGINS="$CORS_ORIGINS"
        
        echo "✅ CORS配置已更新"
    else
        echo "⚠️  跳过CORS配置更新"
    fi
}

# 验证部署
verify_deployment() {
    echo ""
    echo "🔍 验证部署..."
    
    if [ -f "backend_url.txt" ]; then
        BACKEND_URL=$(cat backend_url.txt)
        echo "测试后端健康检查..."
        
        if curl -f "$BACKEND_URL/api/health" > /dev/null 2>&1; then
            echo "✅ 后端健康检查通过"
        else
            echo "❌ 后端健康检查失败"
        fi
    fi
    
    echo ""
    echo "🎉 部署完成！"
    echo "=========================="
    echo "后端URL: $(cat backend_url.txt 2>/dev/null || echo '请查看 Cloud Run 控制台')"
    echo "前端URL: 请查看 Vercel 部署输出"
    echo "API文档: $(cat backend_url.txt 2>/dev/null || echo 'BACKEND_URL')/docs"
}

# 主函数
main() {
    check_tools
    
    echo ""
    echo "选择部署选项:"
    echo "1) 完整部署 (后端 + 前端)"
    echo "2) 仅部署后端"
    echo "3) 仅部署前端"
    echo "4) 更新CORS配置"
    echo ""
    read -p "请选择 (1-4): " choice
    
    case $choice in
        1)
            deploy_backend
            deploy_frontend
            update_cors
            verify_deployment
            ;;
        2)
            deploy_backend
            verify_deployment
            ;;
        3)
            deploy_frontend
            ;;
        4)
            update_cors
            ;;
        *)
            echo "❌ 无效选择"
            exit 1
            ;;
    esac
}

# 运行主函数
main
