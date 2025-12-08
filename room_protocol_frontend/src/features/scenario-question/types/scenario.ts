/**
 * Scenario question related type definitions
 */

export interface ScenarioQuestionData {
  scenario_question: string;
  context_explanation: string;
  imagination_guide: string;
}

export interface ScenarioQuestionRequest {
  thread_id: string;
  user_id: string;
}

export interface ScenarioQuestionResponse {
  success: boolean;
  question_data?: ScenarioQuestionData;
  message: string;
}

export interface UserScenarioResponse {
  thread_id: string;
  user_id: string;
  scenario_description: string;
}

export interface ScenarioSession {
  id: string;
  thread_id: string;
  user_id: string;
  question_data: ScenarioQuestionData;
  user_response?: string;
  created_at: string;
  completed_at?: string;
  status: 'waiting' | 'completed';
}
