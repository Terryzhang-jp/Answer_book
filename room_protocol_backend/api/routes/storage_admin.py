"""
存储管理API端点
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from loguru import logger

from core.storage.storage_manager import get_storage_manager

router = APIRouter()

@router.get("/storage/stats")
async def get_storage_stats() -> Dict[str, Any]:
    """获取存储统计信息"""
    try:
        storage_manager = get_storage_manager()
        stats = await storage_manager.get_storage_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"获取存储统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取存储统计失败: {str(e)}")

@router.get("/storage/health")
async def storage_health_check() -> Dict[str, Any]:
    """存储系统健康检查"""
    try:
        storage_manager = get_storage_manager()
        health = await storage_manager.health_check()
        
        # 根据健康状态设置HTTP状态码
        if health.get("overall") == "error":
            raise HTTPException(status_code=503, detail="存储系统不健康")
        elif health.get("overall") == "degraded":
            # 部分功能异常，但系统仍可用
            pass
        
        return {
            "success": True,
            "data": health
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"存储健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@router.post("/storage/migrate")
async def migrate_storage() -> Dict[str, Any]:
    """执行存储迁移"""
    try:
        storage_manager = get_storage_manager()
        
        if storage_manager.is_migrated:
            return {
                "success": True,
                "message": "数据已经迁移完成",
                "data": {"already_migrated": True}
            }
        
        success = await storage_manager.migrate_from_legacy()
        
        if success:
            # 验证迁移结果
            verification = await storage_manager.verify_migration()
            
            return {
                "success": True,
                "message": "数据迁移完成",
                "data": {
                    "migration_completed": True,
                    "verification": verification
                }
            }
        else:
            raise HTTPException(status_code=500, detail="数据迁移失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"存储迁移失败: {e}")
        raise HTTPException(status_code=500, detail=f"迁移失败: {str(e)}")

@router.post("/storage/verify")
async def verify_migration() -> Dict[str, Any]:
    """验证迁移结果"""
    try:
        storage_manager = get_storage_manager()
        verification = await storage_manager.verify_migration()
        
        return {
            "success": True,
            "data": verification
        }
    except Exception as e:
        logger.error(f"迁移验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")

@router.post("/storage/optimize")
async def optimize_storage() -> Dict[str, Any]:
    """优化存储性能"""
    try:
        storage_manager = get_storage_manager()
        results = await storage_manager.optimize_storage()
        
        return {
            "success": True,
            "message": "存储优化完成",
            "data": results
        }
    except Exception as e:
        logger.error(f"存储优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")

@router.post("/storage/cleanup-legacy")
async def cleanup_legacy_storage() -> Dict[str, Any]:
    """清理旧存储系统（危险操作）"""
    try:
        storage_manager = get_storage_manager()
        
        if not storage_manager.is_migrated:
            raise HTTPException(
                status_code=400, 
                detail="数据尚未迁移，无法清理旧存储"
            )
        
        success = await storage_manager.cleanup_legacy_storage()
        
        if success:
            return {
                "success": True,
                "message": "旧存储系统清理完成",
                "data": {"cleanup_completed": True}
            }
        else:
            raise HTTPException(status_code=500, detail="清理旧存储失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清理旧存储失败: {e}")
        raise HTTPException(status_code=500, detail=f"清理失败: {str(e)}")

@router.get("/storage/migration-status")
async def get_migration_status() -> Dict[str, Any]:
    """获取迁移状态"""
    try:
        storage_manager = get_storage_manager()
        
        return {
            "success": True,
            "data": {
                "is_migrated": storage_manager.is_migrated,
                "progress": storage_manager.migration_progress,
                "status": "completed" if storage_manager.is_migrated else "pending"
            }
        }
    except Exception as e:
        logger.error(f"获取迁移状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@router.get("/storage/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    try:
        storage_manager = get_storage_manager()
        cache_stats = storage_manager.cache.get_stats()
        metrics = storage_manager.unified_storage.get_metrics()
        
        return {
            "success": True,
            "data": {
                "cache": cache_stats,
                "metrics": metrics.get("cache_stats", {}),
                "hit_rate": metrics.get("cache_hit_rate", 0)
            }
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")

@router.post("/storage/cache/clear")
async def clear_cache() -> Dict[str, Any]:
    """清空缓存"""
    try:
        storage_manager = get_storage_manager()
        await storage_manager.cache.cache.clear()
        
        return {
            "success": True,
            "message": "缓存已清空"
        }
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

@router.post("/storage/cache/warmup")
async def warmup_cache() -> Dict[str, Any]:
    """预热缓存"""
    try:
        storage_manager = get_storage_manager()
        
        # 获取最近的对话ID进行预热
        recent_threads = storage_manager.legacy_storage.get_all_thread_ids()[-100:]
        warmed_count = await storage_manager.unified_storage.warm_up_cache(recent_threads)
        
        return {
            "success": True,
            "message": f"缓存预热完成，预热了 {warmed_count} 个对话",
            "data": {"warmed_count": warmed_count}
        }
    except Exception as e:
        logger.error(f"缓存预热失败: {e}")
        raise HTTPException(status_code=500, detail=f"缓存预热失败: {str(e)}")
