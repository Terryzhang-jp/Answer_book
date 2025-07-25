# 小范围使用的简单改进建议

# 1. 添加简单的会话清理机制
import time
from threading import Timer

class SimpleSessionManager:
    def __init__(self, cleanup_interval=3600):  # 1小时清理一次
        self.cleanup_interval = cleanup_interval
        self.start_cleanup_timer()
    
    def start_cleanup_timer(self):
        """启动定时清理"""
        Timer(self.cleanup_interval, self.cleanup_old_sessions).start()
    
    def cleanup_old_sessions(self):
        """清理超过24小时的会话"""
        current_time = time.time()
        sessions_to_remove = []
        
        for session_id, history in chat_histories.items():
            # 简单的时间检查（可以改进）
            if len(history.messages) == 0:  # 空会话直接删除
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del chat_histories[session_id]
        
        print(f"清理了 {len(sessions_to_remove)} 个空会话")
        self.start_cleanup_timer()  # 重新启动定时器

# 2. 添加简单的使用统计
class SimpleStats:
    def __init__(self):
        self.total_requests = 0
        self.total_sessions = 0
        self.api_calls = 0
    
    def log_request(self):
        self.total_requests += 1
    
    def log_api_call(self):
        self.api_calls += 1
    
    def get_stats(self):
        return {
            "total_requests": self.total_requests,
            "active_sessions": len(chat_histories),
            "api_calls": self.api_calls
        }

# 3. 添加简单的错误重试
import time
from functools import wraps

def simple_retry(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    print(f"重试 {attempt + 1}/{max_retries}: {str(e)}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# 4. 添加简单的配额提醒
class SimpleQuotaMonitor:
    def __init__(self, daily_limit=100):
        self.daily_limit = daily_limit
        self.daily_count = 0
        self.last_reset = time.time()
    
    def check_quota(self):
        # 每天重置计数
        if time.time() - self.last_reset > 86400:  # 24小时
            self.daily_count = 0
            self.last_reset = time.time()
        
        if self.daily_count >= self.daily_limit:
            raise Exception(f"今日API调用已达上限 ({self.daily_limit})")
        
        self.daily_count += 1
        
        # 接近限制时提醒
        if self.daily_count > self.daily_limit * 0.8:
            print(f"警告: 今日API调用已达 {self.daily_count}/{self.daily_limit}")