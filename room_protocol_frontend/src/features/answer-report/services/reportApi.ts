import { ReportRequest, ReportResponse, ReportStatusResponse, ReportData } from '../types/report';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ReportApiService {
  /**
   * Generate report
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
   * Get report generation status
   */
  static async getReportStatus(taskId: string): Promise<ReportStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/report/status/${taskId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Get complete report
   */
  static async getReport(reportId: string): Promise<{ success: boolean; report: ReportData }> {
    const response = await fetch(`${API_BASE_URL}/api/report/${reportId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Poll report status until complete
   */
  static async pollReportStatus(
    taskId: string,
    onStatusUpdate?: (status: string) => void,
    onProgressUpdate?: (report: Partial<ReportData>) => void,
    maxAttempts: number = 120, // Increased to 120 attempts, 4 minutes total
    interval: number = 3000 // Increased polling interval to 3 seconds
  ): Promise<string> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const statusResponse = await this.getReportStatus(taskId);

        if (onStatusUpdate) {
          onStatusUpdate(statusResponse.status);
        }

        // If progress update callback exists and report is generating, get current progress
        if (onProgressUpdate && statusResponse.status === 'generating' && statusResponse.report_id) {
          try {
            const progressReport = await this.getReport(statusResponse.report_id);
            onProgressUpdate(progressReport);
          } catch (progressError) {
            console.warn('Failed to get progress:', progressError);
          }
        }

        if (statusResponse.status === 'completed') {
          if (!statusResponse.report_id) {
            throw new Error('Report completed but no report ID returned');
          }
          return statusResponse.report_id;
        }

        if (statusResponse.status === 'failed') {
          // Report generation failed, should not retry
          const errorMessage = statusResponse.error_message || 'Report generation failed';
          console.error('Report generation failed:', errorMessage);
          throw new Error(errorMessage);
        }

        // Wait for next poll
        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        // Check if this is a report generation failure error (should not retry)
        if (error instanceof Error) {
          const errorMessage = error.message;
          if (errorMessage.includes('数据验证失败') ||
              errorMessage.includes('报告生成失败') ||
              errorMessage.includes('没有找到任何对话数据') ||
              errorMessage.includes('报告完成但未返回报告ID') ||
              errorMessage.includes('Data validation failed') ||
              errorMessage.includes('Report generation failed') ||
              errorMessage.includes('No conversation data found') ||
              errorMessage.includes('Report completed but no report ID returned')) {
            console.error('Report generation business error, stopping retry:', errorMessage);
            throw error;
          }
        }

        console.error(`Failed to poll report status (attempt ${attempt + 1}/${maxAttempts}):`, error);

        if (attempt === maxAttempts - 1) {
          throw error;
        }

        // Only retry for temporary errors like network issues
        await new Promise(resolve => setTimeout(resolve, interval));
      }
    }

    throw new Error('Report generation timeout');
  }
}
