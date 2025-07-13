"""
LLM服务 - 负责与大语言模型的交互
"""

import os
from typing import Optional, Callable
from langchain.chat_models.base import init_chat_model
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from loguru import logger

from config.settings import get_settings


class LLMService:
    """LLM服务类"""
    
    _instance: Optional['LLMService'] = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    async def initialize(cls):
        """初始化LLM模型"""
        instance = cls()
        settings = get_settings()
        
        try:
            # 检查API密钥
            gemini_key = settings.GEMINI_API_KEY
            openai_key = settings.OPENAI_API_KEY
            anthropic_key = settings.ANTHROPIC_API_KEY
            
            # 优先使用Gemini模型
            if gemini_key:
                os.environ["GOOGLE_API_KEY"] = gemini_key
                instance._model = init_chat_model(
                    "gemini-2.5-flash",
                    model_provider="google-genai",
                    temperature=settings.DEFAULT_TEMPERATURE,
                    max_tokens=settings.DEFAULT_MAX_TOKENS
                )
                logger.info("Gemini 2.5 flash模型初始化成功")
            elif openai_key:
                instance._model = init_chat_model(
                    "gpt-4o", 
                    model_provider="openai",
                    temperature=settings.DEFAULT_TEMPERATURE,
                    max_tokens=settings.DEFAULT_MAX_TOKENS
                )
                logger.info("OpenAI模型初始化成功")
            elif anthropic_key:
                instance._model = init_chat_model(
                    "claude-3-5-sonnet-latest", 
                    model_provider="anthropic",
                    temperature=settings.DEFAULT_TEMPERATURE,
                    max_tokens=settings.DEFAULT_MAX_TOKENS
                )
                logger.info("Anthropic模型初始化成功")
            else:
                raise ValueError("未找到有效的API密钥")
                
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            # 尝试备用模型
            try:
                if gemini_key:
                    os.environ["GOOGLE_API_KEY"] = gemini_key
                    instance._model = init_chat_model("gemini-1.5-flash", model_provider="google-genai")
                    logger.info("使用Gemini 1.5 Flash备用模型初始化成功")
                elif openai_key:
                    instance._model = init_chat_model("gpt-4o-mini", model_provider="openai")
                    logger.info("使用OpenAI备用模型初始化成功")
                elif anthropic_key:
                    instance._model = init_chat_model("claude-3-haiku-latest", model_provider="anthropic")
                    logger.info("使用Anthropic备用模型初始化成功")
                else:
                    raise e
            except Exception as e2:
                logger.error(f"备用模型初始化也失败: {e2}")
                raise e2
    
    @classmethod
    def get_model(cls):
        """获取模型实例"""
        instance = cls()
        if instance._model is None:
            raise RuntimeError("LLM模型未初始化，请先调用initialize()")
        return instance._model
    
    @classmethod
    def create_conversation_chain(cls, get_session_history_func: Callable):
        """创建带记忆的对话链"""
        model = cls.get_model()
        return RunnableWithMessageHistory(
            model,
            get_session_history_func,
        )

    @classmethod
    async def generate_response_with_history(cls, messages: list, config: dict, get_session_history_func: Callable) -> str:
        """使用历史记录生成回应"""
        conversation = cls.create_conversation_chain(get_session_history_func)
        try:
            logger.info(f"发送消息到LLM: {len(messages)} 条消息")
            response = await conversation.ainvoke(messages, config)
            logger.info(f"LLM原始响应: {response.content[:200]}...")
            return response.content
        except Exception as e:
            logger.error(f"生成回应失败: {e}")
            raise e

    @classmethod
    async def generate_response(cls, messages: list) -> str:
        """生成回应（保留向后兼容性）"""
        model = cls.get_model()
        try:
            logger.info(f"发送消息到LLM: {len(messages)} 条消息")
            response = await model.ainvoke(messages)
            logger.info(f"LLM原始响应: {response.content[:200]}...")
            return response.content
        except Exception as e:
            logger.error(f"生成回应失败: {e}")
            raise e

    @classmethod
    async def generate_response_direct(cls, messages: list, enable_thinking: bool = True) -> str:
        """直接生成回应（新记忆系统专用，避免历史记录重复发送）"""
        model = cls.get_model()
        try:
            # 计算消息统计
            total_chars = sum(len(msg.get('content', '') if isinstance(msg, dict) else msg.content) for msg in messages)
            estimated_tokens = total_chars // 4  # 粗略估算

            logger.info(f"直接调用LLM: {len(messages)} 条消息, 约 {estimated_tokens} tokens")

            # 如果是Gemini 2.5模型且启用thinking，添加thinking配置
            if enable_thinking and hasattr(model, 'model_name') and '2.5' in str(model.model_name):
                try:
                    # 尝试使用thinking配置（根据LangChain文档）
                    response = await model.ainvoke(
                        messages,
                        config={
                            "thinking_budget": 2048,  # 适中的推理预算
                            "include_thoughts": False  # 暂时不包含思考摘要
                        }
                    )
                    logger.info("使用Thinking模式调用成功")
                except Exception as thinking_error:
                    logger.warning(f"Thinking模式调用失败，回退到普通模式: {thinking_error}")
                    response = await model.ainvoke(messages)
            else:
                response = await model.ainvoke(messages)

            logger.info(f"LLM直接响应: {response.content[:200]}...")
            return response.content
        except Exception as e:
            logger.error(f"直接生成回应失败: {e}")
            raise e
