"""
Room Protocol Backend - Main Application Entry Point
"""

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import conversation, health, session, insight, report, scenario, storage_admin
from api.middleware.auth import OptionalAuthMiddleware
from config.settings import get_settings
from core.services.llm_service import LLMService

# 获取配置
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    await LLMService.initialize()
    yield
    # 关闭时清理资源
    pass


# 创建FastAPI应用
app = FastAPI(
    title="Room Protocol Backend",
    description="智能对话房间系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加认证中间件（在CORS之前）
app.add_middleware(OptionalAuthMiddleware)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,  # 从配置读取允许的域名
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(","),
    allow_headers=settings.CORS_ALLOW_HEADERS.split(","),
)

# 注册路由
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(conversation.router, prefix="/api", tags=["conversation"])
app.include_router(session.router, prefix="/api", tags=["session"])
app.include_router(insight.router, prefix="/api/insight", tags=["insight"])
app.include_router(report.router, prefix="/api/report", tags=["report"])
app.include_router(scenario.router, prefix="/api/scenario", tags=["scenario"])
app.include_router(storage_admin.router, prefix="/api/admin", tags=["storage-admin"])


# 旧的事件处理器已移至lifespan函数中


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
