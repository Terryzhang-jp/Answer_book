"""
智能Insight服务 - 使用Gemini 2.5 Flash分析对话内容并生成深刻insights
"""

import os
import json
import asyncio
from typing import List, Dict, Optional, Any
from langchain.chat_models.base import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, AIMessage
from loguru import logger
from datetime import datetime

from config.settings import get_settings
from core.schemas.insight import (
    InsightRequest,
    InsightResponse,
    InsightSessionData,
    ConversationData
)
from core.services.global_storage import global_storage


class InsightService:
    """智能Insight服务类"""
    
    _flash_model = None
    _sessions: Dict[str, InsightSessionData] = {}
    
    @classmethod
    def get_flash_model(cls):
        """获取Gemini 2.5 Flash模型实例"""
        if cls._flash_model is None:
            settings = get_settings()
            
            try:
                # 检查API密钥
                api_key = settings.GEMINI_API_KEY
                if not api_key:
                    logger.warning("GEMINI_API_KEY未配置，Insight功能将被禁用")
                    return None

                # 设置环境变量
                os.environ["GOOGLE_API_KEY"] = api_key

                cls._flash_model = init_chat_model(
                    "gemini-2.5-flash",
                    model_provider="google-genai",
                    temperature=0.7,  # 适中的创造性
                    max_tokens=2000   # 增加token限制，确保有足够空间输出
                )
                logger.info("Insight分析模型初始化成功: gemini-2.5-flash")
            except Exception as e:
                logger.error(f"Insight分析模型初始化失败: {e}")
                return None

        return cls._flash_model

    @classmethod
    async def generate_insight_from_conversation(
        cls, 
        thread_id: str, 
        conversation_service=None
    ) -> Dict[str, Any]:
        """
        从对话历史生成智能insight
        
        Args:
            thread_id: 对话线程ID
            conversation_service: 对话服务实例，用于获取历史数据
            
        Returns:
            包含insight的结果字典
        """
        try:
            # 获取对话数据
            conversation_data = await cls._extract_conversation_data(thread_id, conversation_service)
            
            if not conversation_data.user_questions and not conversation_data.guest_responses:
                return {
                    "success": False,
                    "message": "没有找到足够的对话内容来生成insight"
                }

            # 生成insight
            insight = await cls._generate_insight_with_llm(conversation_data)
            
            if not insight:
                return {
                    "success": False,
                    "message": "无法生成insight"
                }

            return {
                "success": True,
                "insight": insight,
                "analysis_summary": f"分析了{conversation_data.total_messages}条消息，包含{len(conversation_data.user_questions)}个用户问题"
            }

        except Exception as e:
            logger.error(f"生成insight失败: {e}")
            return {
                "success": False,
                "message": f"生成失败: {str(e)}"
            }

    @classmethod
    async def _extract_conversation_data(
        cls, 
        thread_id: str, 
        conversation_service=None
    ) -> ConversationData:
        """
        从对话历史中提取关键数据
        """
        conversation_data = ConversationData()
        
        if not conversation_service:
            logger.warning("没有提供conversation_service，无法获取对话历史")
            return conversation_data

        try:
            # 获取历史消息
            messages = []

            # 首先尝试从全局存储获取
            messages = global_storage.get_messages(thread_id)

            # 如果全局存储没有数据，尝试从conversation_service获取
            if not messages and conversation_service:
                # 尝试从现代记忆系统获取
                if hasattr(conversation_service, 'modern_memory') and conversation_service.modern_memory:
                    messages = conversation_service.modern_memory.get_messages_from_backup(thread_id)
                    logger.info(f"从现代记忆系统获取到{len(messages)}条消息")

                # 如果现代记忆系统没有数据，尝试从传统系统获取
                if not messages and hasattr(conversation_service, 'chat_histories'):
                    if thread_id in conversation_service.chat_histories:
                        history = conversation_service.chat_histories[thread_id]
                        messages = history.messages
                        logger.info(f"从传统记忆系统获取到{len(messages)}条消息")

            # 解析消息内容
            for message in messages:
                if isinstance(message, HumanMessage):
                    # 用户问题
                    conversation_data.user_questions.append(message.content)
                elif isinstance(message, AIMessage):
                    # AI回复，尝试解析JSON格式的嘉宾回答
                    try:
                        ai_content = message.content
                        if ai_content.strip().startswith('{'):
                            # 尝试解析JSON格式的回复
                            response_data = json.loads(ai_content)
                            if 'character_responses' in response_data:
                                for char_response in response_data['character_responses']:
                                    guest_response = {
                                        'character_name': char_response.get('character_name', ''),
                                        'thinking': char_response.get('thinking', ''),
                                        'speaking': char_response.get('speaking', ''),
                                        'body_language': char_response.get('body_language', '')
                                    }
                                    conversation_data.guest_responses.append(guest_response)
                        else:
                            # 普通文本回复
                            conversation_data.guest_responses.append({
                                'character_name': 'AI助手',
                                'speaking': ai_content,
                                'thinking': '',
                                'body_language': ''
                            })
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，作为普通回复处理
                        conversation_data.guest_responses.append({
                            'character_name': 'AI助手',
                            'speaking': message.content,
                            'thinking': '',
                            'body_language': ''
                        })

            conversation_data.total_messages = len(messages)
            conversation_data.conversation_context = f"对话包含{len(conversation_data.user_questions)}个用户问题和{len(conversation_data.guest_responses)}个嘉宾回答"
            
            logger.info(f"提取对话数据完成: {conversation_data.conversation_context}")
            return conversation_data

        except Exception as e:
            logger.error(f"提取对话数据失败: {e}")
            return conversation_data

    @classmethod
    async def _generate_insight_with_llm(cls, conversation_data: ConversationData) -> str:
        """
        使用LLM生成insight
        """
        model = cls.get_flash_model()
        if not model:
            logger.warning("LLM模型不可用，返回默认insight")
            return "继续探索，答案就在对话中。"

        try:
            # 构建分析内容
            user_questions_text = "\n".join([f"- {q}" for q in conversation_data.user_questions])
            
            guest_responses_text = ""
            for i, response in enumerate(conversation_data.guest_responses, 1):
                guest_responses_text += f"\n{i}. {response['character_name']}:\n"
                if response['thinking']:
                    guest_responses_text += f"   思考: {response['thinking']}\n"
                if response['speaking']:
                    guest_responses_text += f"   发言: {response['speaking']}\n"
                if response['body_language']:
                    guest_responses_text += f"   肢体语言: {response['body_language']}\n"

            # 构建提示词
            system_prompt = """根据对话内容，生成一句优美的智慧箴言。

要求：
1. 不超过15个字
2. 富有诗意和哲理
3. 只返回箴言，不要解释

示例风格：
- "心之所向，道之所在"
- "知者不言，言者不知"
- "山重水复疑无路，柳暗花明又一村"
"""

            user_prompt = f"""对话内容：
问题：{user_questions_text}
回答：{guest_responses_text}

生成一句智慧箴言："""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            logger.info(f"正在调用LLM生成insight，消息数: {len(messages)}")
            response = await model.ainvoke(messages)

            logger.info(f"LLM原始响应类型: {type(response)}")
            logger.info(f"LLM原始响应内容: {response}")

            insight = response.content.strip() if hasattr(response, 'content') else str(response).strip()
            logger.info(f"提取的insight内容: '{insight}' (长度: {len(insight)})")

            # 清理可能的格式问题
            if insight.startswith('"') and insight.endswith('"'):
                insight = insight[1:-1]
                logger.info(f"清理引号后的insight: '{insight}'")

            # 检查insight是否为空
            if not insight:
                logger.warning("LLM返回了空的insight，使用默认值")
                insight = "言有尽而意无穷，思无涯而道自明。"

            logger.info(f"成功生成insight: {insight}")
            return insight

        except Exception as e:
            logger.error(f"LLM生成insight失败: {e}")
            return "山重水复疑无路，柳暗花明又一村。"

    @classmethod
    async def create_insight_session(
        cls, 
        user_id: str, 
        thread_id: str, 
        conversation_service=None
    ) -> Dict[str, Any]:
        """
        创建insight会话
        """
        try:
            # 生成会话ID
            session_id = f"insight_{user_id}_{int(datetime.now().timestamp() * 1000)}"
            
            # 生成insight
            result = await cls.generate_insight_from_conversation(thread_id, conversation_service)
            
            if not result["success"]:
                return result

            # 创建会话数据
            session_data = InsightSessionData(
                session_id=session_id,
                user_id=user_id,
                thread_id=thread_id,
                insight=result["insight"],
                analysis_data={
                    "analysis_summary": result.get("analysis_summary", ""),
                    "generated_at": datetime.now().isoformat()
                },
                status="completed"
            )
            
            # 存储会话
            cls._sessions[session_id] = session_data
            
            # 保存到文件（简单持久化）
            await cls._save_session_to_file(session_data)

            return {
                "success": True,
                "session_id": session_id,
                "insight": result["insight"],
                "analysis_summary": result.get("analysis_summary", "")
            }

        except Exception as e:
            logger.error(f"创建insight会话失败: {e}")
            return {
                "success": False,
                "message": f"创建失败: {str(e)}"
            }

    @classmethod
    async def _save_session_to_file(cls, session_data: InsightSessionData):
        """保存会话数据到文件"""
        try:
            # 确保目录存在
            insight_dir = "memory/insight"
            os.makedirs(insight_dir, exist_ok=True)
            
            # 保存文件
            file_path = f"{insight_dir}/{session_data.session_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(session_data.dict(), f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"Insight会话数据已保存: {file_path}")
        except Exception as e:
            logger.error(f"保存insight会话数据失败: {e}")
