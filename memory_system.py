"""
持久化记忆系统 - 记住用户偏好和对话历史
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class UserPreference:
    """用户偏好"""
    preferred_experts: List[str]  # 偏好的专家
    avoided_experts: List[str]    # 不喜欢的专家
    favorite_topics: List[str]    # 感兴趣的话题
    dialogue_style: str           # 偏好的对话风格 (formal/casual/debate)
    last_updated: str

@dataclass
class ConversationMemory:
    """对话记忆"""
    topic: str
    experts_involved: List[str]
    key_insights: List[str]
    user_satisfaction: Optional[int]  # 1-5评分
    timestamp: str

@dataclass
class ExpertInteraction:
    """专家交互记忆"""
    expert_name: str
    interaction_count: int
    positive_feedback: int
    negative_feedback: int
    last_interaction: str

class MemorySystem:
    """记忆系统"""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
    def _get_user_id(self, session_info: str) -> str:
        """生成用户ID（基于IP或session）"""
        return hashlib.md5(session_info.encode()).hexdigest()[:8]
    
    def _get_user_file(self, user_id: str) -> str:
        """获取用户记忆文件路径"""
        return os.path.join(self.memory_dir, f"user_{user_id}.json")
    
    def load_user_memory(self, user_id: str) -> Dict:
        """加载用户记忆"""
        file_path = self._get_user_file(user_id)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载用户记忆失败: {e}")
        
        # 返回默认记忆结构
        return {
            "preferences": {
                "preferred_experts": [],
                "avoided_experts": [],
                "favorite_topics": [],
                "dialogue_style": "balanced",
                "last_updated": datetime.now().isoformat()
            },
            "conversation_history": [],
            "expert_interactions": {},
            "total_conversations": 0,
            "created_at": datetime.now().isoformat()
        }
    
    def save_user_memory(self, user_id: str, memory: Dict):
        """保存用户记忆"""
        file_path = self._get_user_file(user_id)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存用户记忆失败: {e}")
    
    def update_expert_interaction(self, user_id: str, expert_name: str, feedback: str = "neutral"):
        """更新专家交互记忆"""
        memory = self.load_user_memory(user_id)
        
        if expert_name not in memory["expert_interactions"]:
            memory["expert_interactions"][expert_name] = {
                "interaction_count": 0,
                "positive_feedback": 0,
                "negative_feedback": 0,
                "last_interaction": datetime.now().isoformat()
            }
        
        interaction = memory["expert_interactions"][expert_name]
        interaction["interaction_count"] += 1
        interaction["last_interaction"] = datetime.now().isoformat()
        
        if feedback == "positive":
            interaction["positive_feedback"] += 1
        elif feedback == "negative":
            interaction["negative_feedback"] += 1
        
        self.save_user_memory(user_id, memory)
    
    def add_conversation_memory(self, user_id: str, topic: str, experts: List[str], insights: List[str] = None):
        """添加对话记忆"""
        memory = self.load_user_memory(user_id)
        
        conversation = {
            "topic": topic,
            "experts_involved": experts,
            "key_insights": insights or [],
            "user_satisfaction": None,
            "timestamp": datetime.now().isoformat()
        }
        
        memory["conversation_history"].append(conversation)
        memory["total_conversations"] += 1
        
        # 只保留最近50次对话
        if len(memory["conversation_history"]) > 50:
            memory["conversation_history"] = memory["conversation_history"][-50:]
        
        # 更新专家交互
        for expert in experts:
            self.update_expert_interaction(user_id, expert)
        
        self.save_user_memory(user_id, memory)
    
    def update_user_preferences(self, user_id: str, preferred_experts: List[str] = None, 
                              avoided_experts: List[str] = None, topics: List[str] = None):
        """更新用户偏好"""
        memory = self.load_user_memory(user_id)
        
        if preferred_experts:
            memory["preferences"]["preferred_experts"] = list(set(
                memory["preferences"]["preferred_experts"] + preferred_experts
            ))
        
        if avoided_experts:
            memory["preferences"]["avoided_experts"] = list(set(
                memory["preferences"]["avoided_experts"] + avoided_experts
            ))
        
        if topics:
            memory["preferences"]["favorite_topics"] = list(set(
                memory["preferences"]["favorite_topics"] + topics
            ))
        
        memory["preferences"]["last_updated"] = datetime.now().isoformat()
        self.save_user_memory(user_id, memory)
    
    def get_expert_recommendations(self, user_id: str, topic: str = None) -> List[str]:
        """基于记忆推荐专家"""
        memory = self.load_user_memory(user_id)
        
        # 获取偏好专家
        preferred = memory["preferences"]["preferred_experts"]
        avoided = memory["preferences"]["avoided_experts"]
        
        # 基于交互历史评分专家
        expert_scores = {}
        for expert, interaction in memory["expert_interactions"].items():
            if expert in avoided:
                continue
                
            score = interaction["positive_feedback"] - interaction["negative_feedback"]
            score += interaction["interaction_count"] * 0.1  # 交互次数加分
            expert_scores[expert] = score
        
        # 排序并返回推荐
        recommended = sorted(expert_scores.items(), key=lambda x: x[1], reverse=True)
        return [expert for expert, score in recommended[:5]] + preferred
    
    def get_memory_context(self, user_id: str) -> str:
        """获取记忆上下文，用于增强prompt"""
        memory = self.load_user_memory(user_id)
        
        context_parts = []
        
        # 用户偏好
        if memory["preferences"]["preferred_experts"]:
            context_parts.append(f"用户偏好的专家: {', '.join(memory['preferences']['preferred_experts'])}")
        
        if memory["preferences"]["avoided_experts"]:
            context_parts.append(f"用户不喜欢的专家: {', '.join(memory['preferences']['avoided_experts'])}")
        
        if memory["preferences"]["favorite_topics"]:
            context_parts.append(f"用户感兴趣的话题: {', '.join(memory['preferences']['favorite_topics'])}")
        
        # 最近对话历史
        recent_conversations = memory["conversation_history"][-3:]  # 最近3次对话
        if recent_conversations:
            topics = [conv["topic"] for conv in recent_conversations]
            context_parts.append(f"最近讨论的话题: {', '.join(topics)}")
        
        # 专家交互统计
        top_experts = []
        for expert, interaction in memory["expert_interactions"].items():
            if interaction["interaction_count"] >= 2:  # 至少交互2次
                score = interaction["positive_feedback"] - interaction["negative_feedback"]
                if score > 0:
                    top_experts.append(expert)
        
        if top_experts:
            context_parts.append(f"用户评价较好的专家: {', '.join(top_experts[:3])}")
        
        return "\n".join(context_parts) if context_parts else "新用户，无历史记忆"

# 全局记忆系统实例
memory_system = MemorySystem()
