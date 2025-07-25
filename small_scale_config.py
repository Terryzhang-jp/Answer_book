# 小范围使用的配置建议

# 1. 环境变量配置
SMALL_SCALE_CONFIG = {
    # API配额控制
    "DAILY_API_LIMIT": 50,  # 每天最多50次API调用
    "MAX_SESSIONS": 20,     # 最多20个活跃会话
    "SESSION_TIMEOUT": 24 * 3600,  # 会话24小时后过期
    
    # 简单的访问控制
    "ALLOWED_IPS": [
        "127.0.0.1",        # 本地访问
        "192.168.1.0/24",   # 局域网访问
        # 添加你的朋友的IP
    ],
    
    # 内容长度限制
    "MAX_QUESTION_LENGTH": 500,    # 问题最长500字符
    "MAX_MESSAGE_LENGTH": 1000,    # 消息最长1000字符
}

# 2. 简单的IP白名单检查
from fastapi import Request, HTTPException
import ipaddress

def check_ip_whitelist(request: Request):
    """简单的IP白名单检查"""
    client_ip = request.client.host
    
    # 开发环境跳过检查
    if client_ip in ["127.0.0.1", "localhost"]:
        return True
    
    # 检查白名单（可选）
    allowed_ips = SMALL_SCALE_CONFIG.get("ALLOWED_IPS", [])
    if allowed_ips:
        for allowed_ip in allowed_ips:
            try:
                if "/" in allowed_ip:  # CIDR格式
                    if ipaddress.ip_address(client_ip) in ipaddress.ip_network(allowed_ip):
                        return True
                else:  # 单个IP
                    if client_ip == allowed_ip:
                        return True
            except:
                continue
        
        # 如果设置了白名单但IP不在其中
        raise HTTPException(status_code=403, detail="访问被拒绝")
    
    return True

# 3. 简单的使用限制
class SimpleRateLimiter:
    def __init__(self):
        self.user_requests = {}  # IP -> (count, last_reset_time)
        self.requests_per_hour = 10  # 每小时最多10次请求
    
    def check_rate_limit(self, client_ip: str):
        current_time = time.time()
        
        if client_ip not in self.user_requests:
            self.user_requests[client_ip] = (1, current_time)
            return True
        
        count, last_reset = self.user_requests[client_ip]
        
        # 每小时重置
        if current_time - last_reset > 3600:
            self.user_requests[client_ip] = (1, current_time)
            return True
        
        if count >= self.requests_per_hour:
            raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
        
        self.user_requests[client_ip] = (count + 1, last_reset)
        return True

# 4. 简单的健康检查
def simple_health_check():
    """简单的系统健康检查"""
    health_info = {
        "status": "healthy",
        "active_sessions": len(chat_histories),
        "memory_usage_mb": get_memory_usage(),
        "uptime_hours": get_uptime_hours(),
    }
    
    # 简单的健康判断
    if health_info["active_sessions"] > 50:
        health_info["status"] = "warning"
        health_info["message"] = "会话数量较多"
    
    if health_info["memory_usage_mb"] > 500:  # 500MB
        health_info["status"] = "warning"
        health_info["message"] = "内存使用较高"
    
    return health_info

import psutil
import time

start_time = time.time()

def get_memory_usage():
    """获取内存使用量（MB）"""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024

def get_uptime_hours():
    """获取运行时间（小时）"""
    return (time.time() - start_time) / 3600