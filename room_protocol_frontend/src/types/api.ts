// API type definitions

export interface QuestionRequest {
  question: string;
  user_id?: string;
  thread_id?: string;
}

export interface ContinueRequest {
  thread_id: string;
  user_id?: string;
}

export interface CharacterResponse {
  character_name: string;
  character_role: 'system' | 'expert_1' | 'expert_2';
  thinking: string;
  speaking: string;
  body_language: string;
}

export interface MemberChange {
  action: 'invite' | 'remove' | 'none';
  old_expert?: string;
  new_expert?: string;
  reason?: string;
}

// Conversation analysis related types
export interface ExpertInsight {
  expert_name: string;
  total_contributions: number;
  key_insights: string[];
  helpful_points: string[];
  expertise_areas: string[];
  last_appearance: string;
  is_current: boolean;
}

export interface ConversationEvolution {
  topic_progression: string[];
  key_turning_points: string[];
  discussion_depth: string;
}

export interface ConversationTimelineEntry {
  speaker: string; // Speaker (expert name or 'User')
  action: string; // Action description
  content: string; // Specific content
  timestamp: string; // Timestamp
  round_number: number; // Conversation round number
}

export interface ConversationAnalysis {
  user_question_analysis: string;
  expert_selection_reason?: string; // Expert invitation reason
  conversation_timeline: ConversationTimelineEntry[]; // Conversation timeline summary
  all_experts_insights: ExpertInsight[];
  conversation_evolution: ConversationEvolution;
  suggested_directions: string[];
  analysis_timestamp: string;
}

export interface AnswerResponse {
  room_announcement?: string;
  character_responses: CharacterResponse[];
  dialogue_mode: 'single' | 'free_dialogue';
  next_action: 'continue' | 'invite_expert' | 'remove_expert' | 'end';
  thread_id: string;
  timestamp: string;
  member_change?: MemberChange;
  conversation_analysis?: ConversationAnalysis;
}

export interface SessionInfo {
  thread_id: string;
  message_count: number;
  created_at: string;
}

export interface SessionListResponse {
  sessions: SessionInfo[];
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
}



// Insight related types
export interface InsightRequest {
  user_id: string;
  thread_id: string;
  user_context?: Record<string, any>;
}

export interface InsightResponse {
  success: boolean;
  session_id?: string;
  insight: string;
  analysis_summary?: string;
  message?: string;
}
