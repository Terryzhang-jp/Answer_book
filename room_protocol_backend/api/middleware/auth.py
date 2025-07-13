"""
认证中间件
"""

import os
from typing import List, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from config.settings import get_settings
from loguru import logger


class AuthMiddleware(BaseHTTPMiddleware):
    """API认证中间件"""
    
    def __init__(self, app, enabled: bool = True):
        super().__init__(app)
        self.enabled = enabled
        self.settings = get_settings()
        
        # 白名单路径（不需要认证的端点）
        self.whitelist_paths = [
            "/api/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        # 开发环境额外白名单
        if self.settings.DEBUG:
            self.whitelist_paths.extend([
                "/api/test/memory-system",
                "/api/test/performance-compare"
            ])
    
    async def dispatch(self, request: Request, call_next):
        """处理请求认证"""
        
        # 如果认证未启用，直接通过
        if not self.enabled:
            return await call_next(request)
        
        # 检查是否在白名单中
        if self._is_whitelisted(request.url.path):
            return await call_next(request)
        
        # 执行认证检查
        try:
            self._authenticate_request(request)
        except HTTPException as e:
            # 返回认证失败响应
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": {
                        "code": "AUTHENTICATION_FAILED",
                        "message": e.detail,
                        "timestamp": self._get_timestamp()
                    }
                }
            )
        
        # 认证通过，继续处理请求
        response = await call_next(request)
        return response
    
    def _is_whitelisted(self, path: str) -> bool:
        """检查路径是否在白名单中"""
        for whitelist_path in self.whitelist_paths:
            if path.startswith(whitelist_path):
                return True
        return False
    
    def _authenticate_request(self, request: Request) -> None:
        """认证请求"""
        
        # 获取认证头
        auth_header = request.headers.get("Authorization")
        api_key_header = request.headers.get("X-API-Key")
        
        # 检查API Key认证
        if api_key_header:
            if self._validate_api_key(api_key_header):
                logger.debug(f"API Key认证成功: {request.url.path}")
                return
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的API Key"
                )
        
        # 检查Bearer Token认证
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # 移除 "Bearer " 前缀
            if self._validate_bearer_token(token):
                logger.debug(f"Bearer Token认证成功: {request.url.path}")
                return
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="无效的Bearer Token"
                )
        
        # 没有提供认证信息
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="缺少认证信息。请提供API Key (X-API-Key头) 或 Bearer Token (Authorization头)"
        )
    
    def _validate_api_key(self, api_key: str) -> bool:
        """验证API Key"""
        valid_keys = self._get_valid_api_keys()
        return api_key in valid_keys
    
    def _validate_bearer_token(self, token: str) -> bool:
        """验证Bearer Token"""
        # 目前使用与API Key相同的验证逻辑
        # 未来可以扩展为JWT验证
        return self._validate_api_key(token)
    
    def _get_valid_api_keys(self) -> List[str]:
        """获取有效的API Key列表"""
        keys = []
        
        # 从环境变量获取
        env_key = os.getenv("API_KEY")
        if env_key:
            keys.append(env_key)
        
        # 从配置获取多个key（逗号分隔）
        config_keys = os.getenv("API_KEYS", "")
        if config_keys:
            keys.extend([key.strip() for key in config_keys.split(",") if key.strip()])
        
        # 开发环境默认key
        if self.settings.DEBUG and not keys:
            keys.append("dev-api-key-12345")
            logger.warning("使用开发环境默认API Key，生产环境请设置环境变量")
        
        return keys
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()


class OptionalAuthMiddleware(AuthMiddleware):
    """可选认证中间件（用于渐进式部署）"""
    
    def __init__(self, app):
        # 从环境变量读取是否启用认证
        enabled = os.getenv("ENABLE_AUTH", "false").lower() == "true"
        super().__init__(app, enabled=enabled)
        
        if enabled:
            logger.info("API认证已启用")
        else:
            logger.info("API认证已禁用（可通过ENABLE_AUTH=true启用）")


# 便捷的认证检查函数（用于手动认证检查）
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = None) -> Optional[str]:
    """获取当前用户（用于依赖注入）"""
    if not credentials:
        return None
    
    # 这里可以扩展为更复杂的用户验证逻辑
    # 目前只是简单的token验证
    middleware = AuthMiddleware(None)
    if middleware._validate_bearer_token(credentials.credentials):
        return "authenticated_user"
    
    return None
