"""
场景问题API路由
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from loguru import logger

from core.models.scenario import (
    ScenarioQuestionRequest, 
    ScenarioQuestionResponse,
    UserScenarioResponse,
    ScenarioSession
)
from core.services.scenario_question_service import scenario_question_service
from core.services.conversation_service import ConversationService
from core.services.scenario_storage import get_scenario_storage
from langchain_core.messages import BaseMessage

router = APIRouter()

# 获取场景存储实例
scenario_storage = get_scenario_storage()


@router.post("/generate-question", response_model=ScenarioQuestionResponse)
async def generate_scenario_question(request: ScenarioQuestionRequest):
    """生成场景想象问题"""
    try:
        logger.info(f"收到场景问题生成请求 - 线程ID: {request.thread_id}, 用户ID: {request.user_id}")
        
        # 1. 从ConversationService获取对话数据
        conversation_service = ConversationService()
        messages = []

        # 优先从ConversationService获取
        if request.thread_id in conversation_service.chat_histories:
            history = conversation_service.chat_histories[request.thread_id]
            messages = history.messages
            logger.info(f"从ConversationService获取到对话消息 {len(messages)} 条")
        else:
            # 如果ConversationService中没有，尝试从GlobalStorage获取
            from core.services.global_storage import global_storage
            messages = global_storage.get_messages(request.thread_id)
            logger.info(f"从GlobalStorage获取到对话消息 {len(messages)} 条")

        # 检查是否有对话数据
        if not messages or len(messages) == 0:
            raise HTTPException(status_code=404, detail="对话不存在或为空")
        
        # 2. 转换消息格式
        conversation_data = []
        for msg in messages:
            if isinstance(msg, BaseMessage):
                msg_dict = {
                    "type": msg.__class__.__name__,
                    "content": msg.content,
                    "additional_kwargs": getattr(msg, 'additional_kwargs', {})
                }
                conversation_data.append(msg_dict)
        
        # 3. 生成场景问题
        question_data_dict = await scenario_question_service.generate_scenario_question(conversation_data)
        
        # 4. 创建场景会话
        session_id = str(uuid.uuid4())
        scenario_session = ScenarioSession(
            id=session_id,
            thread_id=request.thread_id,
            user_id=request.user_id,
            question_data=question_data_dict,
            created_at=datetime.now(),
            status="waiting"
        )
        
        # 保存到持久化存储
        save_success = await scenario_storage.save_session(scenario_session)
        if not save_success:
            raise HTTPException(status_code=500, detail="保存场景会话失败")

        logger.info(f"场景问题生成成功 - 会话ID: {session_id}")

        return ScenarioQuestionResponse(
            success=True,
            question_data=question_data_dict,
            message="场景问题生成成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成场景问题失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成场景问题失败: {str(e)}")


@router.post("/submit-response")
async def submit_scenario_response(response: UserScenarioResponse):
    """提交用户的场景描述"""
    try:
        logger.info(f"收到用户场景描述 - 线程ID: {response.thread_id}, 用户ID: {response.user_id}")
        
        # 查找对应的场景会话
        sessions = await scenario_storage.list_sessions(thread_id=response.thread_id, user_id=response.user_id)
        session = None
        for s in sessions:
            if s.status == "waiting":
                session = s
                break

        if not session:
            raise HTTPException(status_code=404, detail="未找到对应的场景问答会话")

        # 更新会话
        session.user_response = response.scenario_description
        session.completed_at = datetime.now()
        session.status = "completed"

        # 保存更新后的会话
        save_success = await scenario_storage.save_session(session)
        if not save_success:
            raise HTTPException(status_code=500, detail="更新场景会话失败")

        # 将场景描述加入聊天历史
        try:
            conversation_service = ConversationService()

            # 创建场景描述消息
            from langchain_core.messages import HumanMessage
            scenario_message = HumanMessage(
                content=f"我想象的未来场景：{response.scenario_description}"
            )

            # 添加到聊天历史
            if response.thread_id in conversation_service.chat_histories:
                conversation_service.chat_histories[response.thread_id].add_message(scenario_message)
                logger.info(f"场景描述已添加到聊天历史 - 线程ID: {response.thread_id}")
            else:
                logger.warning(f"聊天历史不存在，无法添加场景描述 - 线程ID: {response.thread_id}")

            # 同时保存到GlobalStorage
            from core.services.global_storage import global_storage
            messages = global_storage.get_messages(response.thread_id)
            messages.append(scenario_message)
            global_storage.save_messages(response.thread_id, messages)
            logger.info(f"场景描述已保存到GlobalStorage - 线程ID: {response.thread_id}")

        except Exception as e:
            logger.error(f"保存场景描述到聊天历史失败: {e}")
            # 不影响主流程，继续执行

        logger.info(f"用户场景描述提交成功 - 会话ID: {session.id}")

        return {
            "success": True,
            "message": "场景描述提交成功",
            "session_id": session.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交场景描述失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"提交场景描述失败: {str(e)}")


@router.get("/session/{session_id}")
async def get_scenario_session(session_id: str):
    """获取场景会话信息"""
    try:
        session = await scenario_storage.load_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="场景会话不存在")

        return {
            "success": True,
            "session": session.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取场景会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取场景会话失败: {str(e)}")


@router.get("/sessions/thread/{thread_id}")
async def get_thread_scenario_sessions(thread_id: str):
    """获取指定线程的所有场景会话"""
    try:
        sessions = await scenario_storage.list_sessions(thread_id=thread_id)
        thread_sessions = [session.model_dump() for session in sessions]

        return {
            "success": True,
            "sessions": thread_sessions
        }
        
    except Exception as e:
        logger.error(f"获取线程场景会话失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取线程场景会话失败: {str(e)}")


@router.post("/migrate-from-memory")
async def migrate_from_memory():
    """将内存中的场景会话迁移到持久化存储（仅用于数据迁移）"""
    try:
        # 这里的scenario_sessions是全局变量，包含了内存中的数据
        # 在实际部署时，这个变量可能为空，这是正常的
        global scenario_sessions

        if not scenario_sessions:
            return {
                "success": True,
                "message": "没有需要迁移的内存数据",
                "migrated_count": 0
            }

        # 执行迁移
        from core.services.scenario_storage import FileScenarioStorage
        file_storage = FileScenarioStorage()
        migrated_count = await file_storage.migrate_from_memory(scenario_sessions)

        # 清空内存数据（迁移完成后）
        if migrated_count > 0:
            scenario_sessions.clear()
            logger.info(f"内存数据迁移完成，已清空内存存储")

        return {
            "success": True,
            "message": f"数据迁移完成，成功迁移 {migrated_count} 个会话",
            "migrated_count": migrated_count
        }

    except Exception as e:
        logger.error(f"数据迁移失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"数据迁移失败: {str(e)}")


# 保留内存存储变量用于向后兼容和数据迁移
scenario_sessions = {}
