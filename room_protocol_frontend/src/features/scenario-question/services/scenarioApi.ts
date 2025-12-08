/**
 * Scenario question API service
 */

import { 
  ScenarioQuestionRequest, 
  ScenarioQuestionResponse, 
  UserScenarioResponse,
  ScenarioSession 
} from '../types/scenario';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ScenarioApiService {
  /**
   * Generate scenario imagination question
   */
  static async generateScenarioQuestion(request: ScenarioQuestionRequest): Promise<ScenarioQuestionResponse> {
    const response = await fetch(`${API_BASE_URL}/api/scenario/generate-question`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Submit user's scenario description
   */
  static async submitScenarioResponse(response: UserScenarioResponse): Promise<{ success: boolean; message: string; session_id: string }> {
    const apiResponse = await fetch(`${API_BASE_URL}/api/scenario/submit-response`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(response),
    });

    if (!apiResponse.ok) {
      throw new Error(`HTTP error! status: ${apiResponse.status}`);
    }

    return apiResponse.json();
  }

  /**
   * Get scenario session info
   */
  static async getScenarioSession(sessionId: string): Promise<{ success: boolean; session: ScenarioSession }> {
    const response = await fetch(`${API_BASE_URL}/api/scenario/session/${sessionId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get all scenario sessions for a thread
   */
  static async getThreadScenarioSessions(threadId: string): Promise<{ success: boolean; sessions: ScenarioSession[] }> {
    const response = await fetch(`${API_BASE_URL}/api/scenario/sessions/thread/${threadId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}
