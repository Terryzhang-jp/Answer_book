"""
现代化记忆管理服务
实现滑动窗口和消息摘要功能，优化chatbot性能
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langchain.chat_models.base import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from loguru import logger
from core.services.global_storage import global_storage

from config.settings import get_settings


class ModernMemoryService:
    """现代化记忆管理服务"""

    def __init__(self):
        self.settings = get_settings()
        self.checkpointer = MemorySaver()
        # 添加备用存储机制来解决MemorySaver检索问题
        self.backup_storage: Dict[str, List[BaseMessage]] = {}
        self.summary_model = None
        self.conversation_summaries: Dict[str, str] = {}
        self._initialize_summary_model()
        
    def _initialize_summary_model(self):
        """初始化摘要专用模型"""
        try:
            # 使用与主模型相同的初始化方式
            from langchain_google_genai import ChatGoogleGenerativeAI

            # 从settings获取API密钥，而不是直接从环境变量
            api_key = self.settings.GEMINI_API_KEY
            if not api_key:
                logger.warning("GEMINI_API_KEY未设置，摘要功能将不可用")
                self.summary_model = None
                return

            self.summary_model = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
                temperature=0.3,
                max_tokens=1000
            )
            logger.info("摘要模型初始化成功")
        except Exception as e:
            logger.error(f"摘要模型初始化失败: {e}")
            self.summary_model = None
    
    async def process_messages_with_memory(
        self, 
        messages: List[BaseMessage], 
        thread_id: str,
        max_messages: int = 5
    ) -> List[BaseMessage]:
        """
        处理消息并应用记忆管理
        
        Args:
            messages: 原始消息列表
            thread_id: 线程ID
            max_messages: 滑动窗口大小（保留的最近消息数）
            
        Returns:
            处理后的消息列表
        """
        
        if not messages:
            return messages
            
        logger.info(f"处理消息记忆管理，线程ID: {thread_id}, 原始消息数: {len(messages)}")
        
        # 如果消息数量超过阈值，应用摘要策略
        if len(messages) > max_messages * 2:  # 超过10条消息时开始摘要
            processed_messages = await self._apply_sliding_window_with_summary(
                messages, thread_id, max_messages
            )
        else:
            # 直接应用滑动窗口
            processed_messages = self._apply_sliding_window(messages, max_messages)
        
        logger.info(f"记忆管理处理完成，处理后消息数: {len(processed_messages)}")
        return processed_messages

    def get_messages_from_backup(self, thread_id: str) -> List[BaseMessage]:
        """从备用存储获取消息（解决MemorySaver检索问题）"""
        return self.backup_storage.get(thread_id, [])

    def save_messages_to_backup(self, thread_id: str, messages: List[BaseMessage]):
        """保存消息到备用存储"""
        self.backup_storage[thread_id] = messages.copy()
        # 同时保存到全局存储
        global_storage.save_messages(thread_id, messages)
        logger.info(f"备用存储保存成功，线程ID: {thread_id}, 消息数: {len(messages)}")

    def clear_backup_messages(self, thread_id: str) -> bool:
        """清除备用存储中的消息"""
        if thread_id in self.backup_storage:
            del self.backup_storage[thread_id]
            logger.info(f"已清除备用存储中的消息，线程ID: {thread_id}")
            return True
        return False
    
    def _apply_sliding_window(
        self, 
        messages: List[BaseMessage], 
        max_messages: int = 5
    ) -> List[BaseMessage]:
        """
        应用滑动窗口，保留最近N条消息
        
        Args:
            messages: 消息列表
            max_messages: 保留的消息数量
            
        Returns:
            修剪后的消息列表
        """
        
        if len(messages) <= max_messages:
            return messages
            
        try:
            trimmed_messages = trim_messages(
                messages,
                strategy="last",
                max_tokens=max_messages,
                token_counter=len,  # 按消息数量计算
                start_on="human",
                include_system=True,
                allow_partial=False
            )
            
            logger.info(f"滑动窗口应用成功，保留 {len(trimmed_messages)} 条消息")
            return trimmed_messages
            
        except Exception as e:
            logger.error(f"滑动窗口应用失败: {e}")
            # 降级处理：直接返回最后N条消息
            return messages[-max_messages:]
    
    async def _apply_sliding_window_with_summary(
        self, 
        messages: List[BaseMessage], 
        thread_id: str,
        max_messages: int = 5
    ) -> List[BaseMessage]:
        """
        应用滑动窗口并生成摘要
        
        Args:
            messages: 消息列表
            thread_id: 线程ID
            max_messages: 保留的最近消息数
            
        Returns:
            包含摘要的处理后消息列表
        """
        
        # 分离系统消息和对话消息
        system_messages = [msg for msg in messages if isinstance(msg, SystemMessage)]
        conversation_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
        
        if len(conversation_messages) <= max_messages:
            return messages
        
        # 需要摘要的旧消息（除了最近N条）
        old_messages = conversation_messages[:-max_messages]
        recent_messages = conversation_messages[-max_messages:]
        
        # 生成摘要
        summary = await self._generate_summary(old_messages, thread_id)
        
        # 创建摘要消息
        summary_message = SystemMessage(
            content=f"对话历史摘要: {summary}"
        )
        
        # 返回：原系统消息 + 摘要消息 + 最近N条消息
        result = system_messages + [summary_message] + recent_messages
        
        logger.info(f"摘要处理完成，生成摘要长度: {len(summary)} 字符")
        return result
    
    async def _generate_summary(
        self, 
        messages: List[BaseMessage], 
        thread_id: str
    ) -> str:
        """
        使用Gemini 1.5 Flash生成消息摘要
        
        Args:
            messages: 需要摘要的消息列表
            thread_id: 线程ID
            
        Returns:
            生成的摘要文本
        """
        
        if not self.summary_model:
            logger.warning("摘要模型不可用，返回默认摘要")
            return "对话摘要功能暂时不可用"
        
        if not messages:
            return "无对话内容"
        
        # 检查是否已有摘要
        existing_summary = self.conversation_summaries.get(thread_id, "")
        
        # 构建摘要prompt
        messages_text = "\n".join([
            f"{self._get_message_type_name(msg)}: {msg.content}" 
            for msg in messages
        ])
        
        if existing_summary:
            prompt = f"""
