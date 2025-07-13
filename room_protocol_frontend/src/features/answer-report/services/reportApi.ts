import { ReportRequest, ReportResponse, ReportStatusResponse, ReportData } from '../types/report';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ReportApiService {
  /**
   * 生成报告
   */
  static async generateReport(request: ReportRequest): Promise<ReportResponse> {
    const response = await fetch(`${API_BASE_URL}/api/report/generate`, {
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
   * 获取报告生成状态
   */
  static async getReportStatus(taskId: string): Promise<ReportStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/report/status/${taskId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * 获取完整报告
   */
  static async getReport(reportId: string): Promise<{ success: boolean; report: ReportData }> {
    const response = await fetch(`${API_BASE_URL}/api/report/${reportId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
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
