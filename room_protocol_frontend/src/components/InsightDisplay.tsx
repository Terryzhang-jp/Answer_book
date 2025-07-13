import React, { useState, useEffect, useRef } from 'react';
import { X, Lightbulb, Loader2 } from 'lucide-react';
import { useConversationStore } from '@/store/conversation';
import { ApiService } from '@/services/api';

interface InsightDisplayProps {
  userId: string;
  threadId: string;
  onComplete: () => void;
  onSkip: () => void;
}

export default function InsightDisplay({
  userId,
  threadId,
  onComplete,
  onSkip
}: InsightDisplayProps) {
  const [error, setError] = useState<string | null>(null);
  const { insightDisplay, startInsightDisplay, setInsightLoading } = useConversationStore();

  // 使用ref来跟踪是否已经生成过，避免状态更新导致的重复调用
  const hasGeneratedRef = useRef(false);
  const isGeneratingRef = useRef(false);

  // 当组件激活时生成insight
  useEffect(() => {
    console.log('InsightDisplay mounted/updated:', {
      isActive: insightDisplay.isActive,
      hasInsight: !!insightDisplay.insight,
      hasGenerated: hasGeneratedRef.current,
      isGenerating: isGeneratingRef.current,
      sessionId: insightDisplay.sessionId
    });

    // 只有在激活状态、没有insight内容、没有生成过、没有正在生成时才调用
    if (insightDisplay.isActive &&
        !insightDisplay.insight &&
        !hasGeneratedRef.current &&
        !isGeneratingRef.current) {

      console.log('开始生成insight');
      hasGeneratedRef.current = true;
      isGeneratingRef.current = true;
      generateInsight();
    }
  }, [insightDisplay.isActive, insightDisplay.insight]);

  // 当组件卸载或重置时，重置ref
  useEffect(() => {
    if (!insightDisplay.isActive) {
      hasGeneratedRef.current = false;
      isGeneratingRef.current = false;
    }
  }, [insightDisplay.isActive]);

  const generateInsight = async () => {
    const callId = Date.now();
    console.log(`[${callId}] generateInsight 开始调用`, { userId, threadId });

    try {
      setError(null);
      setInsightLoading(true);

      console.log(`[${callId}] 调用 ApiService.generateInsight`);
      const response = await ApiService.generateInsight({
        user_id: userId,
        thread_id: threadId,
      });

      console.log(`[${callId}] API响应:`, response);

      if (response.success && response.insight) {
        startInsightDisplay(response.session_id || '', response.insight);
      } else {
        throw new Error(response.message || '生成insight失败');
      }
    } catch (err) {
      console.error(`[${callId}] 生成insight失败:`, err);
      setError(err instanceof Error ? err.message : '生成失败');
    } finally {
      setInsightLoading(false);
      isGeneratingRef.current = false;
      console.log(`[${callId}] generateInsight 调用结束`);
    }
  };

  const handleComplete = () => {
    onComplete();
  };

  const handleSkip = () => {
    onSkip();
  };

  const handleRetry = () => {
    setError(null);
    hasGeneratedRef.current = false;
    isGeneratingRef.current = false;
    generateInsight();
  };

  if (!insightDisplay.isActive) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Lightbulb className="w-5 h-5 text-yellow-500" />
            <h3 className="text-lg font-semibold text-gray-800">智慧洞察</h3>
          </div>
          <button
            onClick={handleSkip}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-6">
          {insightDisplay.isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
              <span className="ml-2 text-gray-600">正在生成智慧洞察...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-500 mb-4">{error}</p>
              <button
                onClick={handleRetry}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                重试
              </button>
            </div>
          ) : insightDisplay.insight ? (
            <div className="text-center py-8">
              <div className="text-2xl font-bold text-gray-800 mb-4 leading-relaxed">
                {insightDisplay.insight}
              </div>
              <p className="text-sm text-gray-500">
                在等待智者回答的过程中，让这句话陪伴您思考
              </p>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-600">准备生成洞察...</p>
            </div>
          )}
        </div>

        {insightDisplay.insight && !insightDisplay.isLoading && (
          <div className="flex justify-center">
            <button
              onClick={handleComplete}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              继续
            </button>
          </div>
        )}
      </div>
    </div>
  );
}