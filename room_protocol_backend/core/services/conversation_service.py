"""
对话服务 - 负责处理对话逻辑和会话管理
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Optional
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from core.services.llm_service import LLMService
from core.services.prompt_service import PromptService
from core.services.expert_service import ExpertService
from core.services.dynamic_expert_service import DynamicExpertService
from core.services.analysis_service import AnalysisService
from core.schemas.conversation import AnswerResponse, QuestionRequest, ContinueRequest
from utils.memory_system import MemorySystem
from config.constants import SYSTEM_TRIGGER_WORDS
from config.settings import get_settings

# 新记忆系统组件（条件导入）
try:
    from core.services.memory_service import ModernMemoryService
    from utils.message_trimmer import message_trimmer, expert_context_preserver
    NEW_MEMORY_AVAILABLE = True
except ImportError:
    NEW_MEMORY_AVAILABLE = False

# 统一存储系统
try:
    from core.storage.conversation_storage import get_unified_storage
    UNIFIED_STORAGE_AVAILABLE = True
except ImportError:
    UNIFIED_STORAGE_AVAILABLE = False


class ConversationService:
    """对话服务类"""

    def __init__(self):
        # 原有组件
        self.chat_histories: Dict[str, InMemoryChatMessageHistory] = {}
        self.session_experts: Dict[str, list] = {}  # 存储每个会话的专家
        self.session_all_experts: Dict[str, list] = {}  # 存储所有历史专家
        self.session_expert_reasons: Dict[str, str] = {}  # 存储每个会话的专家邀请理由
        self.session_cumulative_analysis: Dict[str, dict] = {}  # 存储累积的对话分析
        self.conversation_summaries: Dict[str, str] = {}  # 早期对话摘要
        self.prompt_service = PromptService()
        self.expert_service = ExpertService()
        self.dynamic_expert_service = DynamicExpertService()
        self.memory_system = MemorySystem()
        self.analysis_service = AnalysisService()

        # 新记忆系统组件（条件初始化）
        self.settings = get_settings()
        self.modern_memory = None

        # 统一存储系统（条件初始化）
        self.unified_storage = None
        if UNIFIED_STORAGE_AVAILABLE:
            try:
                self.unified_storage = get_unified_storage()
                print("✅ 统一存储系统已启用")
            except Exception as e:
                print(f"⚠️ 统一存储系统初始化失败: {e}")
                self.unified_storage = None
        if NEW_MEMORY_AVAILABLE and self.settings.ENABLE_NEW_MEMORY_SYSTEM:
            try:
                self.modern_memory = ModernMemoryService()
                print("新记忆系统已启用")
            except Exception as e:
                print(f"新记忆系统初始化失败: {e}")
                self.modern_memory = None
    
    def get_session_history(self, session_id: str) -> InMemoryChatMessageHistory:
        """获取或创建会话历史"""
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = InMemoryChatMessageHistory()

            # 如果启用了统一存储，尝试从存储加载历史消息
            if self.unified_storage:
                try:
                    import asyncio
                    # 在同步方法中调用异步方法
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # 如果事件循环正在运行，创建任务
                        asyncio.create_task(self._load_history_from_storage(session_id))
                    else:
                        # 如果没有运行的事件循环，直接运行
                        messages = loop.run_until_complete(self.unified_storage.get_messages(session_id))
                        for message in messages:
                            self.chat_histories[session_id].add_message(message)
                except Exception as e:
                    print(f"从统一存储加载历史失败: {e}")

        return self.chat_histories[session_id]

    async def _load_history_from_storage(self, session_id: str):
        """异步加载历史消息到内存"""
        try:
            if self.unified_storage:
                messages = await self.unified_storage.get_messages(session_id)
                for message in messages:
                    self.chat_histories[session_id].add_message(message)
                print(f"从统一存储加载历史成功: {session_id}, 消息数: {len(messages)}")
        except Exception as e:
            print(f"异步加载历史失败: {e}")
    
    async def process_question(self, request: QuestionRequest) -> AnswerResponse:
        """处理用户问题 - 主入口方法"""
        # 根据配置选择处理方式
        if self.modern_memory and self.settings.ENABLE_NEW_MEMORY_SYSTEM:
            return await self.process_question_v2(request)
        else:
            return await self.process_question_v1(request)

    async def process_question_v1(self, request: QuestionRequest) -> AnswerResponse:
        """处理用户问题 - 原有逻辑（重命名但不修改）"""
        # 确定线程ID：如果提供了thread_id则继续现有对话，否则创建新对话
        if request.thread_id and request.thread_id in self.chat_histories:
            thread_id = request.thread_id
            is_new_conversation = False
        else:
            thread_id = str(uuid.uuid4())
            is_new_conversation = True

        # 获取会话历史
        history = self.get_session_history(thread_id)
        
        # 检查是否是系统对话
        if self._is_system_dialogue(request.question):
            return await self._handle_system_dialogue(request, thread_id)

        # 检查是否要求更换专家
        expert_change_request = self._check_expert_change_request(request.question)

        # 动态专家选择（仅在新对话时）
        dynamic_expert_info = None
        if is_new_conversation:
            try:
                dynamic_expert_info = await self.dynamic_expert_service.select_experts_for_question(
                    request.question, request.user_id
                )
                print(f"动态专家选择成功: {[expert['name'] for expert in dynamic_expert_info['experts']]}")
            except Exception as e:
                print(f"动态专家选择失败，使用默认逻辑: {e}")

        # 创建系统提示词
        current_experts = self.session_experts.get(thread_id, [])
        system_prompt = self.prompt_service.get_complete_prompt(
            request.user_id,
            current_experts=current_experts,
            is_new_conversation=is_new_conversation,
            expert_change_request=expert_change_request,
            dynamic_expert_info=dynamic_expert_info
        )
        
        # 构建消息
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.question)
        ]

        try:
            # 使用带记忆的LLM调用
            config = {"configurable": {"session_id": thread_id}}
            response_content = await LLMService.generate_response_with_history(
                messages,
                config,
                self.get_session_history
            )

            # 清理响应内容（移除可能的markdown格式）
            cleaned_content = self._clean_response_content(response_content)

            # 解析JSON响应
            response_data = json.loads(cleaned_content)

            # 添加元数据
            response_data["thread_id"] = thread_id
            response_data["timestamp"] = datetime.now().isoformat()

            # 保存当前会话的专家信息
            self._update_session_experts(thread_id, response_data)

            # 更新所有专家历史
            self._update_all_experts_history(thread_id, response_data)

            # 保存到全局存储（确保报告生成能找到数据）
            # 获取完整的消息历史
            all_messages = history.messages + [
                HumanMessage(content=request.question),
                AIMessage(content=response_content)
            ]

            # 保存消息 - 优先使用统一存储
            if self.unified_storage:
                try:
                    import asyncio
                    # 异步保存到统一存储
                    asyncio.create_task(self.unified_storage.save_messages(thread_id, all_messages))
                    print(f"💾 v1版本通过统一存储保存消息 - 线程ID: {thread_id}, 消息数: {len(all_messages)}")
                except Exception as e:
                    print(f"统一存储保存失败，使用备用方案: {e}")
                    # 备用方案：使用原有逻辑
                    if hasattr(self, 'modern_memory') and self.modern_memory:
                        self.modern_memory.save_messages_to_backup(thread_id, all_messages)
                    else:
                        from core.services.global_storage import global_storage
                        global_storage.save_messages(thread_id, all_messages)
            else:
                # 备用方案：使用原有逻辑
                if hasattr(self, 'modern_memory') and self.modern_memory:
                    self.modern_memory.save_messages_to_backup(thread_id, all_messages)
                    print(f"💾 v1版本通过modern_memory保存消息到全局存储 - 线程ID: {thread_id}, 消息数: {len(all_messages)}")
                else:
                    # 直接保存到全局存储（确保数据不丢失）
                    from core.services.global_storage import global_storage
                    global_storage.save_messages(thread_id, all_messages)
                    print(f"💾 v1版本直接保存消息到全局存储 - 线程ID: {thread_id}, 消息数: {len(all_messages)}")

            # 执行对话分析
            try:
                # 获取之前的累积分析
                previous_analysis = self.session_cumulative_analysis.get(thread_id)

                analysis = await self._analyze_current_conversation(
                    thread_id=thread_id,
                    user_question=request.question,
                    current_response=response_data,
                    history=history,
                    user_id=request.user_id,
                    dynamic_expert_info=dynamic_expert_info,
                    previous_analysis=previous_analysis
                )
                if analysis:
                    # 保存累积分析结果
                    self.session_cumulative_analysis[thread_id] = analysis.model_dump()
                    response_data["conversation_analysis"] = analysis.model_dump()
                    print(f"对话分析成功: {thread_id}")
                else:
                    print(f"对话分析返回空结果: {thread_id}")
            except Exception as e:
                print(f"对话分析失败: {e}")
                import traceback
                traceback.print_exc()
                # 分析失败不影响主要功能

            # 保存到记忆系统
            if request.user_id:
                self._save_to_memory(request.user_id, request.question, response_data)

            return AnswerResponse(**response_data)

        except json.JSONDecodeError as e:
            # 处理JSON解析错误
            print(f"JSON解析错误，原始响应: {response_content}")
            return self._create_error_response(thread_id, f"响应格式错误: {e}")
        except Exception as e:
            # 处理其他错误
            print(f"处理请求时发生错误: {e}")
            return self._create_error_response(thread_id, f"处理请求时发生错误: {e}")
    
    async def continue_conversation(self, request: ContinueRequest) -> AnswerResponse:
        """继续对话"""
        # 检查线程是否存在
        if request.thread_id not in self.chat_histories:
            raise ValueError("对话会话不存在")
        
        history = self.get_session_history(request.thread_id)
        
        # 创建系统提示词
        system_prompt = self.prompt_service.get_complete_prompt(request.user_id)
        
        # 构建消息
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="请继续对话")
        ]

        try:
            # 使用带记忆的LLM调用
            config = {"configurable": {"session_id": request.thread_id}}
            response_content = await LLMService.generate_response_with_history(
                messages,
                config,
                self.get_session_history
            )
            
            # 解析JSON响应
            response_data = json.loads(response_content)
            
            # 添加元数据
            response_data["thread_id"] = request.thread_id
            response_data["timestamp"] = datetime.now().isoformat()

            # 更新所有专家历史
            self._update_all_experts_history(request.thread_id, response_data)

            # 执行对话分析
            try:
                history = self.get_session_history(request.thread_id)
                analysis = await self._analyze_current_conversation(
                    thread_id=request.thread_id,
                    user_question="请继续对话",
                    current_response=response_data,
                    history=history,
                    user_id=request.user_id
                )
                response_data["conversation_analysis"] = analysis.dict()
            except Exception as e:
                print(f"继续对话分析失败: {e}")
                # 分析失败不影响主要功能

            return AnswerResponse(**response_data)
            
        except json.JSONDecodeError as e:
            return self._create_error_response(request.thread_id, f"响应格式错误: {e}")
        except Exception as e:
            return self._create_error_response(request.thread_id, f"处理请求时发生错误: {e}")
    
    def _is_system_dialogue(self, question: str) -> bool:
        """判断是否是系统对话"""
        question_lower = question.lower()
        return any(trigger in question_lower for trigger in SYSTEM_TRIGGER_WORDS)

    def _check_expert_change_request(self, question: str) -> Optional[str]:
        """检查是否有更换/邀请专家的请求"""
        question_lower = question.lower()

        # 明确的专家更换/邀请关键词组合
        explicit_change_patterns = [
            "我想请", "我想要", "我想叫", "我想找",
            "请换", "更换", "替换", "换成",
            "邀请", "请来", "叫来", "找来", "加入",
            "让.*来", "请.*来讨论", "请.*来谈"
        ]

        # 检查是否有明确的更换/邀请意图
        import re
        for pattern in explicit_change_patterns:
            if re.search(pattern, question_lower):
                return question

        return None

    def _update_session_experts(self, thread_id: str, response_data: dict):
        """更新会话专家信息"""
        experts = []
        for char_response in response_data.get("character_responses", []):
            if char_response.get("character_role") != "system":
                expert_name = char_response.get("character_name")
                if expert_name and expert_name not in experts:
                    experts.append(expert_name)

        if experts:
            self.session_experts[thread_id] = experts
    
    async def _handle_system_dialogue(self, request: QuestionRequest, thread_id: str) -> AnswerResponse:
        """处理系统对话"""
        response_data = {
            "room_announcement": None,
            "character_responses": [
                {
                    "character_name": "房间管理员",
                    "character_role": "system",
                    "thinking": "用户在呼叫我，我应该友好回应并询问需要什么帮助",
                    "speaking": "我在这里！有什么可以帮助您的吗？无论是想邀请专家进行深度对话，还是管理房间，我随时待命。",
                    "body_language": "系统界面亮起，发出友好的提示音"
                }
            ],
            "dialogue_mode": "single",
            "next_action": "continue",
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "member_change": {
                "action": "none",
                "old_expert": None,
                "new_expert": None,
                "reason": None
            }
        }
        
        return AnswerResponse(**response_data)
    
    def _create_error_response(self, thread_id: str, error_message: str) -> AnswerResponse:
        """创建错误响应"""
        response_data = {
            "room_announcement": None,
            "character_responses": [
                {
                    "character_name": "房间管理员",
                    "character_role": "system",
                    "thinking": "系统出现了错误，我需要向用户说明情况",
                    "speaking": f"抱歉，系统遇到了一些问题：{error_message}。请稍后重试。",
                    "body_language": "系统显示错误提示"
                }
            ],
            "dialogue_mode": "single",
            "next_action": "continue",
            "thread_id": thread_id,
            "timestamp": datetime.now().isoformat(),
            "member_change": {
                "action": "none",
                "old_expert": None,
                "new_expert": None,
                "reason": None
            }
        }
        
        return AnswerResponse(**response_data)
    
    def _save_to_memory(self, user_id: str, question: str, response_data: dict):
        """保存对话到记忆系统"""
        try:
            # 获取用户记忆
            memory = self.memory_system.load_user_memory(user_id)

            # 提取专家信息
            experts_involved = []
            for char_response in response_data.get("character_responses", []):
                if char_response.get("character_role") != "system":
                    experts_involved.append(char_response.get("character_name"))

            # 更新对话统计
            memory["total_conversations"] += 1

            # 记录专家交互
            for expert in experts_involved:
                if expert not in memory["expert_interactions"]:
                    memory["expert_interactions"][expert] = {
                        "interaction_count": 0,
                        "positive_feedback": 0,
                        "negative_feedback": 0,
                        "topics": []
                    }
                memory["expert_interactions"][expert]["interaction_count"] += 1
                if question not in memory["expert_interactions"][expert]["topics"]:
                    memory["expert_interactions"][expert]["topics"].append(question)

            # 添加到对话历史
            conversation_record = {
                "timestamp": response_data.get("timestamp"),
                "question": question,
                "experts": experts_involved,
                "dialogue_mode": response_data.get("dialogue_mode")
            }

            if "conversation_history" not in memory:
                memory["conversation_history"] = []

            memory["conversation_history"].append(conversation_record)

            # 只保留最近20次对话
            if len(memory["conversation_history"]) > 20:
                memory["conversation_history"] = memory["conversation_history"][-20:]

            # 保存更新后的记忆
            self.memory_system.save_user_memory(user_id, memory)

        except Exception as e:
            # 记忆保存失败不应该影响主要功能
            print(f"保存记忆失败: {e}")
    
    def get_all_sessions(self) -> list:
        """获取所有会话"""
        sessions = []
        for session_id, history in self.chat_histories.items():
            sessions.append({
                "thread_id": session_id,
                "message_count": len(history.messages),
                "created_at": "unknown"  # 可以添加创建时间跟踪
            })
        return sessions
    
    def delete_session(self, thread_id: str) -> bool:
        """删除指定会话及其所有相关数据"""
        deleted = False

        # 删除聊天历史
        if thread_id in self.chat_histories:
            del self.chat_histories[thread_id]
            deleted = True

        # 删除会话专家信息
        if thread_id in self.session_experts:
            del self.session_experts[thread_id]
            deleted = True

        # 删除所有专家历史
        if thread_id in self.session_all_experts:
            del self.session_all_experts[thread_id]
            deleted = True

        # 删除专家邀请理由
        if thread_id in self.session_expert_reasons:
            del self.session_expert_reasons[thread_id]
            deleted = True

        # 删除累积分析
        if thread_id in self.session_cumulative_analysis:
            del self.session_cumulative_analysis[thread_id]
            deleted = True

        # 删除对话摘要
        if thread_id in self.conversation_summaries:
            del self.conversation_summaries[thread_id]
            deleted = True

        # 清理新记忆系统数据
        if hasattr(self, 'modern_memory') and self.modern_memory:
            try:
                # 清理备用存储
                self.modern_memory.clear_backup_messages(thread_id)
                # 清理对话摘要
                self.modern_memory.clear_conversation_summary(thread_id)
                deleted = True
            except Exception as e:
                print(f"清理新记忆系统数据失败: {e}")

        # 清理存储 - 优先使用统一存储
        if self.unified_storage:
            try:
                import asyncio
                asyncio.create_task(self.unified_storage.delete_conversation(thread_id))
                deleted = True
                print(f"通过统一存储清理数据成功: {thread_id}")
            except Exception as e:
                print(f"统一存储清理失败，使用备用方案: {e}")
                # 备用方案：使用原有逻辑
                try:
                    from core.services.global_storage import global_storage
                    if global_storage.has_messages(thread_id):
                        global_storage.clear_thread(thread_id)
                        deleted = True
                except Exception as e2:
                    print(f"清理全局存储数据失败: {e2}")
        else:
            # 备用方案：使用原有逻辑
            try:
                from core.services.global_storage import global_storage
                if global_storage.has_messages(thread_id):
                    global_storage.clear_thread(thread_id)
                    deleted = True
            except Exception as e:
                print(f"清理全局存储数据失败: {e}")

        if deleted:
            print(f"已删除会话 {thread_id} 及其所有相关数据")

        return deleted

    def _update_all_experts_history(self, thread_id: str, response_data: dict):
        """更新所有专家历史记录"""
        if thread_id not in self.session_all_experts:
            self.session_all_experts[thread_id] = []

        # 从当前响应中提取专家
        for char_response in response_data.get("character_responses", []):
            if char_response.get("character_role") != "system":
                expert_name = char_response.get("character_name")
                if expert_name and expert_name not in self.session_all_experts[thread_id]:
                    self.session_all_experts[thread_id].append(expert_name)

    async def _analyze_current_conversation(
        self,
        thread_id: str,
        user_question: str,
        current_response: dict,
        history,
        user_id: str = None,
        dynamic_expert_info: Optional[dict] = None,
        previous_analysis: Optional[dict] = None
    ):
        """分析当前对话"""
        # 获取所有历史专家
        all_experts = self.session_all_experts.get(thread_id, [])

        # 获取对话历史
        conversation_history = history.messages if history else []

        # 获取之前的累积分析
        previous_analysis = self.session_cumulative_analysis.get(thread_id)

        # 执行分析（首次分析或增量分析）
        analysis = await self.analysis_service.analyze_conversation_round(
            thread_id=thread_id,
            user_question=user_question,
            current_response=current_response,
            conversation_history=conversation_history,
            all_experts=all_experts,
            user_id=user_id,
            previous_analysis=previous_analysis
        )

        # 保存累积分析结果
        if analysis:
            self.session_cumulative_analysis[thread_id] = analysis.model_dump()

        # 处理专家邀请理由
        if analysis:
            # 如果是新对话且有动态专家信息，生成并保存专家邀请理由
            if dynamic_expert_info:
                expert_reason = f"基于问题分析，我们邀请了以下专家：\n\n"
                for expert in dynamic_expert_info['experts']:
                    expert_reason += f"• **{expert['name']}** ({expert['era']}) - {expert['selection_reason']}\n"
                expert_reason += f"\n{dynamic_expert_info['complementarity']}"
                self.session_expert_reasons[thread_id] = expert_reason
                analysis.expert_selection_reason = expert_reason
            # 如果不是新对话，使用保存的专家邀请理由
            elif thread_id in self.session_expert_reasons:
                analysis.expert_selection_reason = self.session_expert_reasons[thread_id]

        return analysis

    async def process_question_v2(self, request: QuestionRequest) -> AnswerResponse:
        """处理用户问题 - 新记忆系统版本"""
        # 确保LLM已初始化
        try:
            LLMService.get_model()
        except RuntimeError:
            await LLMService.initialize()

        # 确定线程ID
        if request.thread_id:
            thread_id = request.thread_id
            is_new_conversation = False
        else:
            thread_id = str(uuid.uuid4())
            is_new_conversation = True

        # 检查是否是系统对话
        if self._is_system_dialogue(request.question):
            return await self._handle_system_dialogue(request, thread_id)

        try:
            # 获取历史消息（优先使用备用存储，解决MemorySaver检索问题）
            messages = self.modern_memory.get_messages_from_backup(thread_id)

            # 如果备用存储为空，尝试从checkpointer获取（向后兼容）
            if not messages:
                checkpoint = self.modern_memory.checkpointer.get_tuple(
                    {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}
                )
                if checkpoint and checkpoint.checkpoint:
                    messages = checkpoint.checkpoint.get("channel_values", {}).get("messages", [])

            print(f"🔍 历史消息检索结果 - 线程ID: {thread_id}, 消息数: {len(messages)}")

            # 应用现代记忆管理
            processed_messages = await self.modern_memory.process_messages_with_memory(
                messages,
                thread_id,
                max_messages=self.settings.MEMORY_SLIDING_WINDOW_SIZE
            )

            # 检查专家更换请求
            expert_change_request = self._check_expert_change_request(request.question)

            # 动态专家选择（仅在新对话时）
            dynamic_expert_info = None
            if is_new_conversation:
                try:
                    dynamic_expert_info = await self.dynamic_expert_service.select_experts_for_question(
                        request.question, request.user_id
                    )
                    print(f"动态专家选择成功: {[expert['name'] for expert in dynamic_expert_info['experts']]}")
                except Exception as e:
                    print(f"动态专家选择失败，使用默认逻辑: {e}")

            # 获取当前专家信息
            current_experts = self.session_experts.get(thread_id, [])

            # 创建优化的系统提示词
            if is_new_conversation:
                # 新对话使用完整prompt
                system_prompt = self.prompt_service.get_complete_prompt(
                    request.user_id,
                    current_experts=current_experts,
                    is_new_conversation=True,
                    expert_change_request=expert_change_request,
                    dynamic_expert_info=dynamic_expert_info
                )
            else:
                # 后续对话使用简化prompt
                system_prompt = self.prompt_service.get_optimized_prompt(
                    request.user_id,
                    current_experts=current_experts,
                    expert_change_request=expert_change_request
                )

            # 构建消息
            messages_to_send = [
                SystemMessage(content=system_prompt)
            ] + processed_messages + [
                HumanMessage(content=request.question)
            ]

            # 使用直接LLM调用（避免重复历史）
            response_content = await LLMService.generate_response_direct(messages_to_send)

            # 清理和解析响应
            cleaned_content = self._clean_response_content(response_content)
            response_data = json.loads(cleaned_content)

            # 添加元数据
            response_data["thread_id"] = thread_id
            response_data["timestamp"] = datetime.now().isoformat()

            # 更新专家信息
            self._update_session_experts(thread_id, response_data)
            self._update_all_experts_history(thread_id, response_data)

            # 保存到新的checkpointer和备用存储
            new_messages = processed_messages + [
                HumanMessage(content=request.question),
                AIMessage(content=response_content)
            ]

            # 保存消息 - 优先使用统一存储
            if self.unified_storage:
                try:
                    await self.unified_storage.save_messages(thread_id, new_messages)
                    print(f"💾 v2版本通过统一存储保存消息 - 线程ID: {thread_id}, 消息数: {len(new_messages)}")
                except Exception as e:
                    print(f"统一存储保存失败，使用备用方案: {e}")
                    # 备用方案：使用原有逻辑
                    self._save_to_checkpointer(thread_id, new_messages)
                    self.modern_memory.save_messages_to_backup(thread_id, new_messages)
            else:
                # 备用方案：使用原有逻辑
                self._save_to_checkpointer(thread_id, new_messages)
                self.modern_memory.save_messages_to_backup(thread_id, new_messages)
                print(f"💾 v2版本保存消息到全局存储 - 线程ID: {thread_id}, 消息数: {len(new_messages)}")

            # 执行对话分析
            if self.settings.ENABLE_ASYNC_ANALYSIS:
                # 异步分析（后台执行，不阻塞响应）
                self._schedule_async_analysis(thread_id, request.question, response_data)
                print(f"异步对话分析已安排: {thread_id}")
            else:
                # 同步分析（确保结果包含在响应中）
                try:
                    analysis = await self._analyze_current_conversation_v2(
                        thread_id, request.question, response_data, processed_messages, request.user_id, dynamic_expert_info
                    )
                    if analysis:
                        response_data["conversation_analysis"] = analysis.model_dump()
                        print(f"对话分析成功: {thread_id}")
                    else:
                        print(f"对话分析返回空结果: {thread_id}")
                except Exception as e:
                    print(f"对话分析失败: {e}")
                    import traceback
                    traceback.print_exc()
                    # 分析失败不影响主要功能

            # 保存到记忆系统
            if request.user_id:
                self._save_to_memory(request.user_id, request.question, response_data)

            return AnswerResponse(**response_data)

        except Exception as e:
            print(f"❌ 处理请求时发生错误 (v2): {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_response(thread_id, f"处理请求时发生错误: {e}")

    def _clean_response_content(self, response_content: str) -> str:
        """清理响应内容"""
        cleaned_content = response_content.strip()

        # 移除markdown代码块标记
        if cleaned_content.startswith("```json"):
            cleaned_content = cleaned_content[7:]
        elif cleaned_content.startswith("```"):
            cleaned_content = cleaned_content[3:]

        if cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[:-3]

        cleaned_content = cleaned_content.strip()

        # 修复常见的JSON语法错误
        import re
        # 修复对象末尾多余的逗号 (如: "key": "value",})
        cleaned_content = re.sub(r',(\s*[}\]])', r'\1', cleaned_content)
        # 修复数组末尾多余的逗号 (如: "item1", "item2",])
        cleaned_content = re.sub(r',(\s*\])', r'\1', cleaned_content)

        return cleaned_content

    def _save_to_checkpointer(self, thread_id: str, messages: list):
        """保存到checkpointer"""
        try:
            config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}

            # 使用正确的checkpointer格式
            from langgraph.checkpoint.base import Checkpoint

            checkpoint = Checkpoint(
                v=1,
                ts=datetime.now().isoformat(),
                id=str(uuid.uuid4()),
                channel_values={"messages": messages},
                channel_versions={},
                versions_seen={},
                pending_sends=[]  # 添加缺失的字段
            )

            self.modern_memory.checkpointer.put(config, checkpoint, {}, {})
        except Exception as e:
            print(f"保存到checkpointer失败: {e}")
            import traceback
            traceback.print_exc()

    def _schedule_async_analysis(self, thread_id: str, question: str, response_data: dict):
        """安排异步对话分析"""
        import asyncio

        async def async_analysis():
            try:
                analysis = await self._analyze_current_conversation_v2(
                    thread_id, question, response_data, []
                )
                print(f"后台分析完成: {thread_id}")
            except Exception as e:
                print(f"后台分析失败: {e}")

        # 在后台执行
        asyncio.create_task(async_analysis())

    async def _analyze_current_conversation_v2(
        self,
        thread_id: str,
        user_question: str,
        current_response: dict,
        conversation_history: list,
        user_id: str = None,
        dynamic_expert_info: Optional[dict] = None
    ):
        """分析当前对话 - v2版本"""
        all_experts = self.session_all_experts.get(thread_id, [])

        # 获取之前的累积分析
        previous_analysis = self.session_cumulative_analysis.get(thread_id)

        # 执行分析（首次分析或增量分析）
        analysis = await self.analysis_service.analyze_conversation_round(
            thread_id=thread_id,
            user_question=user_question,
            current_response=current_response,
            conversation_history=conversation_history,
            all_experts=all_experts,
            user_id=user_id,
            previous_analysis=previous_analysis
        )

        # 保存累积分析结果
        if analysis:
            self.session_cumulative_analysis[thread_id] = analysis.model_dump()

            # 处理专家邀请理由
            if dynamic_expert_info:
                # 如果是新对话且有动态专家信息，生成并保存专家邀请理由
                expert_reason = f"基于问题分析，我们邀请了以下专家：\n\n"
                for expert in dynamic_expert_info['experts']:
                    expert_reason += f"• **{expert['name']}** ({expert['era']}) - {expert['selection_reason']}\n"
                expert_reason += f"\n{dynamic_expert_info['complementarity']}"
                self.session_expert_reasons[thread_id] = expert_reason
                analysis.expert_selection_reason = expert_reason
            elif thread_id in self.session_expert_reasons:
                analysis.expert_selection_reason = self.session_expert_reasons[thread_id]

        return analysis
