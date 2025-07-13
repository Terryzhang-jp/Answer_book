"""
应用配置管理
"""

import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "Room Protocol Backend"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # API配置
    API_V1_STR: str = "/api"
    
    # LLM配置
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # 默认LLM配置
    DEFAULT_MODEL: str = "gemini-2.0-flash-exp"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 4000
    
    # 记忆系统配置
    MEMORY_DIR: str = "memory"

    # 新记忆系统配置
    ENABLE_NEW_MEMORY_SYSTEM: bool = True   # 新记忆系统开关
    MEMORY_SLIDING_WINDOW_SIZE: int = 5     # 滑动窗口大小（保留的最近消息数）
    MEMORY_SUMMARY_MODEL: str = "gemini-1.5-flash"  # 摘要专用模型
    MEMORY_MAX_TOKENS: int = 2000           # 最大token限制
    MEMORY_SUMMARY_THRESHOLD: int = 10      # 开始摘要的消息数阈值
    ENABLE_ASYNC_ANALYSIS: bool = False     # 启用异步对话分析（改为同步以确保前端显示）

    # 会话配置
    SESSION_TIMEOUT: int = 3600  # 1小时
    MAX_SESSIONS: int = 1000
    
    # CORS配置
    CORS_ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"  # 开发环境默认值
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    CORS_ALLOW_HEADERS: str = "Content-Type,Authorization,X-Requested-With,X-API-Key"

    # 认证配置
    ENABLE_AUTH: bool = False  # 认证开关，默认关闭便于开发
    API_KEY: Optional[str] = None  # 主API Key
    API_KEYS: Optional[str] = None  # 多个API Key（逗号分隔）

    # 存储配置
    STORAGE_SHARD_COUNT: int = 100  # 分片数量
    STORAGE_BASE_PATH: str = "data/conversations"  # 存储基础路径
    STORAGE_ENABLE_SHARDING: bool = True  # 是否启用分片存储
    STORAGE_MAX_SHARD_SIZE_MB: int = 10  # 单分片最大大小(MB)

    # 日志配置
    LOG_LEVEL: str = "INFO"

    @property
    def allowed_origins(self) -> list[str]:
        """获取允许的CORS源列表"""
        if self.CORS_ALLOWED_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()
