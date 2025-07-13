"""
对话相关路由
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from core.schemas.conversation import (
    QuestionRequest,
    ContinueRequest,
    AnswerResponse
)
from core.services.conversation_service import ConversationService
from config.settings import get_settings

router = APIRouter()

# 创建对话服务实例
conversation_service = ConversationService()


@router.post("/room/create", response_model=AnswerResponse)
async def create_room(request: QuestionRequest):
    """创建新房间"""
    try:
        # 强制创建新thread_id（不使用传入的thread_id）
        request.thread_id = None
        response = await conversation_service.process_question(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """继续对话（需要提供thread_id）"""
    try:
        if not request.thread_id:
            raise HTTPException(status_code=400, detail="继续对话必须提供thread_id")
        response = await conversation_service.process_question(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/continue", response_model=AnswerResponse)
async def continue_conversation(request: ContinueRequest):
    """继续对话"""
    try:
        response = await conversation_service.continue_conversation(request)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 新记忆系统测试端点 ==========

@router.post("/v2/room/create", response_model=AnswerResponse)
async def create_room_v2(request: QuestionRequest):
    """创建新房间 - v2版本（新记忆系统）"""
    try:
        # 强制启用新记忆系统
        settings = get_settings()
        original_setting = settings.ENABLE_NEW_MEMORY_SYSTEM

        # 临时启用新系统
        settings.ENABLE_NEW_MEMORY_SYSTEM = True

        try:
            # 强制创建新thread_id
            request.thread_id = None
            response = await conversation_service.process_question(request)
            return response
        finally:
            # 恢复原设置
            settings.ENABLE_NEW_MEMORY_SYSTEM = original_setting

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"v2创建房间失败: {str(e)}")


@router.post("/v2/ask", response_model=AnswerResponse)
async def ask_question_v2(request: QuestionRequest):
    """继续对话 - v2版本（新记忆系统）"""
    try:
        # 强制启用新记忆系统
        settings = get_settings()
        original_setting = settings.ENABLE_NEW_MEMORY_SYSTEM

        # 临时启用新系统
        settings.ENABLE_NEW_MEMORY_SYSTEM = True

        try:
            if not request.thread_id:
                raise HTTPException(status_code=400, detail="继续对话必须提供thread_id")
            response = await conversation_service.process_question(request)
            return response
        finally:
            # 恢复原设置
            settings.ENABLE_NEW_MEMORY_SYSTEM = original_setting

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"v2对话失败: {str(e)}")


@router.post("/test/memory-system", response_model=dict)
async def test_memory_system():
    """测试记忆系统状态"""
    try:
        settings = get_settings()

        # 检查新记忆系统可用性
        memory_available = False
        try:
            from core.services.memory_service import ModernMemoryService
            memory_service = ModernMemoryService()
            memory_stats = memory_service.get_memory_stats()
            memory_available = True
        except Exception as e:
            memory_stats = {"error": str(e)}

        return {
            "new_memory_system_enabled": settings.ENABLE_NEW_MEMORY_SYSTEM,
            "new_memory_system_available": memory_available,
            "sliding_window_size": settings.MEMORY_SLIDING_WINDOW_SIZE,
            "summary_model": settings.MEMORY_SUMMARY_MODEL,
            "async_analysis_enabled": settings.ENABLE_ASYNC_ANALYSIS,
            "memory_stats": memory_stats,
            "conversation_service_type": type(conversation_service).__name__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试失败: {str(e)}")


@router.post("/test/performance-compare")
async def performance_compare(request: QuestionRequest):
    """性能对比测试（同时测试新旧系统）"""
    import time

    try:
        results = {}

        # 测试旧系统
        settings = get_settings()
        settings.ENABLE_NEW_MEMORY_SYSTEM = False

        start_time = time.time()
        try:
            old_response = await conversation_service.process_question_v1(request)
            old_time = time.time() - start_time
            results["old_system"] = {
                "response_time": old_time,
                "success": True,
                "thread_id": old_response.thread_id
            }
        except Exception as e:
            old_time = time.time() - start_time
            results["old_system"] = {
                "response_time": old_time,
                "success": False,
                "error": str(e)
            }

        # 测试新系统
        settings.ENABLE_NEW_MEMORY_SYSTEM = True

        start_time = time.time()
        try:
            new_response = await conversation_service.process_question_v2(request)
            new_time = time.time() - start_time
            results["new_system"] = {
                "response_time": new_time,
                "success": True,
                "thread_id": new_response.thread_id
            }
        except Exception as e:
            new_time = time.time() - start_time
            results["new_system"] = {
                "response_time": new_time,
                "success": False,
                "error": str(e)
            }

        # 计算性能提升
        if results["old_system"]["success"] and results["new_system"]["success"]:
            improvement = (results["old_system"]["response_time"] - results["new_system"]["response_time"]) / results["old_system"]["response_time"] * 100
            results["performance_improvement"] = f"{improvement:.1f}%"

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"性能对比测试失败: {str(e)}")
