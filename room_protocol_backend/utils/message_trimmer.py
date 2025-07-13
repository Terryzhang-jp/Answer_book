"""
消息处理工具类
提供消息修剪、分类和优化处理功能
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from loguru import logger


class MessageTrimmer:
    """消息修剪工具类"""
    
    def __init__(self, max_tokens: int = 2000):
        """
        初始化消息修剪器
        
        Args:
            max_tokens: 最大token数量限制
        """
        self.max_tokens = max_tokens
    
    def trim_by_count(
        self, 
        messages: List[BaseMessage], 
        max_count: int = 5,
        preserve_system: bool = True
    ) -> List[BaseMessage]:
        """
        按消息数量修剪
        
        Args:
            messages: 消息列表
            max_count: 保留的最大消息数量
            preserve_system: 是否保留系统消息
            
        Returns:
            修剪后的消息列表
        """
        
        if not messages:
            return messages
            
        try:
            trimmed = trim_messages(
                messages,
                strategy="last",
                max_tokens=max_count,
                token_counter=len,  # 使用消息数量作为token计数
                start_on="human",
                include_system=preserve_system,
                allow_partial=False
            )
            
            logger.debug(f"按数量修剪: {len(messages)} -> {len(trimmed)} 条消息")
            return trimmed
            
        except Exception as e:
            logger.error(f"按数量修剪失败: {e}")
            # 降级处理
            return self._fallback_trim_by_count(messages, max_count, preserve_system)
    
    def trim_by_tokens(
        self, 
        messages: List[BaseMessage], 
        max_tokens: Optional[int] = None,
        preserve_system: bool = True
    ) -> List[BaseMessage]:
        """
        按token数量修剪
        
        Args:
            messages: 消息列表
            max_tokens: 最大token数量，默认使用初始化时的值
            preserve_system: 是否保留系统消息
            
        Returns:
            修剪后的消息列表
        """
        
        if not messages:
            return messages
            
        token_limit = max_tokens or self.max_tokens
        
        try:
            trimmed = trim_messages(
                messages,
                strategy="last",
                max_tokens=token_limit,
                token_counter=count_tokens_approximately,
                start_on="human",
                include_system=preserve_system,
                allow_partial=False
            )
            
            logger.debug(f"按token修剪: {len(messages)} -> {len(trimmed)} 条消息")
            return trimmed
            
        except Exception as e:
            logger.error(f"按token修剪失败: {e}")
            # 降级处理
            return self._fallback_trim_by_count(messages, 5, preserve_system)
    
    def _fallback_trim_by_count(
        self, 
        messages: List[BaseMessage], 
        max_count: int,
        preserve_system: bool
    ) -> List[BaseMessage]:
        """
        降级处理：简单的按数量修剪
        
        Args:
            messages: 消息列表
            max_count: 保留的最大消息数量
            preserve_system: 是否保留系统消息
            
        Returns:
            修剪后的消息列表
        """
        
        if preserve_system:
            # 分离系统消息和其他消息
            system_messages = [msg for msg in messages if isinstance(msg, SystemMessage)]
            other_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
            
            # 保留最后的max_count条非系统消息
            trimmed_others = other_messages[-max_count:] if len(other_messages) > max_count else other_messages
            
            return system_messages + trimmed_others
        else:
            # 直接保留最后max_count条消息
            return messages[-max_count:] if len(messages) > max_count else messages
    
    def categorize_messages(self, messages: List[BaseMessage]) -> Dict[str, List[BaseMessage]]:
        """
        对消息进行分类
        
        Args:
            messages: 消息列表
            
        Returns:
            分类后的消息字典
        """
        
        categorized = {
            "system": [],
            "human": [],
            "ai": [],
            "other": []
        }
        
        for message in messages:
            if isinstance(message, SystemMessage):
                categorized["system"].append(message)
            elif isinstance(message, HumanMessage):
                categorized["human"].append(message)
            elif isinstance(message, AIMessage):
                categorized["ai"].append(message)
            else:
                categorized["other"].append(message)
        
        return categorized
    
    def extract_expert_context(self, messages: List[BaseMessage]) -> Dict[str, Any]:
        """
        从消息中提取专家上下文信息
        
        Args:
            messages: 消息列表
            
        Returns:
            专家上下文信息
        """
        
        expert_context = {
            "current_experts": [],
            "expert_changes": [],
            "room_announcements": []
        }
        
        for message in messages:
            if isinstance(message, AIMessage):
                try:
                    # 尝试解析AI消息中的JSON内容
                    import json
                    content = message.content
                    
                    # 简单的JSON检测和解析
                    if content.strip().startswith('{') and content.strip().endswith('}'):
                        data = json.loads(content)
                        
                        # 提取专家信息
                        if "character_responses" in data:
                            for char in data["character_responses"]:
                                expert_name = char.get("character_name", "")
                                expert_role = char.get("character_role", "")
                                if expert_name and expert_name not in expert_context["current_experts"]:
                                    expert_context["current_experts"].append(expert_name)
                        
                        # 提取房间宣告
                        if "room_announcement" in data:
                            announcement = data["room_announcement"]
                            if announcement and announcement not in expert_context["room_announcements"]:
                                expert_context["room_announcements"].append(announcement)
                                
                except (json.JSONDecodeError, KeyError):
                    # 如果解析失败，跳过
                    continue
        
        return expert_context
    
    def optimize_for_context_window(
        self, 
        messages: List[BaseMessage],
        target_tokens: int = 1500
    ) -> Tuple[List[BaseMessage], Dict[str, Any]]:
        """
        为上下文窗口优化消息列表
        
        Args:
            messages: 原始消息列表
            target_tokens: 目标token数量
            
        Returns:
            优化后的消息列表和优化信息
        """
        
        if not messages:
            return messages, {"optimization": "no_messages"}
        
        # 提取专家上下文
        expert_context = self.extract_expert_context(messages)
        
        # 按token修剪
        optimized_messages = self.trim_by_tokens(messages, target_tokens)
        
        # 计算优化统计
        optimization_info = {
            "original_count": len(messages),
            "optimized_count": len(optimized_messages),
            "reduction_ratio": 1 - (len(optimized_messages) / len(messages)) if messages else 0,
            "expert_context": expert_context,
            "target_tokens": target_tokens
        }
        
        logger.info(f"消息优化完成: {len(messages)} -> {len(optimized_messages)} 条消息")
        
        return optimized_messages, optimization_info


class ExpertContextPreserver:
    """专家上下文保持器"""
    
    def __init__(self):
        self.expert_memory: Dict[str, Dict[str, Any]] = {}
    
    def preserve_expert_info(self, thread_id: str, expert_context: Dict[str, Any]):
        """
        保存专家信息
        
        Args:
            thread_id: 线程ID
            expert_context: 专家上下文信息
        """
        
        self.expert_memory[thread_id] = {
            "experts": expert_context.get("current_experts", []),
            "last_announcement": expert_context.get("room_announcements", [])[-1] if expert_context.get("room_announcements") else "",
            "timestamp": logger._core.now().isoformat()
        }
    
    def get_expert_info(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        获取专家信息
        
        Args:
            thread_id: 线程ID
            
        Returns:
            专家信息或None
        """
        
        return self.expert_memory.get(thread_id)
    
    def create_expert_context_message(self, thread_id: str) -> Optional[SystemMessage]:
        """
        创建专家上下文消息
        
        Args:
            thread_id: 线程ID
            
        Returns:
            包含专家上下文的系统消息
        """
        
        expert_info = self.get_expert_info(thread_id)
        if not expert_info:
            return None
        
        experts = expert_info.get("experts", [])
        last_announcement = expert_info.get("last_announcement", "")
        
        if not experts and not last_announcement:
            return None
        
        context_content = "当前对话上下文:\n"
        
        if experts:
            context_content += f"当前专家: {', '.join(experts)}\n"
        
        if last_announcement:
            context_content += f"最近房间宣告: {last_announcement}\n"
        
        return SystemMessage(content=context_content)


# 全局实例
message_trimmer = MessageTrimmer()
expert_context_preserver = ExpertContextPreserver()
