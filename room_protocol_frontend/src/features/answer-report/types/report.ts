export interface Evidence {
  type: string; // "语言模式", "关注焦点", "情绪反应"
  content: string;
  quote: string; // 原始对话引用
}

export interface ActionPlan {
  goal: string; // 清晰的目标
  steps: string[]; // 具体的步骤
  timeline: string; // 明确的时间线
  success_criteria: string; // 成功的标准
}

export interface StrategicAutopsy {
  problem_categorization: string; // 问题定性
  dimensional_analysis: string[]; // 维度剖析
  core_confusion: string; // 症结诊断
}

export interface InternalStruggle {
  contending_parties: string[]; // 博弈双方 [party1, party2]
  evidence_list: {
    party1: Evidence[];
    party2: Evidence[];
  };
  outcome: string; // 博弈结果
}

export interface CatalystEvent {
  initial_stance: string; // 初始观念
  key_insight: string; // 关键洞察
  conceptual_evolution: string; // 观念演化
}

export interface RebirthStrategy {
  strategy_name: string; // 策略名称
  core_logic: string; // 策略核心与好处
  personal_significance: string; // 个人意义
  success_analysis: string; // 成功性分析
  action_plan: ActionPlan; // 行动预案
}

export interface ActionAnchor {
  core_verb: string; // 核心动词
  proverb: string; // 行动箴言
}

export interface LetterContent {
  letter_content: string; // 信件内容
  generated_at: string; // 生成时间
}

export interface ReportData {
  id: string;
  thread_id: string;
  user_id: string;
  generated_at: string;
  status: 'generating' | 'completed' | 'failed';
  current_section?: number; // 当前正在生成的部分 (0-4)
  completed_sections?: number[]; // 已完成的部分列表

  // 旧的分段报告字段（保持兼容性）
  strategic_autopsy?: StrategicAutopsy;
  internal_struggle?: InternalStruggle;
  catalyst_event?: CatalystEvent;
  rebirth_strategy?: RebirthStrategy;
  action_anchor?: ActionAnchor;

  // 新的信件内容字段
  letter_content?: LetterContent;

  error_message?: string;
}

export interface ReportRequest {
  thread_id: string;
  user_id: string;
}

export interface ReportResponse {
  success: boolean;
  report_id?: string;
  task_id?: string;
  message: string;
}

export interface ReportStatusResponse {
  success: boolean;
  status: string;
  report_id?: string;
  error_message?: string;
}
