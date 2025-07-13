"""
对话相关的数据模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """提问请求模型"""
    question: str = Field(..., description="用户问题", min_length=1, max_length=1000)
    user_id: Optional[str] = Field(None, description="用户ID")
    thread_id: Optional[str] = Field(None, description="对话线程ID，如果提供则继续现有对话")


class ContinueRequest(BaseModel):
    """继续对话请求模型"""
    thread_id: str = Field(..., description="对话线程ID")
    user_id: Optional[str] = Field(None, description="用户ID")


class MemberChange(BaseModel):
    """成员变更模型"""
    action: str = Field(..., description="变更行动: invite|remove|none")
    old_expert: Optional[str] = Field(None, description="被移除的专家名称")
    new_expert: Optional[str] = Field(None, description="新邀请的专家名称")
    reason: Optional[str] = Field(None, description="变更原因")


class CharacterResponse(BaseModel):
    """角色回应模型"""
    character_name: str = Field(..., description="角色名称")
    character_role: str = Field(..., description="角色类型: system|expert_1|expert_2")
    thinking: str = Field(..., description="内心思考过程")
    speaking: str = Field(..., description="外在发言")
    body_language: str = Field(..., description="肢体语言描述")


class AnswerResponse(BaseModel):
    """回答响应模型"""
    room_announcement: Optional[str] = Field(None, description="房间宣告")
    character_responses: List[CharacterResponse] = Field(..., description="角色回应列表")
    dialogue_mode: str = Field(..., description="对话模式: single|free_dialogue")
    next_action: str = Field(..., description="下一步行动")
    thread_id: str = Field(..., description="对话线程ID")
    timestamp: str = Field(..., description="时间戳")
    member_change: Optional[MemberChange] = Field(None, description="成员变更信息")
    conversation_analysis: Optional[dict] = Field(None, description="对话分析结果")


class SessionInfo(BaseModel):
    """会话信息模型"""
    thread_id: str = Field(..., description="线程ID")
    message_count: int = Field(..., description="消息数量")
    created_at: str = Field(..., description="创建时间")


class SessionListResponse(BaseModel):
    """会话列表响应模型"""
    sessions: List[SessionInfo] = Field(..., description="会话列表")


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="状态")
    timestamp: str = Field(..., description="时间戳")
    version: str = Field(..., description="版本号")
