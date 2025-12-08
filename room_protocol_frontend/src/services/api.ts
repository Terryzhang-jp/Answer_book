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

// API base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 minute timeout for LLM processing
});

// API service class
export class ApiService {
  /**
   * Health check
   */
  static async healthCheck(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/api/health');
    return response.data;
  }

  /**
   * Create new room
   */
  static async createRoom(request: QuestionRequest): Promise<AnswerResponse> {
    const response = await apiClient.post<AnswerResponse>('/api/room/create', request);
    return response.data;
  }

  /**
   * Ask question (requires thread_id for continuation)
   */
  static async askQuestion(request: QuestionRequest): Promise<AnswerResponse> {
    const response = await apiClient.post<AnswerResponse>('/api/ask', request);
    return response.data;
  }

  /**
   * Continue conversation
   */
  static async continueConversation(request: ContinueRequest): Promise<AnswerResponse> {
    const response = await apiClient.post<AnswerResponse>('/api/continue', request);
    return response.data;
  }

  /**
   * Get session list
   */
  static async getSessions(): Promise<SessionListResponse> {
    const response = await apiClient.get<SessionListResponse>('/api/sessions');
    return response.data;
  }

  /**
   * Delete session
   */
  static async deleteSession(threadId: string): Promise<void> {
    await apiClient.delete(`/api/sessions/${threadId}`);
  }



  // Insight related APIs

  /**
   * Generate smart insight
   */
  static async generateInsight(request: InsightRequest): Promise<InsightResponse> {
    const response = await apiClient.post<InsightResponse>('/api/insight/generate', request);
    return response.data;
  }

  /**
   * Get insight session info
   */
  static async getInsightSession(sessionId: string): Promise<any> {
    const response = await apiClient.get(`/api/insight/session/${sessionId}`);
    return response.data;
  }

  /**
   * Insight service health check
   */
  static async insightHealthCheck(): Promise<any> {
    const response = await apiClient.get('/api/insight/health');
    return response.data;
  }

  /**
   * Get report by thread ID
   */
  static async getReportByThreadId(threadId: string): Promise<any> {
    try {
      // Get report directly by thread ID
      const response = await apiClient.get(`/api/report/thread/${threadId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get report:', error);
      if (error instanceof Error && error.message.includes('404')) {
        return { success: false, message: 'No report available for this conversation' };
      }
      return { success: false, message: 'Failed to get report' };
    }
  }
}

// Error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);

    if (error.response) {
      // Server returned error status code
      const message = error.response.data?.detail || error.response.data?.message || 'Server error';
      throw new Error(`${error.response.status}: ${message}`);
    } else if (error.request) {
      // Request sent but no response received
      throw new Error('Network connection failed, please check your network or backend service');
    } else {
      // Other errors
      throw new Error(error.message || 'Unknown error');
    }
  }
);
