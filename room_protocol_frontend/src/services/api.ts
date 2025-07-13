import axios from 'axios';
import {
  QuestionRequest,
  ContinueRequest,
  AnswerResponse,
  SessionListResponse,
  HealthResponse,

  InsightRequest,
  InsightResponse,
} from '@/types/api';

// API基础配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2分钟超时，给LLM足够时间
});

// API服务类
export class ApiService {
  /**
   * 健康检查
   */
  static async healthCheck(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/health');
    return response.data;
  }

  /**
   * 创建新房间
   */
  static async createRoom(request: QuestionRequest): Promise<AnswerResponse> {
    const response = await apiClient.post<AnswerResponse>('/api/room/create', request);
    return response.data;
  }

  /**
   * 继续对话（需要thread_id）
   */
  static async askQuestion(request: QuestionRequest): Promise<AnswerResponse> {
    const response = await apiClient.post<AnswerResponse>('/api/ask', request);
    return response.data;
  }

  /**
   * 继续对话
   */
  static async continueConversation(request: ContinueRequest): Promise<AnswerResponse> {
    const response = await apiClient.post<AnswerResponse>('/api/continue', request);
    return response.data;
  }

  /**
   * 获取会话列表
   */
  static async getSessions(): Promise<SessionListResponse> {
    const response = await apiClient.get<SessionListResponse>('/api/sessions');
    return response.data;
  }

  /**
   * 删除会话
   */
  static async deleteSession(threadId: string): Promise<void> {
    await apiClient.delete(`/api/sessions/${threadId}`);
  }



  // Insight相关API

  /**
   * 生成智能insight
   */
  static async generateInsight(request: InsightRequest): Promise<InsightResponse> {
    const response = await apiClient.post<InsightResponse>('/api/insight/generate', request);
    return response.data;
  }

  /**
   * 获取insight会话信息
   */
  static async getInsightSession(sessionId: string): Promise<any> {
    const response = await apiClient.get(`/api/insight/session/${sessionId}`);
    return response.data;
  }

  /**
   * Insight服务健康检查
   */
  static async insightHealthCheck(): Promise<any> {
    const response = await apiClient.get('/api/insight/health');
    return response.data;
  }

  /**
   * 根据线程ID获取报告
   */
  static async getReportByThreadId(threadId: string): Promise<any> {
    try {
      // 直接通过线程ID获取报告
      const response = await apiClient.get(`/api/report/thread/${threadId}`);
      return response.data;
    } catch (error) {
      console.error('获取报告失败:', error);
      if (error instanceof Error && error.message.includes('404')) {
        return { success: false, message: '该对话暂无报告' };
      }
      return { success: false, message: '获取报告失败' };
    }
  }
}

// 错误处理
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
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
