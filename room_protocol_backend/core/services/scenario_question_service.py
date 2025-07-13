"""
场景问题生成服务
基于用户对话生成未来场景想象问题
"""

import json
from typing import List, Dict, Any
from loguru import logger
from core.services.llm_service import LLMService
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage


class ScenarioQuestionService:
    """场景问题生成服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        logger.info("场景问题生成服务初始化完成")

    async def _ensure_llm_initialized(self):
        """确保LLM模型已初始化"""
        try:
            # 检查是否已初始化
            self.llm_service.get_model()
        except RuntimeError:
            # 如果未初始化，则初始化
            await self.llm_service.initialize()
            logger.info("LLM模型初始化完成")
    
    async def generate_scenario_question(self, conversation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        基于对话数据生成场景想象问题
        
        Args:
            conversation_data: 对话数据列表
            
        Returns:
            包含场景问题的字典
        """
        try:
            logger.info(f"开始生成场景问题，对话数据条数: {len(conversation_data)}")

            # 确保LLM模型已初始化
            await self._ensure_llm_initialized()

            # 提取用户问题和专家回复
            user_questions = []
            expert_responses = []
            
            for msg in conversation_data:
                if msg.get('type') == 'HumanMessage':
                    user_questions.append(msg.get('content', ''))
                elif msg.get('type') == 'AIMessage':
                    # 尝试解析AI回复中的专家建议
                    try:
                        ai_content = json.loads(msg.get('content', '{}'))
                        if 'character_responses' in ai_content:
                            for expert in ai_content['character_responses']:
                                expert_responses.append({
                                    'expert': expert.get('character_name', ''),
                                    'advice': expert.get('speech', '')
                                })
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，直接使用内容
                        expert_responses.append({
                            'expert': 'AI助手',
                            'advice': msg.get('content', '')
                        })
            
            # 构建提示词
            prompt = self._build_scenario_prompt(user_questions, expert_responses)
            
            # 调用Gemini 2.5 Flash生成问题
            response = await self.llm_service.generate_response_direct([
                HumanMessage(content=prompt)
            ])
            
            # 解析响应
            scenario_data = self._parse_scenario_response(response)
            
            logger.info("场景问题生成成功")
            return scenario_data
            
        except Exception as e:
            logger.error(f"生成场景问题失败: {str(e)}")
            raise Exception(f"场景问题生成失败: {str(e)}")
    
    def _build_scenario_prompt(self, user_questions: List[str], expert_responses: List[Dict[str, str]]) -> str:
        """构建场景问题生成的提示词"""
        
        # 整理用户问题
        questions_text = "\n".join([f"- {q}" for q in user_questions])
        
        # 整理专家建议
        advice_text = ""
        for response in expert_responses:
            advice_text += f"【{response['expert']}】: {response['advice']}\n\n"
        
        prompt = f"""
基于用户的问题，生成一个简短轻松的场景想象问题。

用户的问题：
{questions_text}

专家的建议：
{advice_text}

请生成一个非常简短（1-2句话）的场景问题，让用户轻松想象未来。问题要：
1. 简单直接，不要复杂
2. 让用户随意发挥想象
3. 与用户问题相关

请以JSON格式返回：
{{
    "scenario_question": "简短的场景问题（1-2句话）",
    "context_explanation": "简短说明（1句话）",
    "imagination_guide": "轻松的提示（1句话）"
}}

示例：
{{
    "scenario_question": "想象一下五年后，你的这个问题已经解决了，那时的你过着什么样的生活？",
    "context_explanation": "通过想象未来，帮助你看清内心真正想要的生活。",
    "imagination_guide": "随便说说就好，想到什么就写什么。"
}}
"""
        return prompt
    
    def _parse_scenario_response(self, response: str) -> Dict[str, Any]:
        """解析场景问题响应"""
        try:
            # 清理响应内容
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()
            
            # 解析JSON
            scenario_data = json.loads(cleaned_response)
            
            # 验证必要字段
            required_fields = ['scenario_question', 'context_explanation', 'imagination_guide']
            for field in required_fields:
                if field not in scenario_data:
                    raise ValueError(f"缺少必要字段: {field}")
            
            return scenario_data
            
        except json.JSONDecodeError as e:
            logger.error(f"解析场景问题响应失败: {e}")
            # 返回默认问题
            return {
                "scenario_question": "想象一下五年后，你的问题已经解决了，那时的你过着什么样的生活？",
                "context_explanation": "通过想象未来，帮助你看清内心真正想要的生活。",
                "imagination_guide": "随便说说就好，想到什么就写什么。"
            }
        except Exception as e:
            logger.error(f"处理场景问题响应时出错: {e}")
            raise


# 创建全局实例
scenario_question_service = ScenarioQuestionService()
