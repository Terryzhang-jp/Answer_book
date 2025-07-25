"""
统一对话存储实现 - 整合L1缓存、L2文件存储和L3 Supabase存储
"""

import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
from loguru import logger

from .storage_interface import ConversationStorageInterface, StorageMetrics
from .memory_cache import ConversationCache
from ..services.global_storage import GlobalStorage
from config.settings import get_settings


class UnifiedConversationStorage(ConversationStorageInterface):
    """统一对话存储 - L1缓存 + L2文件存储 + L3 Supabase存储"""

    def __init__(self, enable_cache: bool = True):
        self.settings = get_settings()
        self.enable_cache = enable_cache
        self.cache = ConversationCache() if enable_cache else None
        self.file_storage = GlobalStorage()
        self.metrics = StorageMetrics()

        # 初始化Supabase存储（如果启用）
        self.supabase_storage = None
        if self.settings.ENABLE_SUPABASE_STORAGE:
            try:
                from .supabase_storage import SupabaseStorage
                self.supabase_storage = SupabaseStorage()
                logger.info("✅ Supabase存储已启用")
            except Exception as e:
                logger.warning(f"⚠️ Supabase存储初始化失败: {e}")
                self.supabase_storage = None

        logger.info(f"统一对话存储初始化 - 缓存启用: {enable_cache}, Supabase启用: {self.supabase_storage is not None}")
    
    async def save_messages(self, thread_id: str, messages: List[BaseMessage]) -> bool:
        """保存消息 - L1缓存 + L2文件存储 + L3 Supabase存储"""
        try:
            # L2: 写入文件存储（主存储）
            self.file_storage.save_messages(thread_id, messages)
            self.metrics.record_storage_write()

            # L3: 写入Supabase存储（如果启用）
            if self.supabase_storage:
                try:
                    await self.supabase_storage.save_messages(thread_id, messages)
                    logger.debug(f"Supabase存储保存成功 - thread_id: {thread_id}")
                except Exception as e:
                    logger.warning(f"Supabase存储保存失败 - thread_id: {thread_id}, 错误: {e}")
                    # Supabase失败不影响整体保存流程

            # L1: 写入缓存
            if self.enable_cache and self.cache:
                await self.cache.set_messages(thread_id, messages)

                # 更新对话信息
                info = {
                    "thread_id": thread_id,
                    "message_count": len(messages),
                    "last_updated": datetime.now().isoformat(),
                    "last_message": messages[-1].content[:100] if messages else ""
                }
                await self.cache.set_conversation_info(thread_id, info)

            logger.debug(f"消息保存成功 - thread_id: {thread_id}, 消息数: {len(messages)}")
            return True

        except Exception as e:
            self.metrics.record_error()
            logger.error(f"消息保存失败 - thread_id: {thread_id}, 错误: {e}")
            return False
    
    async def get_messages(self, thread_id: str, limit: Optional[int] = None) -> List[BaseMessage]:
        """获取消息 - L1缓存 → L2文件存储 → L3 Supabase存储"""
        try:
            messages = []

            # L1: 先尝试从缓存获取
            if self.enable_cache and self.cache:
                messages = await self.cache.get_messages(thread_id)
                if messages:
                    self.metrics.record_cache_hit()
                    logger.debug(f"L1缓存命中 - thread_id: {thread_id}, 消息数: {len(messages)}")

                    # 如果需要更多消息，从文件存储补充
                    if limit and len(messages) < limit:
                        file_messages = self.file_storage.get_messages(thread_id)
                        if len(file_messages) > len(messages):
                            messages = file_messages
                            self.metrics.record_storage_read()
                else:
                    self.metrics.record_cache_miss()

            # L2: 如果缓存未命中，从文件存储获取
            if not messages:
                messages = self.file_storage.get_messages(thread_id)
                self.metrics.record_storage_read()
                logger.debug(f"L2文件存储获取 - thread_id: {thread_id}, 消息数: {len(messages)}")

                # 将数据加载到缓存
                if self.enable_cache and self.cache and messages:
                    await self.cache.set_messages(thread_id, messages)

            # L3: 如果文件存储也没有，尝试从Supabase获取
            if not messages and self.supabase_storage:
                try:
                    messages = await self.supabase_storage.get_messages(thread_id)
                    if messages:
                        logger.debug(f"L3 Supabase存储获取 - thread_id: {thread_id}, 消息数: {len(messages)}")

                        # 回写到文件存储和缓存
                        self.file_storage.save_messages(thread_id, messages)
                        if self.enable_cache and self.cache:
                            await self.cache.set_messages(thread_id, messages)
                except Exception as e:
                    logger.warning(f"Supabase存储获取失败 - thread_id: {thread_id}, 错误: {e}")
            
            # 应用limit限制
            if limit and len(messages) > limit:
                messages = messages[-limit:]
            
            logger.debug(f"消息获取成功 - thread_id: {thread_id}, 消息数: {len(messages)}")
            return messages
            
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"消息获取失败 - thread_id: {thread_id}, 错误: {e}")
            return []
    
    async def get_recent_messages(self, thread_id: str, count: int = 5) -> List[BaseMessage]:
        """获取最近的N条消息"""
        messages = await self.get_messages(thread_id)
        return messages[-count:] if len(messages) > count else messages
    
    async def delete_conversation(self, thread_id: str) -> bool:
        """删除对话 - 同时删除缓存和文件存储"""
        try:
            # 删除文件存储
            self.file_storage.clear_thread(thread_id)
            
            # 删除缓存
            if self.enable_cache and self.cache:
                await self.cache.delete_conversation(thread_id)
            
            logger.info(f"对话删除成功 - thread_id: {thread_id}")
            return True
            
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"对话删除失败 - thread_id: {thread_id}, 错误: {e}")
            return False
    
    async def list_conversations(self, user_id: Optional[str] = None) -> List[str]:
        """列出对话ID"""
        try:
            # 从文件存储获取所有对话ID
            thread_ids = self.file_storage.get_all_thread_ids()
            
            # TODO: 如果需要按user_id过滤，需要额外的索引机制
            # 目前返回所有thread_ids
            
            logger.debug(f"对话列表获取成功 - 数量: {len(thread_ids)}")
            return thread_ids
            
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"对话列表获取失败: {e}")
            return []
    
    async def get_conversation_info(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """获取对话基本信息"""
        try:
            # 先尝试从缓存获取
            if self.enable_cache and self.cache:
                info = await self.cache.get_conversation_info(thread_id)
                if info:
                    self.metrics.record_cache_hit()
                    return info
                else:
                    self.metrics.record_cache_miss()
            
            # 从文件存储构建信息
            messages = self.file_storage.get_messages(thread_id)
            if messages:
                info = {
                    "thread_id": thread_id,
                    "message_count": len(messages),
                    "last_updated": datetime.now().isoformat(),
                    "last_message": messages[-1].content[:100] if messages else ""
                }
                
                # 缓存信息
                if self.enable_cache and self.cache:
                    await self.cache.set_conversation_info(thread_id, info)
                
                return info
            
            return None
            
        except Exception as e:
            self.metrics.record_error()
            logger.error(f"对话信息获取失败 - thread_id: {thread_id}, 错误: {e}")
            return None
    
    async def cleanup_cache(self) -> int:
        """清理过期缓存"""
        if self.enable_cache and self.cache:
            return await self.cache.cleanup()
        return 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取存储指标"""
        base_metrics = self.metrics.get_stats()
        
        if self.enable_cache and self.cache:
            cache_stats = self.cache.get_stats()
            base_metrics.update({
                "cache_stats": cache_stats
            })
        
        return base_metrics
    
    async def warm_up_cache(self, thread_ids: List[str]) -> int:
        """预热缓存"""
        if not self.enable_cache or not self.cache:
            return 0
        
        warmed_count = 0
        for thread_id in thread_ids:
            try:
                messages = self.file_storage.get_messages(thread_id)
                if messages:
                    await self.cache.set_messages(thread_id, messages)
                    warmed_count += 1
            except Exception as e:
                logger.warning(f"缓存预热失败 - thread_id: {thread_id}, 错误: {e}")
        
        logger.info(f"缓存预热完成 - 成功: {warmed_count}/{len(thread_ids)}")
        return warmed_count


# 全局统一存储实例
_unified_storage: Optional[UnifiedConversationStorage] = None

def get_unified_storage() -> UnifiedConversationStorage:
    """获取统一存储实例（单例模式）"""
    global _unified_storage
    if _unified_storage is None:
        _unified_storage = UnifiedConversationStorage()
    return _unified_storage
