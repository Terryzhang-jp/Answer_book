import axios from 'axios';
import { ReportRequest, ReportResponse, ReportStatusResponse, ReportData } from '../types/report';

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
    console.error('Report API Error:', error);

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

export class ReportApiService {
  /**
   * 生成报告
   */
  static async generateReport(request: ReportRequest): Promise<ReportResponse> {
    const response = await apiClient.post<ReportResponse>('/api/report/generate', request);
    return response.data;
  }

  /**
   * 获取报告生成状态
   */
  static async getReportStatus(taskId: string): Promise<ReportStatusResponse> {
    const response = await apiClient.get<ReportStatusResponse>(`/api/report/status/${taskId}`);
    return response.data;
  }

  /**
   * 获取完整报告
   */
  static async getReport(reportId: string): Promise<{ success: boolean; report: ReportData }> {
    const response = await apiClient.get<{ success: boolean; report: ReportData }>(`/api/report/${reportId}`);
    return response.data;
  }

  /**
   * 轮询报告状态直到完成
   */
  static async pollReportStatus(
    taskId: string,
    onStatusUpdate?: (status: string) => void,
    onProgressUpdate?: (report: Partial<ReportData>) => void,
    maxAttempts: number = 120, // 增加到120次，总共4分钟
    interval: number = 3000 // 增加轮询间隔到3秒
  ): Promise<string> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const statusResponse = await this.getReportStatus(taskId);

        if (onStatusUpdate) {
          onStatusUpdate(statusResponse.status);
        }

        // 如果有进度更新回调，并且报告正在生成，获取当前进度
        if (onProgressUpdate && statusResponse.status === 'generating' && statusResponse.report_id) {
          try {
            const progressReport = await this.getReport(statusResponse.report_id);
            onProgressUpdate(progressReport);
          } catch (progressError) {
            console.warn('获取进度失败:', progressError);
          }
        }

        if (statusResponse.status === 'completed') {
          if (!statusResponse.report_id) {
            throw new Error('报告完成但未返回报告ID');
          }
          return statusResponse.report_id;
        }

        if (statusResponse.status === 'failed') {
          // 报告生成失败，不应该重试
          const errorMessage = statusResponse.error_message || '报告生成失败';
          console.error('报告生成失败:', errorMessage);
          throw new Error(errorMessage);
        }

        // 等待下次轮询
        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        // 检查是否是报告生成失败的错误（不应该重试）
        if (error instanceof Error) {
          const errorMessage = error.message;
          if (errorMessage.includes('数据验证失败') ||
              errorMessage.includes('报告生成失败') ||
              errorMessage.includes('没有找到任何对话数据') ||
              errorMessage.includes('报告完成但未返回报告ID')) {
            console.error('报告生成业务错误，停止重试:', errorMessage);
            throw error;
          }
        }

        console.error(`轮询报告状态失败 (尝试 ${attempt + 1}/${maxAttempts}):`, error);

        if (attempt === maxAttempts - 1) {
          throw error;
        }

        // 只有网络错误等临时性错误才重试
        await new Promise(resolve => setTimeout(resolve, interval));
      }
    }

    throw new Error('报告生成超时');
  }
}
