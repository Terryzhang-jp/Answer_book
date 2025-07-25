'use client';

import React, { useState } from 'react';
import { CheckCircle, Loader2, AlertTriangle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';

interface CompleteAnswerButtonProps {
  threadId: string;
  userId: string;
  className?: string;
}

// 确认弹框组件
const ConfirmationModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  isLoading 
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  onConfirm: () => void;
  isLoading: boolean;
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
      >
        <div className="text-center">
          <div className="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-8 h-8 text-amber-600" />
          </div>
          
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            结束对话并生成答案之书
          </h3>
          
          <p className="text-gray-600 mb-6 leading-relaxed">
            点击确认后，将会结束当前对话，并为您生成一份专属的答案之书信件。
            <br />
            <span className="text-sm text-amber-600 font-medium">
              此操作不可撤销，请确认您已获得满意的答案。
            </span>
          </p>

          <div className="flex space-x-3">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg transition-colors disabled:opacity-50"
            >
              取消
            </button>
            
            <button
              onClick={onConfirm}
              disabled={isLoading}
              className="flex-1 px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>处理中...</span>
                </>
              ) : (
                <span>确认生成</span>
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

// 场景问题模态框组件（简化版）
const ScenarioModal = ({ 
  isOpen, 
  onClose, 
  onComplete,
  scenarioQuestion,
  isLoading
}: { 
  isOpen: boolean; 
  onClose: () => void; 
  onComplete: (description: string) => void;
  scenarioQuestion: any;
  isLoading: boolean;
}) => {
  const [description, setDescription] = useState('');

  if (!isOpen || !scenarioQuestion) return null;

  const handleSubmit = () => {
    if (description.trim()) {
      onComplete(description.trim());
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold text-gray-900">想象您的未来场景</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <p className="text-blue-800 font-medium">
              💭 "你的未来生活只是你能想象到的生活"
            </p>
          </div>

          <div className="text-center space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {scenarioQuestion.scenario_question}
            </h3>
            <p className="text-gray-600 text-sm">
              {scenarioQuestion.imagination_guide}
            </p>
          </div>

          <div className="space-y-4">
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="随便说说就好，想到什么就写什么..."
              className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <div className="text-sm text-gray-500 text-center">
              没有标准答案，想到什么就写什么 ✨
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            disabled={isLoading}
          >
            跳过
          </button>

          <button
            onClick={handleSubmit}
            disabled={isLoading || !description.trim()}
            className={`
              flex items-center space-x-2 px-6 py-2 rounded-lg font-medium transition-all duration-200
              ${isLoading || !description.trim()
                ? 'bg-gray-300 cursor-not-allowed text-gray-500'
                : 'bg-green-500 hover:bg-green-600 text-white shadow-lg hover:shadow-xl'
              }
            `}
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>提交中...</span>
              </>
            ) : (
              <span>完成</span>
            )}
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default function CompleteAnswerButton({ threadId, userId, className = '' }: CompleteAnswerButtonProps) {
  const router = useRouter();
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showScenarioModal, setShowScenarioModal] = useState(false);
  const [isGeneratingQuestion, setIsGeneratingQuestion] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [scenarioQuestion, setScenarioQuestion] = useState(null);
  const [error, setError] = useState<string | null>(null);
  const [generationStatus, setGenerationStatus] = useState('');

  // 处理初始点击
  const handleInitialClick = () => {
    setShowConfirmModal(true);
    setError(null);
  };

  // 处理确认生成
  const handleConfirmGenerate = async () => {
    setShowConfirmModal(false);
    setIsGeneratingQuestion(true);
    setError(null);

    try {
      // 1. 生成场景问题
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/scenario/generate-question`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: threadId,
          user_id: userId,
        }),
      });

      if (!response.ok) {
        throw new Error('生成场景问题失败');
      }

      const questionData = await response.json();
      
      if (!questionData.success || !questionData.question_data) {
        throw new Error(questionData.message || '生成场景问题失败');
      }

      setScenarioQuestion(questionData.question_data);
      setShowScenarioModal(true);

    } catch (error) {
      console.error('生成场景问题失败:', error);
      setError(error instanceof Error ? error.message : '生成场景问题失败');
    } finally {
      setIsGeneratingQuestion(false);
    }
  };

  // 处理场景完成
  const handleScenarioComplete = async (scenarioDescription: string) => {
    setShowScenarioModal(false);
    setIsGeneratingReport(true);
    setGenerationStatus('正在生成您的专属答案之书...');

    try {
      // 1. 提交场景描述
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/scenario/submit-response`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: threadId,
          user_id: userId,
          scenario_description: scenarioDescription,
        }),
      });

      // 2. 生成报告
      const generateResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/report/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          thread_id: threadId,
          user_id: userId,
        }),
      });

      if (!generateResponse.ok) {
        throw new Error('启动报告生成失败');
      }

      const generateData = await generateResponse.json();
      
      if (!generateData.success || !generateData.task_id) {
        throw new Error(generateData.message || '启动报告生成失败');
      }

      // 3. 轮询报告状态
      console.log('开始轮询报告状态，task_id:', generateData.task_id);
      const reportId = await pollReportStatus(generateData.task_id);
      console.log('报告生成完成，reportId:', reportId);
      
      // 4. 跳转到报告页面
      console.log('跳转到报告页面，threadId:', threadId);
      router.push(`/chat/${threadId}/report`);

    } catch (error) {
      console.error('生成报告失败:', error);
      setError(error instanceof Error ? error.message : '生成报告失败');
      setIsGeneratingReport(false);
    }
  };

  // 轮询报告状态
  const pollReportStatus = async (taskId: string): Promise<string> => {
    const maxAttempts = 120;
    const interval = 3000;

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/report/status/${taskId}`);
        
        if (!response.ok) {
          throw new Error('获取报告状态失败');
        }

        const statusData = await response.json();

        if (statusData.status === 'completed') {
          if (!statusData.report_id) {
            throw new Error('报告完成但未返回报告ID');
          }
          return statusData.report_id;
        }

        if (statusData.status === 'failed') {
          throw new Error(statusData.error_message || '报告生成失败');
        }

        // 更新状态显示
        switch (statusData.status) {
          case 'generating':
            setGenerationStatus('正在深度分析您的对话...');
            break;
          default:
            setGenerationStatus('正在生成报告...');
        }

        await new Promise(resolve => setTimeout(resolve, interval));
      } catch (error) {
        if (attempt === maxAttempts - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, interval));
      }
    }

    throw new Error('报告生成超时');
  };

  const isLoading = isGeneratingQuestion || isGeneratingReport;

  return (
    <>
      <button
        onClick={handleInitialClick}
        disabled={isLoading}
        className={`
          flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200
          ${isLoading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-green-500 hover:bg-green-600 active:bg-green-700'
          }
          text-white shadow-lg hover:shadow-xl whitespace-nowrap
          ${className}
        `}
      >
        {isGeneratingQuestion ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>生成问题中...</span>
          </>
        ) : isGeneratingReport ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            <span>生成报告中...</span>
          </>
        ) : (
          <>
            <CheckCircle className="w-4 h-4" />
            <span>我已获得答案</span>
          </>
        )}
      </button>

      {/* 状态显示 */}
      {generationStatus && isGeneratingReport && (
        <div className="text-sm text-green-600 text-center mt-2 max-w-xs">
          {generationStatus}
        </div>
      )}

      {/* 错误显示 */}
      {error && (
        <div className="text-sm text-red-600 text-center mt-2 max-w-xs">
          {error}
        </div>
      )}

      {/* 确认弹框 */}
      <ConfirmationModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={handleConfirmGenerate}
        isLoading={isGeneratingQuestion}
      />

      {/* 场景问题弹框 */}
      <ScenarioModal
        isOpen={showScenarioModal}
        onClose={() => setShowScenarioModal(false)}
        onComplete={handleScenarioComplete}
        scenarioQuestion={scenarioQuestion}
        isLoading={isGeneratingReport}
      />
    </>
  );
}