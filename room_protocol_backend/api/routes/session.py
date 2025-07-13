"""
会话管理路由
"""

from fastapi import APIRouter, HTTPException
from core.schemas.conversation import SessionListResponse
from core.services.conversation_service import ConversationService

router = APIRouter()

# 创建对话服务实例
conversation_service = ConversationService()


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """列出所有会话"""
    try:
        sessions = conversation_service.get_all_sessions()
        return SessionListResponse(sessions=sessions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{thread_id}")
async def delete_session(thread_id: str):
    """删除指定会话"""
    try:
        success = conversation_service.delete_session(thread_id)
        if success:
            return {"message": f"会话 {thread_id} 已删除"}
        else:
            raise HTTPException(status_code=404, detail="会话不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
