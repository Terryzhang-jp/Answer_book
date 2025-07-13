"""
信件生成服务
基于新的信件协议生成给用户的信
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any
from loguru import logger
from langchain_core.messages import HumanMessage

from core.services.llm_service import LLMService


class LetterGenerator:
    """信件生成器"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.protocol_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "..", "config", "letter_protocol.md"
        )
        logger.info("信件生成器初始化完成")
    
    def _load_protocol(self) -> str:
        """加载信件协议"""
        try:
            with open(self.protocol_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"加载信件协议失败: {e}")
            return ""
    
    def _extract_conversation_content(self, conversation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """提取对话内容"""
        user_questions = []
        expert_responses = []
        scenario_description = None
        
        for msg in conversation_data:
            content = msg.get('content', '')
            msg_type = msg.get('type', '')
            
            if msg_type == 'HumanMessage':
                if "我想象的未来场景：" in content:
                    scenario_description = content.replace("我想象的未来场景：", "").strip()
                elif content.strip() and not content.startswith("你是一个"):  # 排除系统消息
                    user_questions.append(content.strip())
            elif msg_type == 'AIMessage':
                # 尝试解析AI回复中的专家建议
                try:
                    ai_data = json.loads(content)
                    if 'character_responses' in ai_data:
                        for expert in ai_data['character_responses']:
                            expert_responses.append({
                                'expert': expert.get('character_name', ''),
                                'advice': expert.get('speech', '')
                            })
                    else:
                        # 如果不是JSON格式，直接使用内容
                        expert_responses.append({
                            'expert': 'AI助手',
                            'advice': content
                        })
                except json.JSONDecodeError:
                    # 如果不是JSON格式，直接使用内容
                    expert_responses.append({
                        'expert': 'AI助手',
                        'advice': content
                    })
        
        return {
            'user_questions': user_questions,
            'expert_responses': expert_responses,
            'scenario_description': scenario_description
        }
    
    def _build_letter_prompt(self, conversation_content: Dict[str, Any], protocol: str) -> str:
        """构建信件生成提示词"""
        user_questions = conversation_content['user_questions']
        expert_responses = conversation_content['expert_responses']
        scenario_description = conversation_content['scenario_description']
        
        # 整理用户问题
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(user_questions)])
        
        # 整理专家建议
        advice_text = ""
        for response in expert_responses:
            advice_text += f"【{response['expert']}】: {response['advice']}\n\n"
        
        # 场景描述部分
        scenario_text = ""
        if scenario_description:
            scenario_text = f"\n用户的场景描述：\n{scenario_description}\n"
        
        prompt = f"""
请严格按照以下协议为用户生成一封信。

{protocol}

用户的对话内容：

用户的问题：
{questions_text}

专家的回答：
{advice_text}
{scenario_text}

请严格按照协议要求，生成一封完整的信件。注意：
1. 必须包含完整的信件格式（标题、称呼、正文六个部分、结尾、落款、日期）
2. 语气要温暖、理解、像朋友一样
3. 内容要有深度，体现协议中的六个分析部分
4. 如果有场景描述，要自然地融入到信中
5. 落款必须是"答案之书"
6. 日期使用今天的日期

请直接输出完整的信件内容，不要添加任何其他说明。
"""
        return prompt
    
    def _build_insufficient_content_prompt(self) -> str:
        """构建内容不足时的提示词"""
        return """
请生成一封简短的信，告诉用户对话内容还不够充分，需要更多交流才能生成有价值的分析。

格式要求：
- 标题：来自答案之书的一封信
- 称呼：亲爱的朋友：
- 内容：温和地说明需要更多对话内容
- 落款：答案之书
- 日期：今天的日期

语气要温暖友善，不要让用户感到被拒绝。
"""
    
    async def generate_letter(self, conversation_data: List[Dict[str, Any]]) -> str:
        """生成信件"""
        try:
            logger.info(f"开始生成信件，对话数据条数: {len(conversation_data)}")
            
            # 确保LLM模型已初始化
            try:
                self.llm_service.get_model()
            except RuntimeError:
                await self.llm_service.initialize()
                logger.info("LLM模型初始化完成")
            
            # 提取对话内容
            conversation_content = self._extract_conversation_content(conversation_data)
            
            # 检查内容是否充分
            user_questions_count = len(conversation_content['user_questions'])
            expert_responses_count = len(conversation_content['expert_responses'])
            
            if user_questions_count < 3 or expert_responses_count < 3:
                logger.info(f"对话内容不足，生成简短回复 - 用户问题: {user_questions_count}, 专家回复: {expert_responses_count}")
                prompt = self._build_insufficient_content_prompt()
            else:
                # 加载协议
                protocol = self._load_protocol()
                if not protocol:
                    raise Exception("无法加载信件协议")
                
                # 构建提示词
                prompt = self._build_letter_prompt(conversation_content, protocol)
            
            # 调用Gemini 2.5 Pro生成信件
            response = await self.llm_service.generate_response_direct([
                HumanMessage(content=prompt)
            ])
            
            # 清理响应
            letter_content = response.strip()
            if letter_content.startswith("```"):
                # 移除可能的markdown标记
                lines = letter_content.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                letter_content = '\n'.join(lines)
            
            logger.info("信件生成成功")
            return letter_content
            
        except Exception as e:
            logger.error(f"生成信件失败: {str(e)}")
            # 返回默认信件
            current_date = datetime.now().strftime("%Y年%m月%d日")
            return f"""来自答案之书的一封信

亲爱的朋友：

很抱歉，在生成你的专属信件时遇到了一些技术问题。但我想告诉你，每一个寻求答案的人都值得被认真对待。

请稍后再试，或者继续与专家们深入交流，我会为你准备一份更好的回复。

此致
敬礼

答案之书
{current_date}"""


# 创建全局实例
letter_generator = LetterGenerator()
