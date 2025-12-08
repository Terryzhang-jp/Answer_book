export interface Evidence {
  type: string; // "language pattern", "focus area", "emotional response"
  content: string;
  quote: string; // Original dialogue quote
}

export interface ActionPlan {
  goal: string; // Clear goal
  steps: string[]; // Specific steps
  timeline: string; // Clear timeline
  success_criteria: string; // Success criteria
}

export interface StrategicAutopsy {
  problem_categorization: string; // Problem categorization
  dimensional_analysis: string[]; // Dimensional analysis
  core_confusion: string; // Core issue diagnosis
}

export interface InternalStruggle {
  contending_parties: string[]; // Contending parties [party1, party2]
  evidence_list: {
    party1: Evidence[];
    party2: Evidence[];
  };
  outcome: string; // Struggle outcome
}

export interface CatalystEvent {
  initial_stance: string; // Initial stance
  key_insight: string; // Key insight
  conceptual_evolution: string; // Conceptual evolution
}

export interface RebirthStrategy {
  strategy_name: string; // Strategy name
  core_logic: string; // Core logic and benefits
  personal_significance: string; // Personal significance
  success_analysis: string; // Success analysis
  action_plan: ActionPlan; // Action plan
}

export interface ActionAnchor {
  core_verb: string; // Core verb
  proverb: string; // Action proverb
}

export interface LetterContent {
  letter_content: string; // Letter content
  generated_at: string; // Generation time
}

export interface ReportData {
  id: string;
  thread_id: string;
  user_id: string;
  generated_at: string;
  status: 'generating' | 'completed' | 'failed';
  current_section?: number; // Current section being generated (0-4)
  completed_sections?: number[]; // List of completed sections

  // Legacy section report fields (for backwards compatibility)
  strategic_autopsy?: StrategicAutopsy;
  internal_struggle?: InternalStruggle;
  catalyst_event?: CatalystEvent;
  rebirth_strategy?: RebirthStrategy;
  action_anchor?: ActionAnchor;

  // New letter content field
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
