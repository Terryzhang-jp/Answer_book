"""
对话分析相关数据模型
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ExpertInsight(BaseModel):
    """专家洞察模型"""
    expert_name: str = Field(..., description="专家名称")
    total_contributions: int = Field(..., description="总贡献轮次")
    key_insights: List[str] = Field(..., description="核心观点")
    helpful_points: List[str] = Field(..., description="可帮助用户的要点")
    expertise_areas: List[str] = Field(..., description="专业领域")
    last_appearance: str = Field(..., description="最后出现时间")
    is_current: bool = Field(..., description="是否当前专家")


class ConversationEvolution(BaseModel):
    """对话演进模型"""
    topic_progression: List[str] = Field(..., description="话题演进")
    key_turning_points: List[str] = Field(..., description="关键转折点")
    discussion_depth: str = Field(..., description="讨论深度评估")

class ConversationTimelineEntry(BaseModel):
    """对话时间线条目"""
    speaker: str = Field(..., description="发言者（专家名称或'用户'）")
    action: str = Field(..., description="行动描述")
    content: str = Field(..., description="具体内容")
    timestamp: str = Field(..., description="时间戳")
    round_number: int = Field(..., description="对话轮次")


class IncrementalAnalysis(BaseModel):
    """增量分析结果模型"""
    new_timeline_entries: List[ConversationTimelineEntry] = Field(default_factory=list, description="新增的时间线条目")
    expert_insights_updates: List[ExpertInsight] = Field(default_factory=list, description="专家洞察更新")
    conversation_evolution_update: Optional[ConversationEvolution] = Field(None, description="对话演进更新")
    new_suggested_directions: List[str] = Field(default_factory=list, description="新的建议方向")
    analysis_timestamp: str = Field(..., description="分析时间戳")

class ConversationAnalysis(BaseModel):
    """对话分析结果模型"""
    user_question_analysis: str = Field(..., description="用户问题分析")
    expert_selection_reason: Optional[str] = Field(None, description="专家邀请理由")
    conversation_timeline: List[ConversationTimelineEntry] = Field(default_factory=list, description="对话时间线纪要")
    all_experts_insights: List[ExpertInsight] = Field(..., description="所有专家insights")
    conversation_evolution: ConversationEvolution = Field(..., description="对话演进分析")
    suggested_directions: List[str] = Field(..., description="建议的后续方向")
    analysis_timestamp: str = Field(..., description="分析时间戳")
