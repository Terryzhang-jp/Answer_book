"""
统一存储接口定义
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class ConversationStorageInterface(ABC):
    """对话存储接口"""
    
    @abstractmethod
    async def save_messages(self, thread_id: str, messages: List[BaseMessage]) -> bool:
        """保存消息到存储"""
        pass
    
    @abstractmethod
    async def get_messages(self, thread_id: str, limit: Optional[int] = None) -> List[BaseMessage]:
        """从存储获取消息"""
        pass
    
    @abstractmethod
    async def get_recent_messages(self, thread_id: str, count: int = 5) -> List[BaseMessage]:
        """获取最近的N条消息"""
        pass
    
    @abstractmethod
    async def delete_conversation(self, thread_id: str) -> bool:
        """删除整个对话"""
        pass
    
    @abstractmethod
    async def list_conversations(self, user_id: Optional[str] = None) -> List[str]:
        """列出对话ID"""
        pass
    
    @abstractmethod
    async def get_conversation_info(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """获取对话基本信息"""
        pass


class CacheInterface(ABC):
    """缓存接口"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """清空所有缓存"""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        pass


class StorageMetrics:
    """存储指标"""
    
    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.storage_reads = 0
        self.storage_writes = 0
        self.errors = 0
    
    @property
    def cache_hit_rate(self) -> float:
        """缓存命中率"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.cache_misses += 1
    
    def record_storage_read(self):
        """记录存储读取"""
        self.storage_reads += 1
    
    def record_storage_write(self):
        """记录存储写入"""
        self.storage_writes += 1
    
    def record_error(self):
        """记录错误"""
        self.errors += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hit_rate,
            "storage_reads": self.storage_reads,
            "storage_writes": self.storage_writes,
            "errors": self.errors
        }
