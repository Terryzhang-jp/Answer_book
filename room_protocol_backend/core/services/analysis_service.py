"""
对话分析服务 - 负责分析对话并生成insights
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from loguru import logger

from core.services.analysis_llm_service import AnalysisLLMService
from core.services.analysis_prompt_service import AnalysisPromptService
from core.schemas.analysis import ConversationAnalysis, ExpertInsight, ConversationEvolution, IncrementalAnalysis
from utils.memory_system import MemorySystem


class AnalysisService:
    """对话分析服务类"""

    def __init__(self):
        self.llm_service = AnalysisLLMService()
        self.prompt_service = AnalysisPromptService()
        self.memory_system = MemorySystem()
    
    async def analyze_conversation_round(
        self,
        thread_id: str,
        user_question: str,
        current_response: dict,
        conversation_history: list,
        all_experts: list,
        user_id: Optional[str] = None,
        previous_analysis: Optional[dict] = None
    ) -> ConversationAnalysis:
        """分析当前对话轮次"""
        try:
            # 构建对话上下文
            conversation_context = self._build_conversation_context(
                conversation_history, current_response
            )

            # 获取精确的专家贡献统计
            expert_contributions = self._get_expert_contributions(user_id, all_experts)

            # 判断是首次分析还是增量分析
            if previous_analysis is None:
                # 首次分析：生成完整分析
                return await self._perform_full_analysis(
                    user_question, conversation_context, all_experts, expert_contributions
                )
            else:
                # 增量分析：基于之前的分析生成增量内容并合并
                return await self._perform_incremental_analysis(
                    user_question, conversation_context, all_experts, expert_contributions, previous_analysis
                )
            
        except Exception as e:
            logger.error(f"对话分析失败 (thread_id: {thread_id}): {e}")
            # 返回默认分析结果，使用精确的贡献统计
            expert_contributions = self._get_expert_contributions(user_id, all_experts)
            return self._create_default_analysis(user_question, all_experts, expert_contributions)
    
    def _build_conversation_context(self, history: list, current_response: dict) -> dict:
        """构建对话上下文"""
        context = {
            "recent_conversations": [],
            "current_round": current_response,
            "early_summary": None
        }
        
        # 获取最近3轮对话
        if len(history) > 6:  # 如果历史超过3轮（每轮2条消息）
            # 取最近3轮
            recent_messages = history[-6:]
            context["recent_conversations"] = self._format_messages(recent_messages)
            
            # 如果历史很长，创建早期摘要
            if len(history) > 10:
                early_messages = history[:-6]
                context["early_summary"] = self._create_early_summary(early_messages)
        else:
            # 历史较短，直接使用全部
            context["recent_conversations"] = self._format_messages(history)
        
        return context
    
    def _format_messages(self, messages: list) -> list:
        """格式化消息列表"""
        formatted = []
        for i in range(0, len(messages), 2):
            if i + 1 < len(messages):
                user_msg = messages[i]
                ai_msg = messages[i + 1]
                formatted.append(f"用户: {user_msg.content}\n回应: {ai_msg.content}")
        return formatted
    
    def _create_early_summary(self, messages: list) -> str:
        """创建早期对话摘要"""
        # 简单的摘要逻辑，可以后续优化
        return f"早期对话包含{len(messages)}条消息，涵盖了多个话题的讨论。"
    
    def _parse_analysis_response(self, response: str) -> dict:
        """解析分析响应"""
        try:
            # 提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)

                # 验证和修复数据
                data = self._validate_and_fix_analysis_data(data)
                return data
            else:
                raise ValueError("未找到有效的JSON格式")

        except Exception as e:
            logger.error(f"解析分析响应失败: {e}")
            raise e

    def _validate_and_fix_analysis_data(self, data: dict) -> dict:
        """验证和修复分析数据"""
        from datetime import datetime

        # 确保必要字段存在
        if "all_experts_insights" not in data:
            data["all_experts_insights"] = []

        if "conversation_timeline" not in data:
            data["conversation_timeline"] = []

        # 修复专家insights中的None值
        for insight in data["all_experts_insights"]:
            if insight.get("last_appearance") is None:
                insight["last_appearance"] = datetime.now().isoformat()
            if insight.get("expert_name") is None:
                insight["expert_name"] = "未知专家"
            if insight.get("total_contributions") is None:
                insight["total_contributions"] = 1
            if insight.get("key_insights") is None:
                insight["key_insights"] = ["分析中..."]
            if insight.get("helpful_points") is None:
                insight["helpful_points"] = ["分析中..."]
            if insight.get("expertise_areas") is None:
                insight["expertise_areas"] = ["待分析"]
            if insight.get("is_current") is None:
                insight["is_current"] = True

        # 修复对话时间线中的None值
        for entry in data["conversation_timeline"]:
            if entry.get("timestamp") is None:
                entry["timestamp"] = datetime.now().isoformat()
            if entry.get("speaker") is None:
                entry["speaker"] = "未知发言者"
            if entry.get("action") is None:
                entry["action"] = "发言"
            if entry.get("content") is None:
                entry["content"] = "内容分析中..."
            if entry.get("round_number") is None:
                entry["round_number"] = 1

        return data

    def _get_expert_contributions(self, user_id: Optional[str], all_experts: list) -> Dict[str, int]:
        """获取精确的专家贡献统计"""
        expert_contributions = {}

        if user_id:
            try:
                # 从内存系统获取专家交互数据
                memory = self.memory_system.load_user_memory(user_id)
                expert_interactions = memory.get("expert_interactions", {})

                for expert_name in all_experts:
                    if expert_name in expert_interactions:
                        expert_contributions[expert_name] = expert_interactions[expert_name].get("interaction_count", 0)
                    else:
                        expert_contributions[expert_name] = 0

                logger.info(f"获取专家贡献统计: {expert_contributions}")
            except Exception as e:
                logger.error(f"获取专家贡献统计失败: {e}")
                # 如果获取失败，使用默认值
                for expert_name in all_experts:
                    expert_contributions[expert_name] = 1
        else:
            # 没有user_id时使用默认值
            for expert_name in all_experts:
                expert_contributions[expert_name] = 1

        return expert_contributions

    def _apply_accurate_contributions(self, analysis_data: dict, expert_contributions: Dict[str, int]) -> dict:
        """使用精确的贡献统计覆盖LLM估算"""
        if "all_experts_insights" in analysis_data:
            for expert_insight in analysis_data["all_experts_insights"]:
                expert_name = expert_insight.get("expert_name")
                if expert_name in expert_contributions:
                    expert_insight["total_contributions"] = expert_contributions[expert_name]
                    logger.info(f"更新专家 {expert_name} 贡献统计: {expert_contributions[expert_name]}")

        return analysis_data

    def _create_default_analysis(self, user_question: str, all_experts: list, expert_contributions: Optional[Dict[str, int]] = None) -> ConversationAnalysis:
        """创建默认分析结果"""
        default_insights = []

        # 如果没有提供贡献统计，使用默认值
        if expert_contributions is None:
            expert_contributions = {expert: 1 for expert in all_experts}

        for expert in all_experts:
            contributions = expert_contributions.get(expert, 1)
            default_insights.append(ExpertInsight(
                expert_name=expert,
                total_contributions=contributions,
                key_insights=["正在分析中..."],
                helpful_points=["专家观点分析中..."],
                expertise_areas=["待分析"],
                last_appearance=datetime.now().isoformat(),
                is_current=True
            ))
        
        return ConversationAnalysis(
            user_question_analysis="问题分析中，请稍后...",
            conversation_timeline=[],
            all_experts_insights=default_insights,
            conversation_evolution=ConversationEvolution(
                topic_progression=["对话进行中"],
                key_turning_points=["分析中"],
                discussion_depth="分析中"
            ),
            suggested_directions=["继续当前讨论"],
            analysis_timestamp=datetime.now().isoformat()
        )

    async def _perform_full_analysis(
        self,
        user_question: str,
        conversation_context: dict,
        all_experts: list,
        expert_contributions: dict
    ) -> ConversationAnalysis:
        """执行完整分析"""
        # 构建分析提示词
        analysis_prompt = self.prompt_service.build_analysis_prompt(
            user_question=user_question,
            conversation_context=conversation_context,
            all_experts=all_experts,
            expert_contributions=expert_contributions
        )

        # 执行分析
        analysis_response = await self.llm_service.analyze_conversation(analysis_prompt)

        # 解析分析结果
        analysis_data = self._parse_analysis_response(analysis_response)

        # 使用精确的贡献统计覆盖LLM估算
        analysis_data = self._apply_accurate_contributions(analysis_data, expert_contributions)

        # 创建分析对象
        return ConversationAnalysis(**analysis_data)

    async def _perform_incremental_analysis(
        self,
        user_question: str,
        conversation_context: dict,
        all_experts: list,
        expert_contributions: dict,
        previous_analysis: dict
    ) -> ConversationAnalysis:
        """执行增量分析并合并到之前的分析中"""
        # 构建增量分析提示词
        incremental_prompt = self.prompt_service.build_incremental_analysis_prompt(
            user_question=user_question,
            new_conversation_context=conversation_context,
            previous_analysis=previous_analysis,
            all_experts=all_experts,
            expert_contributions=expert_contributions
        )

        # 执行增量分析
        incremental_response = await self.llm_service.analyze_conversation(incremental_prompt)

        # 解析增量分析结果
        incremental_data = self._parse_incremental_analysis_response(incremental_response)

        # 合并增量分析到之前的分析中
        merged_analysis = self._merge_incremental_analysis(previous_analysis, incremental_data, expert_contributions)

        return ConversationAnalysis(**merged_analysis)

    def _parse_incremental_analysis_response(self, response: str) -> dict:
        """解析增量分析响应"""
        try:
            # 提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1

            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)

                # 验证和修复增量分析数据
                data = self._validate_and_fix_incremental_data(data)
                return data
            else:
                raise ValueError("未找到有效的JSON格式")

        except Exception as e:
            logger.error(f"解析增量分析响应失败: {e}")
            # 返回空的增量分析
            return {
                "new_timeline_entries": [],
                "expert_insights_updates": [],
                "conversation_evolution_update": None,
                "new_suggested_directions": [],
                "analysis_timestamp": datetime.now().isoformat()
            }

    def _validate_and_fix_incremental_data(self, data: dict) -> dict:
        """验证和修复增量分析数据"""
        from datetime import datetime

        # 确保必要字段存在
        if "new_timeline_entries" not in data:
            data["new_timeline_entries"] = []
        if "expert_insights_updates" not in data:
            data["expert_insights_updates"] = []
        if "new_suggested_directions" not in data:
            data["new_suggested_directions"] = []

        # 修复时间线条目中的None值
        for entry in data["new_timeline_entries"]:
            if entry.get("timestamp") is None:
                entry["timestamp"] = datetime.now().isoformat()
            if entry.get("speaker") is None:
                entry["speaker"] = "未知发言者"
            if entry.get("action") is None:
                entry["action"] = "发言"
            if entry.get("content") is None:
                entry["content"] = "内容分析中..."
            if entry.get("round_number") is None:
                entry["round_number"] = 1

        # 修复专家洞察中的None值
        for insight in data["expert_insights_updates"]:
            if insight.get("last_appearance") is None:
                insight["last_appearance"] = datetime.now().isoformat()
            if insight.get("expert_name") is None:
                insight["expert_name"] = "未知专家"
            if insight.get("total_contributions") is None:
                insight["total_contributions"] = 1
            if insight.get("key_insights") is None:
                insight["key_insights"] = []
            if insight.get("helpful_points") is None:
                insight["helpful_points"] = []
            if insight.get("expertise_areas") is None:
                insight["expertise_areas"] = ["待分析"]
            if insight.get("is_current") is None:
                insight["is_current"] = True

        return data

    def _merge_incremental_analysis(
        self,
        previous_analysis: dict,
        incremental_data: dict,
        expert_contributions: dict
    ) -> dict:
        """合并增量分析到之前的分析中"""
        from datetime import datetime

        # 复制之前的分析作为基础
        merged = previous_analysis.copy()

        # 1. 合并对话时间线（直接追加新条目）
        if "conversation_timeline" not in merged:
            merged["conversation_timeline"] = []

        # 限制时间线长度，保留最近15条
        current_timeline = merged["conversation_timeline"]
        new_entries = incremental_data.get("new_timeline_entries", [])

        # 合并并限制长度
        all_timeline = current_timeline + new_entries
        merged["conversation_timeline"] = all_timeline[-15:]  # 只保留最近15条

        # 2. 合并专家洞察（智能更新）
        if "all_experts_insights" not in merged:
            merged["all_experts_insights"] = []

        # 创建专家名称到洞察的映射
        expert_insights_map = {insight["expert_name"]: insight for insight in merged["all_experts_insights"]}

        # 更新专家洞察
        for new_insight in incremental_data.get("expert_insights_updates", []):
            expert_name = new_insight["expert_name"]

            if expert_name in expert_insights_map:
                # 更新现有专家的洞察
                existing_insight = expert_insights_map[expert_name]

                # 合并核心观点（去重）
                existing_insights = set(existing_insight.get("key_insights", []))
                new_insights = set(new_insight.get("key_insights", []))
                existing_insight["key_insights"] = list(existing_insights | new_insights)

                # 合并帮助要点（去重）
                existing_points = set(existing_insight.get("helpful_points", []))
                new_points = set(new_insight.get("helpful_points", []))
                existing_insight["helpful_points"] = list(existing_points | new_points)

                # 更新其他字段
                existing_insight["total_contributions"] = expert_contributions.get(expert_name, existing_insight.get("total_contributions", 1))
                existing_insight["last_appearance"] = new_insight.get("last_appearance", datetime.now().isoformat())
                existing_insight["is_current"] = new_insight.get("is_current", True)

                # 合并专业领域
                existing_areas = set(existing_insight.get("expertise_areas", []))
                new_areas = set(new_insight.get("expertise_areas", []))
                existing_insight["expertise_areas"] = list(existing_areas | new_areas)
            else:
                # 添加新专家的洞察
                new_insight["total_contributions"] = expert_contributions.get(expert_name, new_insight.get("total_contributions", 1))
                merged["all_experts_insights"].append(new_insight)

        # 3. 更新对话演进
        evolution_update = incremental_data.get("conversation_evolution_update")
        if evolution_update and "conversation_evolution" in merged:
            current_evolution = merged["conversation_evolution"]

            # 合并话题进展
            if "topic_progression" in evolution_update:
                current_progression = current_evolution.get("topic_progression", [])
                new_progression = evolution_update["topic_progression"]
                current_evolution["topic_progression"] = current_progression + new_progression

            # 合并关键转折点
            if "key_turning_points" in evolution_update:
                current_points = current_evolution.get("key_turning_points", [])
                new_points = evolution_update["key_turning_points"]
                current_evolution["key_turning_points"] = current_points + new_points

            # 更新讨论深度
            if "discussion_depth" in evolution_update:
                current_evolution["discussion_depth"] = evolution_update["discussion_depth"]

        # 4. 合并建议方向（追加新建议，限制总数）
        if "suggested_directions" not in merged:
            merged["suggested_directions"] = []

        current_directions = merged["suggested_directions"]
        new_directions = incremental_data.get("new_suggested_directions", [])
        all_directions = current_directions + new_directions

        # 去重并限制数量
        unique_directions = []
        seen = set()
        for direction in all_directions:
            if direction not in seen:
                unique_directions.append(direction)
                seen.add(direction)

        merged["suggested_directions"] = unique_directions[-5:]  # 只保留最近5个建议

        # 5. 更新时间戳
        merged["analysis_timestamp"] = incremental_data.get("analysis_timestamp", datetime.now().isoformat())

        return merged
