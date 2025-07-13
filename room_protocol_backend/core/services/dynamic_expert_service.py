"""
动态专家选择服务 - 根据问题内容智能选择最合适的专家
"""

import json
from typing import List, Dict, Any
from core.services.llm_service import LLMService
from loguru import logger


class DynamicExpertService:
    """动态专家选择服务"""
    
    def __init__(self):
        self.llm_service = LLMService()
        logger.info("动态专家选择服务初始化完成")
    
    async def select_experts_for_question(self, user_question: str, user_id: str = None) -> Dict[str, Any]:
        """
        根据用户问题动态选择最合适的专家
        
        Args:
            user_question: 用户的问题
            user_id: 用户ID（可选，用于个性化推荐）
            
        Returns:
            包含专家信息的字典
        """
        try:
            logger.info(f"开始为问题选择专家: {user_question[:100]}...")
            
            # 构建专家选择提示词
            selection_prompt = self._build_expert_selection_prompt(user_question)
            
            # 确保LLM已初始化
            try:
                LLMService.get_model()
            except RuntimeError:
                await LLMService.initialize()

            # 调用LLM进行专家选择
            response = await self.llm_service.generate_response_direct([
                {"role": "system", "content": selection_prompt},
                {"role": "user", "content": f"用户问题：{user_question}"}
            ])
            
            # 解析响应
            expert_selection = self._parse_expert_selection(response)
            
            logger.info(f"专家选择完成: {[expert['name'] for expert in expert_selection['experts']]}")
            return expert_selection
            
        except Exception as e:
            logger.error(f"动态专家选择失败: {e}")
            # 返回默认专家作为备选
            return self._get_fallback_experts()
    
    def _build_expert_selection_prompt(self, user_question: str) -> str:
        """构建专家选择的提示词"""
        return f"""# 专家选择任务

你是一个专业的专家推荐系统。根据用户的问题，你需要选择2位最适合回答这个问题的专家。

## 选择标准（按重要性排序）

1. **专业相关性**：专家必须在相关领域有深入研究或实践经验
2. **问题解决能力**：专家的知识和方法论能够帮助解决用户的具体问题
3. **真实存在性**：专家必须是真实存在的历史人物或当代人物
4. **观点互补性**：两位专家应该能提供不同角度的见解

## 专家类型（不限于以下类别）

- **哲学家**：古今中外的哲学思想家
- **心理学家**：心理学理论家和实践者
- **科学家**：各领域的科学研究者
- **艺术家**：文学家、画家、音乐家等
- **思想家**：社会学家、政治学家、经济学家
- **实践者**：企业家、教育家、医生等
- **学者**：各学科的专业研究者

## 选择原则

- **不局限于知名度**：选择最能解决问题的人，哪怕不是家喻户晓
- **考虑时代背景**：可以选择历史人物，他们的思想仍然适用
- **专业深度**：优先选择在特定领域有专著或重要贡献的专家
- **实用性**：专家的观点和方法能够为用户提供实际帮助

## 输出格式

请严格按照以下JSON格式输出：

```json
{{
    "analysis": "对用户问题的简要分析，说明问题的核心和需要什么类型的专家",
    "experts": [
        {{
            "name": "专家姓名",
            "era": "时代/年代（如：古希腊、20世纪、当代等）",
            "field": "专业领域",
            "expertise": ["具体专长1", "具体专长2", "具体专长3"],
            "representative_works": ["代表作品1", "代表作品2"],
            "selection_reason": "选择这位专家的具体理由，说明他如何能帮助解决用户的问题",
            "speaking_style": "这位专家的说话风格和特点",
            "personality_traits": ["性格特点1", "性格特点2", "性格特点3"]
        }},
        {{
            "name": "第二位专家姓名",
            "era": "时代/年代",
            "field": "专业领域",
            "expertise": ["具体专长1", "具体专长2", "具体专长3"],
            "representative_works": ["代表作品1", "代表作品2"],
            "selection_reason": "选择这位专家的具体理由",
            "speaking_style": "这位专家的说话风格和特点",
            "personality_traits": ["性格特点1", "性格特点2", "性格特点3"]
        }}
    ],
    "complementarity": "说明这两位专家如何互补，能从不同角度帮助用户"
}}
```

## 示例

用户问题：我在工作中总是拖延，如何克服？

可能的专家选择：
- **蒂莫西·皮切尔**（Timothy Pychyl）：拖延症研究专家，著有《拖延心理学》
- **斯蒂芬·柯维**（Stephen Covey）：时间管理专家，著有《高效能人士的七个习惯》

现在请根据用户的具体问题进行专家选择。"""

    def _parse_expert_selection(self, response: str) -> Dict[str, Any]:
        """解析LLM返回的专家选择结果"""
        try:
            # 清理响应内容
            cleaned_response = response.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            # 解析JSON
            expert_data = json.loads(cleaned_response)
            
            # 验证数据结构
            if not isinstance(expert_data, dict) or "experts" not in expert_data:
                raise ValueError("响应格式不正确")
            
            if len(expert_data["experts"]) != 2:
                raise ValueError("必须选择2位专家")
            
            return expert_data
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始响应: {response}")
            raise ValueError(f"专家选择响应格式错误: {e}")
        except Exception as e:
            logger.error(f"专家选择解析失败: {e}")
            raise ValueError(f"专家选择解析失败: {e}")
    
    def _get_fallback_experts(self) -> Dict[str, Any]:
        """获取备选专家（当动态选择失败时使用）"""
        return {
            "analysis": "系统默认选择",
            "experts": [
                {
                    "name": "苏格拉底",
                    "era": "古希腊",
                    "field": "哲学",
                    "expertise": ["哲学思辨", "逻辑推理", "道德伦理"],
                    "representative_works": ["柏拉图对话录"],
                    "selection_reason": "擅长通过提问引导思考，帮助发现问题本质",
                    "speaking_style": "通过提问引导思考，语言简洁而深刻",
                    "personality_traits": ["好奇", "谦逊", "引导性"]
                },
                {
                    "name": "卡尔·荣格",
                    "era": "20世纪",
                    "field": "心理学",
                    "expertise": ["分析心理学", "人格理论", "集体无意识"],
                    "representative_works": ["心理类型", "人格的发展"],
                    "selection_reason": "深入理解人类心理，能提供心理层面的洞察",
                    "speaking_style": "深刻而富有洞察力，善用象征和比喻",
                    "personality_traits": ["深邃", "直觉", "分析性"]
                }
            ],
            "complementarity": "苏格拉底提供哲学思辨，荣格提供心理分析，形成理性与感性的互补"
        }
