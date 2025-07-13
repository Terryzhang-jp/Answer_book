"""
分析提示词服务 - 构建对话分析的提示词
"""

from typing import List, Dict
from datetime import datetime


class AnalysisPromptService:
    """分析提示词服务类"""
    
    def build_analysis_prompt(
        self,
        user_question: str,
        conversation_context: dict,
        all_experts: list,
        expert_contributions: dict = None
    ) -> str:
        """构建分析提示词"""
        
        prompt = f"""# 对话分析任务

你是一个专业的对话分析师，需要分析用户与专家的对话，提供深入的insights。

## 当前用户问题
{user_question}

## 对话上下文
{self._format_conversation_context(conversation_context)}

## 所有参与过的专家
{self._format_all_experts(all_experts, expert_contributions)}

## 分析要求

请按照以下JSON格式提供分析结果：

```json
{{
    "user_question_analysis": "对用户问题的深入分析，包括问题的核心、背景和意图",
    "conversation_timeline": [
        {{
            "speaker": "专家名称或'用户'",
            "action": "提出观点/赞同/质疑/补充/总结等",
            "content": "精简摘要，1句话概括核心要点，不超过30字",
            "timestamp": "时间戳",
            "round_number": 轮次数
        }}
    ],
    "all_experts_insights": [
        {{
            "expert_name": "专家名称",
            "total_contributions": 贡献轮次数,
            "key_insights": ["核心观点1", "核心观点2", "核心观点3", "...更多观点"],
            "helpful_points": ["可帮助用户的要点1", "可帮助用户的要点2", "...更多要点"],
            "expertise_areas": ["专业领域1", "专业领域2"],
            "last_appearance": "最后出现时间",
            "is_current": true/false
        }}
    ],
    "conversation_evolution": {{
        "topic_progression": ["话题演进1", "话题演进2"],
        "key_turning_points": ["转折点1", "转折点2"],
        "discussion_depth": "讨论深度评估"
    }},
    "suggested_directions": ["建议方向1", "建议方向2"],
    "analysis_timestamp": "{datetime.now().isoformat()}"
}}
```

## 分析重点

1. **对话时间线纪要**: 按时间顺序记录每个发言者的关键观点和行动
   - 记录专家的核心观点、立场、论证
   - 记录专家之间的互动（赞同、反驳、补充）
   - 记录用户的问题、质疑、回应
   - **重要**: content字段必须是精简摘要，每个发言者每轮最多1句话，不超过30字
   - 完整对话已在中间板块展示，这里只保留最核心的观点精华

2. **专家贡献分析**: 每个专家的独特价值和观点
   - **不限制核心观点数量**：尽可能完整地记录专家的所有重要观点
   - 包括专家的独特视角和方法论

3. **对话演进**: 话题如何发展和深化
4. **实用建议**: 基于专家insights为用户提供具体帮助
5. **历史专家**: 包括已切换的专家的贡献

## 对话时间线示例

```
第1轮：专家A提出X基础理论
第1轮：专家B补充Y实践案例
第2轮：用户质疑Z观点缺乏W因素
第2轮：专家A解释W因素处理
第2轮：专家B强调V重要性
```

**注意**: 每个content字段都应该是精简的1句话摘要，不超过30字，突出核心要点。

请确保分析深入、准确，并提供实用的insights。"""

        return prompt

    def build_incremental_analysis_prompt(
        self,
        user_question: str,
        new_conversation_context: dict,
        previous_analysis: dict,
        all_experts: list,
        expert_contributions: dict
    ) -> str:
        """构建增量分析提示词"""
        from datetime import datetime

        prompt = f"""# 对话增量分析任务

你是一个专业的对话分析师。现在需要你对最新一轮的对话进行增量分析。

## 任务说明

**重要**：你只需要分析最新一轮的对话内容，不要重新分析之前的内容。
之前的分析结果已经保存，你只需要提供新增的分析内容。

## 之前的分析结果

```json
{previous_analysis}
```

## 最新一轮对话内容

**用户问题**: {user_question}

**对话上下文**:
{self._format_conversation_context(new_conversation_context)}

## 专家贡献统计
{self._format_expert_contributions(expert_contributions)}

## 输出要求

请按照以下JSON格式提供**增量分析结果**：

```json
{{
    "new_timeline_entries": [
        {{
            "speaker": "专家名称或'用户'",
            "action": "提出观点/赞同/质疑/补充/总结等",
            "content": "精简摘要，1句话概括核心要点，不超过30字",
            "timestamp": "{datetime.now().isoformat()}",
            "round_number": 当前轮次数
        }}
    ],
    "expert_insights_updates": [
        {{
            "expert_name": "专家名称",
            "total_contributions": 贡献轮次数,
            "key_insights": ["新增的核心观点1", "新增的核心观点2"],
            "helpful_points": ["新增的可帮助用户的要点1", "新增的可帮助用户的要点2"],
            "expertise_areas": ["专业领域1", "专业领域2"],
            "last_appearance": "{datetime.now().isoformat()}",
            "is_current": true/false
        }}
    ],
    "conversation_evolution_update": {{
        "topic_progression": ["新的话题演进"],
        "key_turning_points": ["新的转折点"],
        "discussion_depth": "讨论深度评估更新"
    }},
    "new_suggested_directions": ["新的建议方向1", "新的建议方向2"],
    "analysis_timestamp": "{datetime.now().isoformat()}"
}}
```

## 分析重点

1. **新增时间线条目**: 只记录本轮对话中的关键观点和互动
   - **重要**: content字段必须是精简摘要，每个发言者每轮最多1句话，不超过30字
   - 完整对话已在中间板块展示，这里只保留最核心的观点精华
2. **专家洞察更新**: 只更新参与本轮对话的专家的洞察
3. **话题演进**: 只记录本轮对话带来的新发展
4. **建议方向**: 基于本轮对话提出的新建议

**注意**: 不要重复之前已经分析过的内容，专注于新增价值。
"""

        return prompt
    
    def _format_conversation_context(self, context: dict) -> str:
        """格式化对话上下文"""
        formatted = ""
        
        if context.get("early_summary"):
            formatted += f"### 早期对话摘要\n{context['early_summary']}\n\n"
        
        if context.get("recent_conversations"):
            formatted += "### 最近对话\n"
            for i, conv in enumerate(context["recent_conversations"]):
                formatted += f"**轮次{i+1}**: {conv}\n"
            formatted += "\n"
        
        if context.get("current_round"):
            formatted += f"### 当前轮次\n{context['current_round']}\n"
        
        return formatted
    
    def _format_all_experts(self, experts: list, expert_contributions: dict = None) -> str:
        """格式化所有专家信息"""
        if not experts:
            return "暂无专家信息"

        formatted = ""
        for expert in experts:
            if expert_contributions and expert in expert_contributions:
                contributions = expert_contributions[expert]
                formatted += f"- {expert} (已贡献 {contributions} 轮对话)\n"
            else:
                formatted += f"- {expert}\n"

        return formatted

    def _format_expert_contributions(self, expert_contributions: dict) -> str:
        """格式化专家贡献统计"""
        if not expert_contributions:
            return "暂无专家贡献统计"

        formatted = []
        for expert_name, count in expert_contributions.items():
            formatted.append(f"- {expert_name}: {count} 轮贡献")

        return "\n".join(formatted)
