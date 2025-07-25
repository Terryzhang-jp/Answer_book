"""
管理员API路由
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from core.services.rate_limiter import get_daily_limiter

router = APIRouter()


@router.get("/daily-limit/status")
async def admin_get_daily_limit_status():
    """管理员获取每日限制详细状态"""
    try:
        limiter = get_daily_limiter()
        status = limiter.get_current_status()
        
        return {
            "success": True,
            "data": {
                **status,
                "limiter_config": {
                    "max_daily_conversations": limiter.max_daily_conversations,
                    "data_file": str(limiter.data_file)
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-limit/reset")
async def admin_reset_daily_limit():
    """管理员重置今日对话计数"""
    try:
        limiter = get_daily_limiter()
        success = limiter.reset_daily_count()
        
        if success:
            return {
                "success": True,
                "message": "今日对话计数已重置",
                "data": limiter.get_current_status()
            }
        else:
            return {
                "success": False,
                "message": "今日计数为空，无需重置"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/daily-limit/set-limit")
async def admin_set_daily_limit(new_limit: int):
    """管理员设置每日对话限制数量"""
    try:
        if new_limit <= 0:
            raise HTTPException(status_code=400, detail="限制数量必须大于0")
        
        limiter = get_daily_limiter()
        success = limiter.set_daily_limit(new_limit)
        
        if success:
            return {
                "success": True,
                "message": f"每日对话限制已更新为 {new_limit}",
                "data": limiter.get_current_status()
            }
        else:
            raise HTTPException(status_code=500, detail="设置限制失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
