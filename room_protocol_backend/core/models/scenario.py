"""
场景问题相关的数据模型
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ScenarioQuestionRequest(BaseModel):
    """场景问题生成请求"""
    thread_id: str
    user_id: str


class ScenarioQuestionData(BaseModel):
    """场景问题数据"""
    scenario_question: str
    context_explanation: str
    imagination_guide: str


class ScenarioQuestionResponse(BaseModel):
    """场景问题响应"""
    success: bool
    question_data: Optional[ScenarioQuestionData] = None
    message: str


class UserScenarioResponse(BaseModel):
    """用户场景回答"""
    thread_id: str
    user_id: str
    scenario_description: str  # 用户对场景的描述


class ScenarioSession(BaseModel):
    """场景问答会话"""
    id: str
    thread_id: str
    user_id: str
    question_data: ScenarioQuestionData
    user_response: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "waiting"  # waiting, completed
