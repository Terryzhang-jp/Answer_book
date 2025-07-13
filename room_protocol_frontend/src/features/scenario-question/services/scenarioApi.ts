/**
 * 场景问题API服务
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
   * 生成场景想象问题
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
   * 提交用户的场景描述
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
   * 获取场景会话信息
   */
  static async getScenarioSession(sessionId: string): Promise<{ success: boolean; session: ScenarioSession }> {
    const response = await fetch(`${API_BASE_URL}/api/scenario/session/${sessionId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * 获取指定线程的所有场景会话
   */
  static async getThreadScenarioSessions(threadId: string): Promise<{ success: boolean; sessions: ScenarioSession[] }> {
    const response = await fetch(`${API_BASE_URL}/api/scenario/sessions/thread/${threadId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}
