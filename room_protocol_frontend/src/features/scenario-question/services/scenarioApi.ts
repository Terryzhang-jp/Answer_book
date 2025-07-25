/**
 * 场景问题API服务
 */

import axios from 'axios';
import {
  ScenarioQuestionRequest,
  ScenarioQuestionResponse,
  UserScenarioResponse,
  ScenarioSession
} from '../types/scenario';

// API基础配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2分钟超时，给LLM足够时间
});

// 错误处理
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Scenario API Error:', error);

    if (error.response) {
      // 服务器返回错误状态码
      const message = error.response.data?.detail || error.response.data?.message || '服务器错误';
      throw new Error(`${error.response.status}: ${message}`);
    } else if (error.request) {
      // 请求发送但没有收到响应
      throw new Error('网络连接失败，请检查网络或后端服务');
    } else {
      // 其他错误
      throw new Error(error.message || '未知错误');
    }
  }
);

export class ScenarioApiService {
  /**
   * 生成场景想象问题
   */
  static async generateScenarioQuestion(request: ScenarioQuestionRequest): Promise<ScenarioQuestionResponse> {
    const response = await apiClient.post<ScenarioQuestionResponse>('/api/scenario/generate-question', request);
    return response.data;
  }

  /**
   * 提交用户的场景描述
   */
  static async submitScenarioResponse(response: UserScenarioResponse): Promise<{ success: boolean; message: string; session_id: string }> {
    const apiResponse = await apiClient.post<{ success: boolean; message: string; session_id: string }>('/api/scenario/submit-response', response);
    return apiResponse.data;
  }

  /**
   * 获取场景会话信息
   */
  static async getScenarioSession(sessionId: string): Promise<{ success: boolean; session: ScenarioSession }> {
    const response = await apiClient.get<{ success: boolean; session: ScenarioSession }>(`/api/scenario/session/${sessionId}`);
    return response.data;
  }

  /**
   * 获取指定线程的所有场景会话
   */
  static async getThreadScenarioSessions(threadId: string): Promise<{ success: boolean; sessions: ScenarioSession[] }> {
    const response = await apiClient.get<{ success: boolean; sessions: ScenarioSession[] }>(`/api/scenario/sessions/thread/${threadId}`);
    return response.data;
  }
}
