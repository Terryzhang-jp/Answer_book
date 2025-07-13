"""
Insight相关数据模型
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class InsightRequest(BaseModel):
    """Insight生成请求模型"""
    user_id: str = Field(..., description="用户ID")
    thread_id: str = Field(..., description="对话线程ID")
    user_context: Optional[Dict[str, Any]] = Field(default=None, description="用户上下文信息")


class InsightResponse(BaseModel):
    """Insight生成响应模型"""
    success: bool
    session_id: Optional[str] = None
    insight: str = Field(default="", description="生成的一句话insight")
    analysis_summary: Optional[str] = Field(default=None, description="分析摘要")
    message: Optional[str] = None


class InsightSessionData(BaseModel):
    """Insight会话数据"""
    session_id: str
    user_id: str
    thread_id: str
    insight: str
    analysis_data: Dict[str, Any] = Field(default={})
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(default="completed")  # completed, failed
    metadata: Dict[str, Any] = Field(default={})


class ConversationData(BaseModel):
    """对话数据结构"""
    user_questions: list[str] = Field(default=[])
    guest_responses: list[Dict[str, str]] = Field(default=[])
    conversation_context: str = Field(default="")
    total_messages: int = Field(default=0)
