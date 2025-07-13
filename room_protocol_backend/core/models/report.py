from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Evidence(BaseModel):
    type: str  # "语言模式", "关注焦点", "情绪反应"
    content: str
    quote: str  # 原始对话引用

class ActionPlan(BaseModel):
    goal: str  # 清晰的目标
    steps: List[str]  # 具体的步骤
    timeline: str  # 明确的时间线
    success_criteria: str  # 成功的标准

class StrategicAutopsy(BaseModel):
    problem_categorization: str  # 问题定性
    dimensional_analysis: List[str]  # 维度剖析
    core_confusion: str  # 症结诊断

class InternalStruggle(BaseModel):
    contending_parties: List[str]  # 博弈双方 [party1, party2]
    evidence_list: Dict[str, List[Evidence]]  # {"party1": [...], "party2": [...]}
    outcome: str  # 博弈结果

class CatalystEvent(BaseModel):
    initial_stance: str  # 初始观念
    key_insight: str  # 关键洞察
    conceptual_evolution: str  # 观念演化

class RebirthStrategy(BaseModel):
    strategy_name: str  # 策略名称
    core_logic: str  # 策略核心与好处
    personal_significance: str  # 个人意义
    success_analysis: str  # 成功性分析
    action_plan: ActionPlan  # 行动预案

class ActionAnchor(BaseModel):
    core_verb: str  # 核心动词
    proverb: str  # 行动箴言

class LetterContent(BaseModel):
    letter_content: str  # 信件内容
    generated_at: str  # 生成时间

class ReportData(BaseModel):
    id: str
    thread_id: str
    user_id: str
    generated_at: datetime
    status: str  # "generating", "completed", "failed"
    current_section: int = 0  # 当前正在生成的部分 (0-4)
    completed_sections: List[int] = []  # 已完成的部分列表

    # 旧的分段报告字段（保持兼容性）
    strategic_autopsy: Optional[StrategicAutopsy] = None
    internal_struggle: Optional[InternalStruggle] = None
    catalyst_event: Optional[CatalystEvent] = None
    rebirth_strategy: Optional[RebirthStrategy] = None
    action_anchor: Optional[ActionAnchor] = None

    # 新的信件内容字段
    letter_content: Optional[LetterContent] = None

    error_message: Optional[str] = None

class ReportRequest(BaseModel):
    thread_id: str
    user_id: str

class ReportResponse(BaseModel):
    success: bool
    report_id: Optional[str] = None
    task_id: Optional[str] = None
    message: str
