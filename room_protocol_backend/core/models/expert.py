"""
专家模型定义
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Expert:
    """专家模型"""
    name: str
    category: str
    description: str
    expertise: List[str]
    personality_traits: List[str]
    speaking_style: str
    
    def __str__(self) -> str:
        return f"{self.name} ({self.category})"


@dataclass
class ExpertInteraction:
    """专家交互记录"""
    expert_name: str
    interaction_count: int
    positive_feedback: int
    negative_feedback: int
    last_interaction: str


@dataclass
class ConversationContext:
    """对话上下文"""
    thread_id: str
    user_id: Optional[str]
    current_experts: List[Expert]
    dialogue_mode: str
    message_count: int
    created_at: str