现有对话摘要：
{existing_summary}

新的对话内容：
{messages_text}

请更新摘要，保留重要信息和上下文，特别注意：
1. 保留专家身份和角色信息
2. 保留重要的对话主题和结论
3. 保持摘要简洁明了（不超过200字）

更新后的摘要：
"""
        else:
            prompt = f"""
请为以下对话生成简洁的摘要，保留关键信息和上下文：

{messages_text}

摘要要求：
1. 保留专家身份和角色信息
2. 保留重要的对话主题和结论
3. 保持简洁明了（不超过200字）

摘要：
"""
        
        try:
            response = await self.summary_model.ainvoke([
                HumanMessage(content=prompt)
            ])
            
            summary = response.content.strip()
            self.conversation_summaries[thread_id] = summary
            
            logger.info(f"摘要生成成功，线程ID: {thread_id}")
            return summary
            
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return existing_summary or "对话摘要生成失败"
    
    def _get_message_type_name(self, message: BaseMessage) -> str:
        """获取消息类型的中文名称"""
        if isinstance(message, HumanMessage):
            return "用户"
        elif isinstance(message, AIMessage):
            return "助手"
        elif isinstance(message, SystemMessage):
            return "系统"
        else:
            return "其他"
    
    def get_conversation_summary(self, thread_id: str) -> Optional[str]:
        """获取对话摘要"""
        return self.conversation_summaries.get(thread_id)
    
    def clear_conversation_summary(self, thread_id: str) -> bool:
        """清除对话摘要"""
        if thread_id in self.conversation_summaries:
            del self.conversation_summaries[thread_id]
            logger.info(f"已清除线程 {thread_id} 的对话摘要")
            return True
        return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆系统统计信息"""
        return {
            "active_conversations": len(self.conversation_summaries),
            "summary_model_available": self.summary_model is not None,
            "checkpointer_type": type(self.checkpointer).__name__
        }
