"""
存储管理器 - 统一管理所有存储操作
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from .conversation_storage import UnifiedConversationStorage
from .memory_cache import ConversationCache
from ..services.global_storage import GlobalStorage


class StorageManager:
    """存储管理器 - 统一管理和监控所有存储操作"""
    
    def __init__(self):
        self.unified_storage = UnifiedConversationStorage()
        self.legacy_storage = GlobalStorage()
        self.cache = ConversationCache()
        
        # 运行状态
        self.is_migrated = False
        self.migration_progress = 0.0
        
        logger.info("存储管理器初始化完成")
    
    async def migrate_from_legacy(self) -> bool:
        """从旧存储系统迁移到新系统"""
        try:
            logger.info("开始从旧存储系统迁移数据...")
            
            # 获取所有旧数据
            all_thread_ids = self.legacy_storage.get_all_thread_ids()
            total_threads = len(all_thread_ids)
            
            if total_threads == 0:
                logger.info("没有需要迁移的数据")
                self.is_migrated = True
                return True
            
            migrated_count = 0
            
            for i, thread_id in enumerate(all_thread_ids):
                try:
                    # 从旧存储获取消息
                    messages = self.legacy_storage.get_messages(thread_id)
                    
                    if messages:
                        # 保存到新存储
                        await self.unified_storage.save_messages(thread_id, messages)
                        migrated_count += 1
                    
                    # 更新进度
                    self.migration_progress = (i + 1) / total_threads
                    
                    if (i + 1) % 100 == 0:
                        logger.info(f"迁移进度: {i + 1}/{total_threads} ({self.migration_progress:.1%})")
                
                except Exception as e:
                    logger.error(f"迁移线程 {thread_id} 失败: {e}")
            
            self.is_migrated = True
            logger.info(f"数据迁移完成 - 成功: {migrated_count}/{total_threads}")
            return True
            
        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            return False
    
    async def verify_migration(self) -> Dict[str, Any]:
        """验证迁移结果"""
        try:
            # 获取旧存储数据统计
            legacy_threads = self.legacy_storage.get_all_thread_ids()
            legacy_count = len(legacy_threads)
            
            # 获取新存储数据统计
            new_threads = await self.unified_storage.list_conversations()
            new_count = len(new_threads)
            
            # 抽样验证数据一致性
            sample_size = min(10, legacy_count)
            sample_threads = legacy_threads[:sample_size]
            
            consistent_count = 0
            for thread_id in sample_threads:
                legacy_messages = self.legacy_storage.get_messages(thread_id)
                new_messages = await self.unified_storage.get_messages(thread_id)
                
                if len(legacy_messages) == len(new_messages):
                    consistent_count += 1
            
            verification_result = {
                "legacy_thread_count": legacy_count,
                "new_thread_count": new_count,
                "count_match": legacy_count == new_count,
                "sample_size": sample_size,
                "consistent_samples": consistent_count,
                "consistency_rate": consistent_count / sample_size if sample_size > 0 else 1.0,
                "verification_passed": legacy_count == new_count and consistent_count == sample_size
            }
            
            logger.info(f"迁移验证结果: {verification_result}")
            return verification_result
            
        except Exception as e:
            logger.error(f"迁移验证失败: {e}")
            return {"verification_passed": False, "error": str(e)}
    
    async def cleanup_legacy_storage(self) -> bool:
        """清理旧存储系统（谨慎操作）"""
        if not self.is_migrated:
            logger.warning("数据尚未迁移，拒绝清理旧存储")
            return False
        
        try:
            # 验证迁移结果
            verification = await self.verify_migration()
            if not verification.get("verification_passed", False):
                logger.warning("迁移验证未通过，拒绝清理旧存储")
                return False
            
            # 备份旧存储文件
            import shutil
            from pathlib import Path
            
            backup_dir = Path("backup") / f"legacy_storage_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # 备份旧存储文件
            old_file = Path("memory/global_backup_storage.json")
            if old_file.exists():
                shutil.copy2(old_file, backup_dir / "global_backup_storage.json")
                logger.info(f"旧存储文件已备份到: {backup_dir}")
            
            # 清理内存中的旧数据
            self.legacy_storage._backup_storage.clear()
            self.legacy_storage._thread_timestamps.clear()
            
            logger.info("旧存储系统清理完成")
            return True
            
        except Exception as e:
            logger.error(f"清理旧存储失败: {e}")
            return False
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计信息"""
        try:
            # 统一存储统计
            unified_metrics = self.unified_storage.get_metrics()
            
            # 缓存统计
            cache_stats = self.cache.get_stats()
            
            # 旧存储统计
            legacy_threads = self.legacy_storage.get_all_thread_ids()
            
            return {
                "unified_storage": unified_metrics,
                "cache": cache_stats,
                "legacy_storage": {
                    "thread_count": len(legacy_threads),
                    "memory_usage_mb": len(str(self.legacy_storage._backup_storage)) / 1024 / 1024
                },
                "migration": {
                    "is_migrated": self.is_migrated,
                    "progress": self.migration_progress
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取存储统计失败: {e}")
            return {"error": str(e)}
    
    async def optimize_storage(self) -> Dict[str, Any]:
        """优化存储性能"""
        try:
            results = {}
            
            # 清理过期缓存
            expired_count = await self.unified_storage.cleanup_cache()
            results["cache_cleanup"] = {"expired_items": expired_count}
            
            # 预热热门数据
            recent_threads = self.legacy_storage.get_all_thread_ids()[-100:]  # 最近100个对话
            warmed_count = await self.unified_storage.warm_up_cache(recent_threads)
            results["cache_warmup"] = {"warmed_items": warmed_count}
            
            # 文件系统优化（如果需要）
            # TODO: 实现分片文件的合并和优化
            
            logger.info(f"存储优化完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"存储优化失败: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """存储系统健康检查"""
        try:
            health_status = {
                "overall": "healthy",
                "components": {},
                "timestamp": datetime.now().isoformat()
            }
            
            # 检查统一存储
            try:
                test_messages = await self.unified_storage.get_messages("health_check_test")
                health_status["components"]["unified_storage"] = "healthy"
            except Exception as e:
                health_status["components"]["unified_storage"] = f"error: {e}"
                health_status["overall"] = "degraded"
            
            # 检查缓存
            try:
                await self.cache.cache.set("health_check", "test")
                test_value = await self.cache.cache.get("health_check")
                if test_value == "test":
                    health_status["components"]["cache"] = "healthy"
                else:
                    health_status["components"]["cache"] = "error: cache test failed"
                    health_status["overall"] = "degraded"
                await self.cache.cache.delete("health_check")
            except Exception as e:
                health_status["components"]["cache"] = f"error: {e}"
                health_status["overall"] = "degraded"
            
            # 检查文件存储
            try:
                from pathlib import Path
                storage_path = Path("data/conversations")
                if storage_path.exists() and storage_path.is_dir():
                    shard_files = list(storage_path.glob("shard_*.json"))
                    health_status["components"]["file_storage"] = {
                        "status": "healthy",
                        "shard_count": len(shard_files)
                    }
                else:
                    health_status["components"]["file_storage"] = "error: storage directory not found"
                    health_status["overall"] = "degraded"
            except Exception as e:
                health_status["components"]["file_storage"] = f"error: {e}"
                health_status["overall"] = "degraded"
            
            return health_status
            
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "overall": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# 全局存储管理器实例
_storage_manager: Optional[StorageManager] = None

def get_storage_manager() -> StorageManager:
    """获取存储管理器实例（单例模式）"""
    global _storage_manager
    if _storage_manager is None:
        _storage_manager = StorageManager()
    return _storage_manager
