import json
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from core.models.report import (
    StrategicAutopsy, InternalStruggle, CatalystEvent,
    RebirthStrategy, ActionAnchor, Evidence, ActionPlan
)
from config.settings import get_settings
from loguru import logger

class ProtocolAnalyzer:
    def __init__(self):
        settings = get_settings()
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required in settings")

        self.model = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.3,
            max_tokens=4000,
            google_api_key=settings.GEMINI_API_KEY
        )
        logger.info("Protocol分析引擎初始化成功: gemini-2.5-pro")

    async def analyze_conversation_streaming(self, conversation_data: List[Any], report: Any, progress_callback) -> None:
        """
        流式分析对话，每完成一个部分就通过回调更新
        """
        try:
            logger.info(f"开始流式Protocol分析，对话消息数: {len(conversation_data)}")

            sections = [
                (0, "第一部分：战略验尸", self._strategic_autopsy),
                (1, "第二部分：内心博弈分析", self._internal_struggle_analysis),
                (2, "第三部分：催化剂事件分析", self._catalyst_event_analysis),
                (3, "第四部分：重生策略与行动预案", None),  # 需要前面的结果
                (4, "第五部分：行动锚点锻造", None)  # 需要第四部分的结果
            ]

            # 存储中间结果
            results = {}

            for section_index, section_name, section_func in sections:
                logger.info(f"执行{section_name}")

                if section_index <= 2:
                    # 前三个部分直接调用
                    result = await section_func(conversation_data)
                elif section_index == 3:
                    # 第四部分需要前面的结果
                    result = await self._rebirth_strategy(
                        conversation_data,
                        results.get(0),
                        results.get(1),
                        results.get(2)
                    )
                elif section_index == 4:
                    # 第五部分需要第四部分的结果
                    result = await self._action_anchor(results.get(3))

                # 保存结果
                results[section_index] = result

                # 通过回调更新进度
                progress_callback(report, section_index, result)

                logger.info(f"{section_name} 完成")

            logger.info("流式Protocol分析完成")

        except Exception as e:
            logger.error(f"流式Protocol分析失败: {str(e)}")
            raise

    async def analyze_conversation(self, conversation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        根据"战略验尸与重生"协议v4.0分析对话
        """
        try:
            logger.info(f"开始Protocol分析，对话消息数: {len(conversation_data)}")
            
            # 第一部分：战略验尸
            logger.info("执行第一部分：战略验尸")
            strategic_autopsy = await self._strategic_autopsy(conversation_data)
            
            # 第二部分：内心博弈分析
            logger.info("执行第二部分：内心博弈分析")
            internal_struggle = await self._internal_struggle_analysis(conversation_data)
            
            # 第三部分：催化剂事件分析
            logger.info("执行第三部分：催化剂事件分析")
            catalyst_event = await self._catalyst_event_analysis(conversation_data)
            
            # 第四部分：重生策略与行动预案
            logger.info("执行第四部分：重生策略与行动预案")
            rebirth_strategy = await self._rebirth_strategy(conversation_data, strategic_autopsy, internal_struggle, catalyst_event)
            
            # 第五部分：行动锚点锻造
            logger.info("执行第五部分：行动锚点锻造")
            action_anchor = await self._action_anchor(rebirth_strategy)
            
            result = {
                "strategic_autopsy": strategic_autopsy,
                "internal_struggle": internal_struggle,
                "catalyst_event": catalyst_event,
                "rebirth_strategy": rebirth_strategy,
                "action_anchor": action_anchor
            }
            
            logger.info("Protocol分析完成")
            return result
            
        except Exception as e:
            logger.error(f"Protocol分析失败: {str(e)}")
            raise

    async def _strategic_autopsy(self, conversation_data: List[Dict[str, Any]]) -> StrategicAutopsy:
        """第一部分：战略验尸"""
        conversation_text = self._format_conversation(conversation_data)
        
        prompt = f"""
根据"战略验尸与重生"协议v4.0的第一部分，分析以下对话。

协议要求：
1. 诊断优先于总结：不是复述对话，而是对用户的困惑进行结构化诊断
2. 证据驱动：每一项分析都必须有明确的对话内容作为证据支撑
3. 直面冲突：勇敢地揭示用户内心的核心矛盾与认知失调

执行指令：

指令1.1 - 问题定性：
从以下类别中选择一个或多个作为问题的根本属性：
- 商业模式问题：核心在于价值创造、传递和捕获的逻辑链条不清晰或不可持续
- 战略定位问题：核心在于不清楚在哪个市场、为哪个客群、提供何种独特的价值
- 心理障碍问题：核心在于非理性的恐惧、不自信、或完美主义等情绪因素
- 资源与能力问题：核心在于目标与现有资源之间的巨大差距
- 价值认知问题：核心在于对自身或所提供事物的价值判断不清

指令1.2 - 维度剖析：
选择2-3个最关键的分析维度，对问题进行拆解：
- 商业维度：价值主张/客户画像/盈利模式/竞争壁垒/市场规模
- 个人维度：动机与恐惧/优势与劣势/价值观与目标/认知与盲区

指令1.3 - 症结诊断：
精准指出问题真正的"症结"所在，用一句高度概括、锐利且一针见血的陈述表达。

对话内容：
{conversation_text}

请严格按照协议执行分析，返回JSON格式：
{{
    "problem_categorization": "问题定性结果（选择一个主要类别，用字符串表示）",
    "dimensional_analysis": ["维度1的分析内容（字符串）", "维度2的分析内容（字符串）", "维度3的分析内容（字符串）"],
    "core_confusion": "症结诊断的一句话总结"
}}

注意：
- problem_categorization必须是单个字符串，不是数组
- dimensional_analysis必须是字符串数组，每个元素是完整的分析内容，不是对象
"""
        
        response = await self.model.ainvoke(prompt)
        result = self._parse_json_response(response.content)
        
        return StrategicAutopsy(**result)

    async def _internal_struggle_analysis(self, conversation_data: List[Dict[str, Any]]) -> InternalStruggle:
        """第二部分：内心博弈分析"""
        conversation_text = self._format_conversation(conversation_data)
        
        prompt = f"""
根据"战略验尸与重生"协议v4.0的第二部分，分析用户内心的思想斗争。

核心原则："你的行为和语言，是你内心价值观的投票。"

执行指令：

指令2.1 - 识别博弈双方：
从对话中提炼出用户内心存在的两个主要对立面。例如："渴望安稳的保守派" vs "追求突破的冒险家"。

指令2.2 - 构建证据清单：
为博弈的每一方，列出具体的、引用自对话的证据：
- 语言模式：使用的词汇频率、情感色彩
- 关注焦点：在哪个话题上投入的追问最多、思考最深
- 情绪反应：对嘉宾提出的不同建议所表现出的接受、抵触或回避等情绪

指令2.3 - 宣布博弈结果：
基于证据清单，给出客观的分析结论，明确指出哪一方在对话中占据了主导地位。

对话内容：
{conversation_text}

请返回JSON格式：
{{
    "contending_parties": ["对立面1", "对立面2"],
    "evidence_list": {{
        "party1": [
            {{"type": "语言模式", "content": "分析内容", "quote": "原始对话引用"}},
            {{"type": "关注焦点", "content": "分析内容", "quote": "原始对话引用"}}
        ],
        "party2": [
            {{"type": "情绪反应", "content": "分析内容", "quote": "原始对话引用"}}
        ]
    }},
    "outcome": "博弈结果分析"
}}

注意：严格按照上述JSON结构返回，不要添加额外的字段或改变数据类型。
"""
        
        response = await self.model.ainvoke(prompt)
        result = self._parse_json_response(response.content)
        
        # 转换evidence格式
        evidence_list = {}
        for party, evidences in result["evidence_list"].items():
            evidence_list[party] = [Evidence(**evidence) for evidence in evidences]
        
        return InternalStruggle(
            contending_parties=result["contending_parties"],
            evidence_list=evidence_list,
            outcome=result["outcome"]
        )

    def _format_conversation(self, conversation_data: List[Any]) -> str:
        """格式化对话数据为文本"""
        formatted = []

        for msg in conversation_data:
            # 处理LangChain消息对象
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                msg_type = msg.type
                content = msg.content

                if msg_type == "human":
                    formatted.append(f"用户: {content}")
                elif msg_type == "ai":
                    # 尝试解析AI回答中的JSON格式
                    try:
                        import json
                        # 如果content是JSON字符串，解析它
                        if isinstance(content, str) and content.strip().startswith('{'):
                            parsed_content = json.loads(content)
                            if "character_responses" in parsed_content:
                                for response in parsed_content["character_responses"]:
                                    name = response.get("character_name", "嘉宾")
                                    thinking = response.get("thinking", "")
                                    speech = response.get("speech", "")
                                    if thinking:
                                        formatted.append(f"{name}(思考): {thinking}")
                                    if speech:
                                        formatted.append(f"{name}: {speech}")
                            else:
                                formatted.append(f"系统: {content}")
                        else:
                            formatted.append(f"系统: {content}")
                    except (json.JSONDecodeError, TypeError):
                        formatted.append(f"系统: {content}")
            # 处理字典格式的消息（兼容性）
            elif isinstance(msg, dict):
                if msg.get("type") == "user":
                    formatted.append(f"用户: {msg.get('content', '')}")
                elif msg.get("type") == "assistant":
                    content = msg.get("content", {})
                    if isinstance(content, dict) and "character_responses" in content:
                        for response in content["character_responses"]:
                            name = response.get("character_name", "嘉宾")
                            thinking = response.get("thinking", "")
                            speech = response.get("speech", "")
                            if thinking:
                                formatted.append(f"{name}(思考): {thinking}")
                            if speech:
                                formatted.append(f"{name}: {speech}")
                    else:
                        formatted.append(f"系统: {content}")

        return "\n\n".join(formatted)

    async def _catalyst_event_analysis(self, conversation_data: List[Dict[str, Any]]) -> CatalystEvent:
        """第三部分：催化剂事件分析"""
        conversation_text = self._format_conversation(conversation_data)

        prompt = f"""
根据"战略验尸与重生"协议v4.0的第三部分，分析对话中的关键转折点。

核心原则："顿悟不是凭空产生的，它是一个准备好的头脑与一个恰当的洞察相遇的结果。"

执行指令：

指令3.1 - 描述初始观念：
清晰、准确地描述用户在对话开始时所持有的核心假设或思维框架，并提供证据。

指令3.2 - 识别并注入关键洞察：
明确指出是哪一位嘉宾，提供了哪一个具体的、颠覆性的核心观念。必须直接引用或精确概括该观念。

指令3.3 - 详述观念演化：
详细描述这个"催化剂"是如何改变用户思考的：
- 它打破了用户的哪个旧假设？
- 它为用户提供了哪个新视角或新框架？
- 用户的关注点、提问方式和语言风格因此发生了怎样的具体变化？

对话内容：
{conversation_text}

请返回JSON格式：
{{
    "initial_stance": "用户初始观念描述（字符串）",
    "key_insight": "关键洞察内容（包含提供者）（字符串）",
    "conceptual_evolution": "观念演化的详细描述（字符串）"
}}

注意：
- 所有字段都必须是字符串类型，不能是对象或数组
- 严格按照上述JSON结构返回，不要添加额外的字段
"""

        response = await self.model.ainvoke(prompt)
        result = self._parse_json_response(response.content)

        return CatalystEvent(**result)

    async def _rebirth_strategy(self, conversation_data: List[Dict[str, Any]],
                               autopsy: StrategicAutopsy, struggle: InternalStruggle,
                               catalyst: CatalystEvent) -> RebirthStrategy:
        """第四部分：重生策略与行动预案"""
        conversation_text = self._format_conversation(conversation_data)

        prompt = f"""
根据"战略验尸与重生"协议v4.0的第四部分，制定具体的解决策略。

核心原则："一个好的战略，不仅告诉你做什么，还告诉你为什么做，以及如何迈出第一步。"

前面分析结果：
- 症结诊断：{autopsy.core_confusion}
- 内心博弈结果：{struggle.outcome}
- 关键洞察：{catalyst.key_insight}

执行指令：

指令4.1 - 命名新策略：
为最终浮现的解决方案，起一个简洁、有力、易于记忆的名字。

指令4.2 - 阐述策略核心与好处：
用最平实、最接地气的语言，解释这个策略是什么，以及它为什么好。

指令4.3 - 阐述其个人意义：
将此策略与前面的"症结诊断"和"内心博弈"直接挂钩，说明为什么能够完美地解决内心的核心冲突。

指令4.4 - 进行成功性分析：
从市场、竞争、趋势等角度，提供1-2个接地气的理由，解释为什么这个策略在当前环境下更可能成功。

指令4.5 - 设计具体的行动预案：
提供一个具体的、小规模的、以验证假设为目的的行动步骤。

对话内容：
{conversation_text}

请返回JSON格式：
{{
    "strategy_name": "策略名称",
    "core_logic": "策略核心与好处",
    "personal_significance": "个人意义说明",
    "success_analysis": "成功性分析",
    "action_plan": {{
        "goal": "清晰的目标",
        "steps": ["步骤1", "步骤2", "步骤3"],
        "timeline": "明确的时间线",
        "success_criteria": "成功的标准"
    }}
}}
"""

        response = await self.model.ainvoke(prompt)
        result = self._parse_json_response(response.content)

        action_plan = ActionPlan(**result["action_plan"])

        return RebirthStrategy(
            strategy_name=result["strategy_name"],
            core_logic=result["core_logic"],
            personal_significance=result["personal_significance"],
            success_analysis=result["success_analysis"],
            action_plan=action_plan
        )

    async def _action_anchor(self, strategy: RebirthStrategy) -> ActionAnchor:
        """第五部分：行动锚点锻造"""

        prompt = f"""
根据"战略验尸与重生"协议v4.0的第五部分，锻造行动锚点。

核心原则："语言塑造思想，思想指导行动。"

策略信息：
- 策略名称：{strategy.strategy_name}
- 核心逻辑：{strategy.core_logic}
- 行动预案：{strategy.action_plan.goal}

执行指令：

指令5.1 - 提炼核心动词：
从行动预案中，找到最关键的、最能代表策略精髓的动词（如：诊断、连接、讲述、构建、验证）。

指令5.2 - 锻造行动箴言：
将这个核心动词，与用户的核心价值或新发现的洞察结合，创造一句简短、有力、对称、易于记忆的行动口号。

请返回JSON格式：
{{
    "core_verb": "核心动词",
    "proverb": "行动箴言"
}}
"""

        response = await self.model.ainvoke(prompt)
        result = self._parse_json_response(response.content)

        return ActionAnchor(**result)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析LLM返回的JSON响应"""
        try:
            # 尝试直接解析
            result = json.loads(response)
            return self._clean_json_data(result)
        except json.JSONDecodeError:
            # 如果失败，尝试提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return self._clean_json_data(result)
            else:
                raise ValueError(f"无法解析JSON响应: {response}")

    def _clean_json_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """清理JSON数据，确保格式正确"""
        cleaned = {}

        for key, value in data.items():
            if isinstance(value, list):
                # 如果是列表，检查是否应该是字符串
                if key in ["problem_categorization"] and len(value) > 0:
                    # 将列表转换为字符串（取第一个或连接）
                    cleaned[key] = value[0] if isinstance(value[0], str) else str(value[0])
                elif key in ["dimensional_analysis"]:
                    # 确保是字符串列表
                    cleaned[key] = [str(item) if not isinstance(item, str) else item for item in value]
                else:
                    cleaned[key] = value
            elif isinstance(value, dict):
                # 如果是字典，检查是否应该是字符串
                if key in ["conceptual_evolution"]:
                    # 将字典转换为描述性字符串
                    if "broken_assumption" in value and "new_perspective" in value:
                        cleaned[key] = f"打破假设：{value.get('broken_assumption', '')}；新视角：{value.get('new_perspective', '')}"
                    else:
                        cleaned[key] = str(value)
                else:
                    cleaned[key] = value
            else:
                cleaned[key] = value

        return cleaned
