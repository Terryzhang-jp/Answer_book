import asyncio
import uuid
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from core.models.report import ReportData, ReportRequest
from core.services.report.protocol_analyzer import ProtocolAnalyzer
from core.services.global_storage import GlobalStorage
from core.services.report.letter_generator import letter_generator

class ReportService:
    def __init__(self):
        self.protocol_analyzer = ProtocolAnalyzer()
        self.global_storage = GlobalStorage()
        self.active_tasks: Dict[str, ReportData] = {}
        self.reports_dir = "reports_data"
        self._ensure_reports_dir()
        logger.info("报告服务初始化完成")

    def _ensure_reports_dir(self):
        """确保报告存储目录存在"""
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

    def _get_report_file_path(self, report_id: str) -> str:
        """获取报告文件路径"""
        return os.path.join(self.reports_dir, f"{report_id}.json")

    def _save_report_to_file(self, report: ReportData):
        """将报告保存到文件"""
        try:
            file_path = self._get_report_file_path(report.id)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report.dict(), f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"报告已保存到文件: {file_path}")
        except Exception as e:
            logger.error(f"保存报告到文件失败: {str(e)}")

    def _load_report_from_file(self, report_id: str) -> Optional[ReportData]:
        """从文件加载报告"""
        try:
            file_path = self._get_report_file_path(report_id)
            if not os.path.exists(file_path):
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 转换datetime字符串
            if 'generated_at' in data and isinstance(data['generated_at'], str):
                data['generated_at'] = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00'))

            return ReportData(**data)
        except Exception as e:
            logger.error(f"从文件加载报告失败: {str(e)}")
            return None

    async def generate_report_async(self, request: ReportRequest) -> str:
        """异步生成报告，返回任务ID"""
        task_id = str(uuid.uuid4())
        report_id = str(uuid.uuid4())
        
        # 创建初始报告记录
        report = ReportData(
            id=report_id,
            thread_id=request.thread_id,
            user_id=request.user_id,
            generated_at=datetime.now(),
            status="generating",
            current_section=0,
            completed_sections=[]
        )
        
        self.active_tasks[task_id] = report
        
        # 启动异步任务
        asyncio.create_task(self._generate_report_task(task_id, request))
        
        logger.info(f"报告生成任务已启动 - 任务ID: {task_id}, 报告ID: {report_id}")
        return task_id

    async def _generate_report_task(self, task_id: str, request: ReportRequest):
        """执行报告生成任务"""
        try:
            report = self.active_tasks[task_id]
            logger.info(f"开始生成信件报告 - 线程ID: {request.thread_id}")

            # 1. 获取对话数据
            try:
                conversation_data = await self._get_conversation_data(request.thread_id)
                logger.info(f"获取到对话数据，消息数: {len(conversation_data)}")
            except ValueError as e:
                if str(e) == "INSUFFICIENT_CONTENT":
                    logger.info("对话内容不足，将生成简短回复")
                    conversation_data = []  # 空数据，让信件生成器处理
                else:
                    raise

            # 2. 更新进度：开始生成
            report.current_section = 1
            report.completed_sections = [0]

            # 3. 使用信件生成器生成完整信件
            letter_content = await letter_generator.generate_letter(conversation_data)

            # 4. 将信件内容保存到报告中
            from core.models.report import LetterContent
            report.letter_content = LetterContent(
                letter_content=letter_content,
                generated_at=datetime.now().isoformat()
            )

            # 5. 标记报告完成
            report.status = "completed"
            report.current_section = 1  # 信件是一个整体
            report.completed_sections = [0]

            # 6. 保存报告到文件
            self._save_report_to_file(report)

            logger.info(f"信件报告生成完成 - 报告ID: {report.id}")

        except Exception as e:
            # 处理所有错误
            error_msg = str(e)
            logger.error(f"信件报告生成失败 - 任务ID: {task_id}, 错误: {error_msg}")
            if task_id in self.active_tasks:
                self.active_tasks[task_id].status = "failed"
                self.active_tasks[task_id].error_message = f"生成失败: {error_msg}"

    def _update_report_progress(self, report: ReportData, section_index: int, section_data: Any):
        """更新报告进度的回调函数"""
        report.current_section = section_index + 1
        report.completed_sections.append(section_index)

        # 根据部分索引更新对应的数据
        if section_index == 0:
            report.strategic_autopsy = section_data
        elif section_index == 1:
            report.internal_struggle = section_data
        elif section_index == 2:
            report.catalyst_event = section_data
        elif section_index == 3:
            report.rebirth_strategy = section_data
        elif section_index == 4:
            report.action_anchor = section_data

        logger.info(f"报告进度更新 - 完成第{section_index + 1}部分")

    async def _get_conversation_data(self, thread_id: str) -> list:
        """直接从ConversationService获取对话数据"""
        try:
            # 直接从conversation_service获取数据
            from core.services.conversation_service import ConversationService
            conversation_service = ConversationService()

            # 尝试多种方式获取消息
            messages = []

            # 方式1: 从chat_histories获取（最直接）
            if thread_id in conversation_service.chat_histories:
                history = conversation_service.chat_histories[thread_id]
                messages = history.messages
                logger.info(f"从chat_histories获取消息 - 线程ID: {thread_id}, 消息数: {len(messages)}")

            # 方式2: 如果方式1没有数据，从modern_memory获取
            if not messages and hasattr(conversation_service, 'modern_memory') and conversation_service.modern_memory:
                messages = conversation_service.modern_memory.get_messages_from_backup(thread_id)
                logger.info(f"从modern_memory获取消息 - 线程ID: {thread_id}, 消息数: {len(messages)}")

            # 方式3: 最后尝试从全局存储获取
            if not messages:
                messages = self.global_storage.get_messages(thread_id)
                logger.info(f"从全局存储获取消息 - 线程ID: {thread_id}, 消息数: {len(messages)}")

            # 检查是否有有效的对话数据
            if not messages or len(messages) == 0:
                raise ValueError(f"线程 {thread_id} 没有找到任何对话数据")

            # 将BaseMessage对象转换为dict格式，以便后续处理
            from langchain_core.messages import BaseMessage
            valid_messages = []
            user_questions = 0
            ai_responses = 0
            scenario_description = None

            for msg in messages:
                if msg:
                    if isinstance(msg, BaseMessage):
                        # 转换BaseMessage为dict格式
                        msg_dict = {
                            "type": msg.__class__.__name__,
                            "content": msg.content,
                            "additional_kwargs": getattr(msg, 'additional_kwargs', {})
                        }
                        valid_messages.append(msg_dict)

                        # 统计对话轮数
                        if msg.__class__.__name__ == "HumanMessage":
                            if "我想象的未来场景：" in msg.content:
                                scenario_description = msg.content.replace("我想象的未来场景：", "").strip()
                            else:
                                user_questions += 1
                        elif msg.__class__.__name__ == "AIMessage":
                            ai_responses += 1

                    elif isinstance(msg, dict):
                        # 已经是dict格式，直接使用
                        valid_messages.append(msg)
                        if msg.get('type') == 'HumanMessage':
                            if "我想象的未来场景：" in msg.get('content', ''):
                                scenario_description = msg.get('content', '').replace("我想象的未来场景：", "").strip()
                            else:
                                user_questions += 1
                        elif msg.get('type') == 'AIMessage':
                            ai_responses += 1

            if len(valid_messages) == 0:
                raise ValueError(f"线程 {thread_id} 的对话数据格式无效")

            # 检查对话内容是否充分（至少3轮完整对话）
            if user_questions < 3 or ai_responses < 3:
                logger.warning(f"对话内容不足 - 用户问题: {user_questions}, AI回复: {ai_responses}")
                raise ValueError("INSUFFICIENT_CONTENT")  # 特殊错误码，用于生成简短回复

            logger.info(f"对话数据验证通过 - 有效消息数: {len(valid_messages)}, 用户问题: {user_questions}, AI回复: {ai_responses}")
            if scenario_description:
                logger.info(f"发现场景描述: {scenario_description[:100]}...")

            return valid_messages

        except ValueError as e:
            # 重新抛出验证错误
            if str(e) == "INSUFFICIENT_CONTENT":
                raise ValueError("INSUFFICIENT_CONTENT")
            else:
                raise
        except Exception as e:
            logger.error(f"获取对话数据失败 - 线程ID: {thread_id}, 错误: {str(e)}")
            raise ValueError(f"无法获取线程 {thread_id} 的对话数据: {str(e)}")

    def get_report_status(self, task_id: str) -> Optional[ReportData]:
        """获取报告状态"""
        return self.active_tasks.get(task_id)

    def get_report_by_id(self, report_id: str) -> Optional[ReportData]:
        """根据报告ID获取报告"""
        # 首先从内存中查找
        for report in self.active_tasks.values():
            if report.id == report_id:
                return report

        # 如果内存中没有，从文件中加载
        return self._load_report_from_file(report_id)

    def get_report_by_thread_id(self, thread_id: str) -> Optional[ReportData]:
        """根据线程ID获取最新的已完成报告"""
        # 先从内存中查找
        latest_report = None
        latest_time = None

        for report in self.active_tasks.values():
            if report.thread_id == thread_id and report.status == "completed":
                if latest_time is None or report.generated_at > latest_time:
                    latest_report = report
                    latest_time = report.generated_at

        if latest_report:
            return latest_report

        # 从文件中查找
        import os
        from pathlib import Path

        reports_dir = Path("reports_data")
        if not reports_dir.exists():
            return None

        # 遍历所有报告文件，找到匹配的thread_id
        for report_file in reports_dir.glob("*.json"):
            try:
                report = self._load_report_from_file(report_file.stem)
                if report and report.thread_id == thread_id and report.status == "completed":
                    if latest_time is None or report.generated_at > latest_time:
                        latest_report = report
                        latest_time = report.generated_at
            except Exception as e:
                logger.warning(f"加载报告文件失败: {report_file}, 错误: {e}")
                continue

        return latest_report

    def cleanup_completed_tasks(self):
        """清理已完成的任务（可选的清理机制）"""
        completed_tasks = [
            task_id for task_id, report in self.active_tasks.items()
            if report.status in ["completed", "failed"]
        ]
        
        for task_id in completed_tasks:
            # 保留一段时间后再删除，这里暂时不删除
            pass

# 全局报告服务实例
report_service = ReportService()
