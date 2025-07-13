"""
智能Insight相关路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from loguru import logger

from core.schemas.insight import (
    InsightRequest,
    InsightResponse
)
from core.services.insight_service import InsightService
from api.routes.conversation import conversation_service

router = APIRouter()


@router.post("/generate", response_model=InsightResponse)
async def generate_insight(request: InsightRequest):
    """
    生成智能insight
    """
    try:
        logger.info(f"开始生成insight - 用户: {request.user_id}, 线程: {request.thread_id}")
        
        result = await InsightService.create_insight_session(
            user_id=request.user_id,
            thread_id=request.thread_id,
            conversation_service=conversation_service
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        response = InsightResponse(
            success=True,
            session_id=result["session_id"],
            insight=result["insight"],
            analysis_summary=result.get("analysis_summary")
        )
        
        logger.info(f"Insight生成成功 - 会话: {result['session_id']}, insight: {result['insight'][:50]}...")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成insight失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成insight失败: {str(e)}")


@router.get("/session/{session_id}")
async def get_insight_session(session_id: str):
    """
    获取insight会话信息
    """
    try:
        if session_id not in InsightService._sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        session_data = InsightService._sessions[session_id]
        return {
            "success": True,
            "session_data": session_data.dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取insight会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取会话失败: {str(e)}")


@router.get("/health")
async def insight_health_check():
    """
    Insight服务健康检查
    """
    try:
        # 检查模型是否可用
        model = InsightService.get_flash_model()
        model_status = "available" if model else "unavailable"
        
        return {
            "status": "healthy",
            "service": "insight_generation",
            "model_status": model_status,
            "active_sessions": len(InsightService._sessions)
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "service": "insight_generation",
            "error": str(e)
        }
