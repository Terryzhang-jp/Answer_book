'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { useReportStore } from '@/features/answer-report/store/reportStore';
import { ReportData } from '@/features/answer-report/types/report';
import { ApiService } from '@/services/api';

// 信件显示组件
import LetterDisplay from '@/features/answer-report/components/LetterDisplay';

// 移除旧的分段标题，现在使用信件格式

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const threadId = params.threadId as string;

  const { currentReport, setCurrentReport } = useReportStore();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadReport = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // 尝试从API获取报告数据
        const response = await ApiService.getReportByThreadId(threadId);
        if (response.success && response.report) {
          setCurrentReport(response.report);
        } else {
          setError('未找到报告数据');
        }
      } catch (err) {
        console.error('加载报告失败:', err);
        setError('加载报告失败');
      } finally {
        setIsLoading(false);
      }
    };

    loadReport();
  }, [threadId, setCurrentReport]);

  // 获取信件内容
  const getLetterContent = (): string => {
    if (!currentReport?.letter_content?.letter_content) {
      return '信件内容加载中...';
    }
    return currentReport.letter_content.letter_content;
  };

  // 加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">正在加载报告...</p>
        </div>
      </div>
    );
  }

  // 错误状态
  if (error || !currentReport) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error || '未找到报告数据'}</p>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            开启新的聊天
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 头部导航 */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center space-x-2 text-gray-600 hover:text-black transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>开启新的聊天</span>
            </button>
          </div>
        </div>
      </div>

      {/* 信件内容 */}
      <div className="py-8">
        <LetterDisplay
          letterContent={getLetterContent()}
          threadId={threadId}
          userId={currentReport?.user_id || ''}
        />
      </div>

    </div>
  );
}
