'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { useReportStore } from '@/features/answer-report/store/reportStore';
import { ReportData } from '@/features/answer-report/types/report';
import { ApiService } from '@/services/api';

// Letter display component
import LetterDisplay from '@/features/answer-report/components/LetterDisplay';

// Removed old section headers, now using letter format

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

        // Try to get report data from API
        const response = await ApiService.getReportByThreadId(threadId);
        if (response.success && response.report) {
          setCurrentReport(response.report);
        } else {
          setError('Report data not found');
        }
      } catch (err) {
        console.error('Failed to load report:', err);
        setError('Failed to load report');
      } finally {
        setIsLoading(false);
      }
    };

    loadReport();
  }, [threadId, setCurrentReport]);

  // Get letter content
  const getLetterContent = (): string => {
    if (!currentReport?.letter_content?.letter_content) {
      return 'Loading letter content...';
    }
    return currentReport.letter_content.letter_content;
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading report...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !currentReport) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 mb-4">{error || 'Report data not found'}</p>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Start a New Chat
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header navigation */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center space-x-2 text-gray-600 hover:text-black transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Start a New Chat</span>
            </button>
          </div>
        </div>
      </div>

      {/* Letter content */}
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
