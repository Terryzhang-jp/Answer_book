"""
内存缓存实现 - L1缓存层
"""

import time
from typing import Any, Optional, Dict, List
from collections import OrderedDict
from langchain_core.messages import BaseMessage
from loguru import logger

from .storage_interface import CacheInterface


class LRUCache(CacheInterface):
    """LRU内存缓存实现"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._ttls: Dict[str, float] = {}
        
        logger.info(f"LRU缓存初始化 - 最大容量: {max_size}, 默认TTL: {default_ttl}秒")
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        # 检查是否过期
        if self._is_expired(key):
            await self.delete(key)
            return None
        
        if key in self._cache:
            # 移动到末尾（最近使用）
            value = self._cache.pop(key)
            self._cache[key] = value
            self._timestamps[key] = time.time()
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        try:
            # 如果key已存在，先删除
            if key in self._cache:
                del self._cache[key]
            
            # 检查容量限制
            while len(self._cache) >= self.max_size:
                # 删除最久未使用的项
                oldest_key = next(iter(self._cache))
                await self.delete(oldest_key)
            
            # 添加新项
            self._cache[key] = value
            self._timestamps[key] = time.time()
            
            # 设置TTL
            if ttl is not None:
                self._ttls[key] = time.time() + ttl
            else:
                self._ttls[key] = time.time() + self.default_ttl
            
            logger.debug(f"缓存设置成功 - key: {key}, 当前大小: {len(self._cache)}")
            return True
            
        except Exception as e:
            logger.error(f"缓存设置失败 - key: {key}, 错误: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._timestamps:
                del self._timestamps[key]
            if key in self._ttls:
                del self._ttls[key]
            return True
        except Exception as e:
            logger.error(f"缓存删除失败 - key: {key}, 错误: {e}")
            return False
    
    async def clear(self) -> bool:
        """清空所有缓存"""
        try:
            self._cache.clear()
            self._timestamps.clear()
            self._ttls.clear()
            logger.info("缓存已清空")
            return True
        except Exception as e:
            logger.error(f"缓存清空失败: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        if self._is_expired(key):
            await self.delete(key)
            return False
        return key in self._cache
    
    def _is_expired(self, key: str) -> bool:
        """检查key是否过期"""
        if key not in self._ttls:
            return False
        return time.time() > self._ttls[key]
    
    async def cleanup_expired(self) -> int:
        """清理过期项"""
        expired_keys = []
        current_time = time.time()
        
        for key, expire_time in self._ttls.items():
            if current_time > expire_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        if expired_keys:
            logger.debug(f"清理过期缓存项: {len(expired_keys)}个")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "usage_rate": len(self._cache) / self.max_size,
            "oldest_item_age": time.time() - min(self._timestamps.values()) if self._timestamps else 0
        }


class ConversationCache:
    """对话专用缓存"""
    
    def __init__(self, max_conversations: int = 500, messages_per_conversation: int = 10):
        self.max_conversations = max_conversations
        self.messages_per_conversation = messages_per_conversation
        self.cache = LRUCache(max_size=max_conversations)
        
        logger.info(f"对话缓存初始化 - 最大对话数: {max_conversations}, 每对话消息数: {messages_per_conversation}")
    
    async def get_messages(self, thread_id: str) -> Optional[List[BaseMessage]]:
        """获取对话消息"""
        return await self.cache.get(f"messages:{thread_id}")
    
    async def set_messages(self, thread_id: str, messages: List[BaseMessage]) -> bool:
        """设置对话消息（只缓存最近的N条）"""
        # 只缓存最近的消息
        recent_messages = messages[-self.messages_per_conversation:] if len(messages) > self.messages_per_conversation else messages
        return await self.cache.set(f"messages:{thread_id}", recent_messages)
    
    async def delete_conversation(self, thread_id: str) -> bool:
        """删除对话缓存"""
        return await self.cache.delete(f"messages:{thread_id}")
    
    async def get_conversation_info(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """获取对话信息"""
        return await self.cache.get(f"info:{thread_id}")
    
    async def set_conversation_info(self, thread_id: str, info: Dict[str, Any]) -> bool:
        """设置对话信息"""
        return await self.cache.set(f"info:{thread_id}", info)
    
    async def cleanup(self) -> int:
        """清理过期缓存"""
        return await self.cache.cleanup_expired()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        base_stats = self.cache.get_stats()
        return {
            **base_stats,
            "max_conversations": self.max_conversations,
            "messages_per_conversation": self.messages_per_conversation
        }
