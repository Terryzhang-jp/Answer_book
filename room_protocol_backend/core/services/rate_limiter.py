"""
每日对话次数限制服务
"""

import json
import os
from datetime import datetime, date
from typing import Dict, Optional
from pathlib import Path
from loguru import logger


class DailyConversationLimiter:
    """每日对话次数限制器"""
    
    def __init__(self, max_daily_conversations: int = 50):
        self.max_daily_conversations = max_daily_conversations
        self.data_file = Path("data/daily_limits.json")
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载现有数据
        self.daily_counts = self._load_data()
        
        logger.info(f"每日对话限制器初始化 - 每日最大对话数: {max_daily_conversations}")
    
    def _load_data(self) -> Dict[str, int]:
        """加载每日计数数据"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 清理过期数据（只保留今天的数据）
                today = date.today().isoformat()
                if today in data:
                    return {today: data[today]}
                    
            return {}
        except Exception as e:
            logger.error(f"加载每日限制数据失败: {e}")
            return {}
    
    def _save_data(self):
        """保存每日计数数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.daily_counts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存每日限制数据失败: {e}")
    
    def _get_today_key(self) -> str:
        """获取今天的日期键"""
        return date.today().isoformat()
    
    def check_and_increment(self) -> tuple[bool, int, int]:
        """
        检查是否可以创建新对话，如果可以则增加计数
        
        Returns:
            tuple[bool, int, int]: (是否允许, 当前次数, 最大次数)
        """
        today = self._get_today_key()
        current_count = self.daily_counts.get(today, 0)
        
        # 检查是否超过限制
        if current_count >= self.max_daily_conversations:
            logger.warning(f"每日对话次数已达上限: {current_count}/{self.max_daily_conversations}")
            return False, current_count, self.max_daily_conversations
        
        # 增加计数
        self.daily_counts[today] = current_count + 1
        self._save_data()
        
        new_count = self.daily_counts[today]
        logger.info(f"对话次数增加: {new_count}/{self.max_daily_conversations}")
        
        return True, new_count, self.max_daily_conversations
    
    def get_current_status(self) -> Dict[str, any]:
        """获取当前限制状态"""
        today = self._get_today_key()
        current_count = self.daily_counts.get(today, 0)
        
        return {
            "date": today,
            "current_count": current_count,
            "max_count": self.max_daily_conversations,
            "remaining": max(0, self.max_daily_conversations - current_count),
            "is_limited": current_count >= self.max_daily_conversations,
            "reset_time": f"{today} 23:59:59"
        }
    
    def reset_daily_count(self) -> bool:
        """重置今日计数（管理员功能）"""
        try:
            today = self._get_today_key()
            if today in self.daily_counts:
                del self.daily_counts[today]
                self._save_data()
                logger.info(f"已重置今日对话计数")
                return True
            return False
        except Exception as e:
            logger.error(f"重置今日计数失败: {e}")
            return False
    
    def set_daily_limit(self, new_limit: int) -> bool:
        """设置每日限制数量（管理员功能）"""
        try:
            if new_limit > 0:
                self.max_daily_conversations = new_limit
                logger.info(f"每日对话限制已更新为: {new_limit}")
                return True
            return False
        except Exception as e:
            logger.error(f"设置每日限制失败: {e}")
            return False


# 全局限制器实例
_daily_limiter: Optional[DailyConversationLimiter] = None

def get_daily_limiter() -> DailyConversationLimiter:
    """获取每日限制器实例（单例模式）"""
    global _daily_limiter
    if _daily_limiter is None:
        _daily_limiter = DailyConversationLimiter()
    return _daily_limiter


# 便捷函数
def check_daily_limit() -> tuple[bool, Dict[str, any]]:
    """
    检查每日限制
    
    Returns:
        tuple[bool, Dict]: (是否允许, 状态信息)
    """
    limiter = get_daily_limiter()
    allowed, current, max_count = limiter.check_and_increment()
    status = limiter.get_current_status()
    
    return allowed, status


def get_daily_status() -> Dict[str, any]:
    """获取每日限制状态（不增加计数）"""
    limiter = get_daily_limiter()
    return limiter.get_current_status()
