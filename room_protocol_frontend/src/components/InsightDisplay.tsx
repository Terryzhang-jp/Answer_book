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

  // Use ref to track if already generated, avoid duplicate calls from state updates
  const hasGeneratedRef = useRef(false);
  const isGeneratingRef = useRef(false);

  // Generate insight when component is activated
  useEffect(() => {
    console.log('InsightDisplay mounted/updated:', {
      isActive: insightDisplay.isActive,
      hasInsight: !!insightDisplay.insight,
      hasGenerated: hasGeneratedRef.current,
      isGenerating: isGeneratingRef.current,
      sessionId: insightDisplay.sessionId
    });

    // Only call when active, no insight content, not generated before, and not currently generating
    if (insightDisplay.isActive &&
        !insightDisplay.insight &&
        !hasGeneratedRef.current &&
        !isGeneratingRef.current) {

      console.log('Starting to generate insight');
      hasGeneratedRef.current = true;
      isGeneratingRef.current = true;
      generateInsight();
    }
  }, [insightDisplay.isActive, insightDisplay.insight]);

  // Reset ref when component unmounts or resets
  useEffect(() => {
    if (!insightDisplay.isActive) {
      hasGeneratedRef.current = false;
      isGeneratingRef.current = false;
    }
  }, [insightDisplay.isActive]);

  const generateInsight = async () => {
    const callId = Date.now();
    console.log(`[${callId}] generateInsight starting`, { userId, threadId });

    try {
      setError(null);
      setInsightLoading(true);

      console.log(`[${callId}] Calling ApiService.generateInsight`);
      const response = await ApiService.generateInsight({
        user_id: userId,
        thread_id: threadId,
      });

      console.log(`[${callId}] API response:`, response);

      if (response.success && response.insight) {
        startInsightDisplay(response.session_id || '', response.insight);
      } else {
        throw new Error(response.message || 'Failed to generate insight');
      }
    } catch (err) {
      console.error(`[${callId}] Failed to generate insight:`, err);
      setError(err instanceof Error ? err.message : 'Generation failed');
    } finally {
      setInsightLoading(false);
      isGeneratingRef.current = false;
      console.log(`[${callId}] generateInsight call ended`);
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
            <h3 className="text-lg font-semibold text-gray-800">Wisdom Insight</h3>
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
              <span className="ml-2 text-gray-600">Generating wisdom insight...</span>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-500 mb-4">{error}</p>
              <button
                onClick={handleRetry}
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : insightDisplay.insight ? (
            <div className="text-center py-8">
              <div className="text-2xl font-bold text-gray-800 mb-4 leading-relaxed">
                {insightDisplay.insight}
              </div>
              <p className="text-sm text-gray-500">
                Let this thought accompany you while waiting for the wise to respond
              </p>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-600">Preparing to generate insight...</p>
            </div>
          )}
        </div>

        {insightDisplay.insight && !insightDisplay.isLoading && (
          <div className="flex justify-center">
            <button
              onClick={handleComplete}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Continue
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
