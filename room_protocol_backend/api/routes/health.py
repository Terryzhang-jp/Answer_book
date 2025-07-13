"""
健康检查路由
"""

from datetime import datetime
from fastapi import APIRouter
from core.schemas.conversation import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查端点"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )
