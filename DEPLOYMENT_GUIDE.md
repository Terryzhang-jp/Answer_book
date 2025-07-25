# 部署指南

## 🚀 部署流程

### 第一步：部署后端到 Google Cloud Run

#### 1. 准备 Google Cloud 项目
```bash
# 安装 Google Cloud CLI
# 登录并设置项目
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 启用必要的API
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### 2. 配置环境变量
```bash
cd room_protocol_backend

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置以下必要变量：
# GEMINI_API_KEY=your_actual_gemini_api_key
# DEBUG=false
# CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-vercel-app.vercel.app
```

#### 3. 部署到 Cloud Run
```bash
# 方法1: 使用 gcloud 直接部署
gcloud run deploy room-protocol-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars DEBUG=false,HOST=0.0.0.0,PORT=8000 \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest

# 方法2: 使用 Cloud Build (推荐)
gcloud builds submit --config cloudbuild.yaml
```

#### 4. 获取后端URL
```bash
# 部署完成后，获取服务URL
gcloud run services describe room-protocol-backend --region us-central1 --format 'value(status.url)'
```

**保存这个URL，例如：`https://room-protocol-backend-xxx-uc.a.run.app`**

### 第二步：部署前端到 Vercel

#### 1. 准备 Vercel 项目
```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login
```

#### 2. 配置环境变量
```bash
cd room_protocol_frontend

# 在 Vercel 项目中设置环境变量
vercel env add NEXT_PUBLIC_API_URL
# 输入值：https://room-protocol-backend-xxx-uc.a.run.app (你的后端URL)
```

#### 3. 部署前端
```bash
# 部署到 Vercel
vercel --prod
```

#### 4. 获取前端URL
部署完成后，Vercel 会提供前端URL，例如：`https://your-app.vercel.app`

### 第三步：更新后端CORS配置

#### 1. 更新环境变量
```bash
# 回到后端目录
cd room_protocol_backend

# 更新 Cloud Run 服务的环境变量
gcloud run services update room-protocol-backend \
  --region us-central1 \
  --set-env-vars CORS_ALLOWED_ORIGINS="http://localhost:3000,https://your-app.vercel.app"
```

#### 2. 验证部署
```bash
# 测试后端健康检查
curl https://room-protocol-backend-xxx-uc.a.run.app/api/health

# 测试前端访问
# 在浏览器中打开：https://your-app.vercel.app
```

## 🔧 配置说明

### 后端环境变量
```env
# 必需配置
GEMINI_API_KEY=your_actual_gemini_api_key
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS配置 (用你的实际域名替换)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-app.vercel.app

# 可选配置
DEFAULT_MODEL=gemini-2.0-flash-exp
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=100000
MEMORY_DIR=memory
SESSION_TIMEOUT=3600
MAX_SESSIONS=1000
LOG_LEVEL=INFO
```

### 前端环境变量
```env
# Vercel 环境变量
NEXT_PUBLIC_API_URL=https://room-protocol-backend-xxx-uc.a.run.app
```

## 📊 资源配置

### Google Cloud Run 配置
- **内存**: 1GB
- **CPU**: 1 vCPU
- **最大实例数**: 10
- **区域**: us-central1
- **认证**: 允许未经身份验证的调用

### Vercel 配置
- **框架**: Next.js
- **Node.js 版本**: 18.x
- **构建命令**: `npm run build`
- **输出目录**: `.next`

## 🔍 故障排除

### 常见问题

1. **CORS 错误**
   - 确保后端 `CORS_ALLOWED_ORIGINS` 包含前端域名
   - 检查前端 `NEXT_PUBLIC_API_URL` 是否正确

2. **API 连接失败**
   - 验证后端服务是否正常运行
   - 检查网络连接和防火墙设置

3. **环境变量未生效**
   - 重新部署服务以应用新的环境变量
   - 检查环境变量名称是否正确

### 健康检查
```bash
# 后端健康检查
curl https://your-backend-url/api/health

# 前端访问测试
curl https://your-frontend-url
```

## 🎉 完成

部署完成后，您的应用将在以下地址可用：
- **前端**: https://your-app.vercel.app
- **后端**: https://room-protocol-backend-xxx-uc.a.run.app
- **API文档**: https://room-protocol-backend-xxx-uc.a.run.app/docs
