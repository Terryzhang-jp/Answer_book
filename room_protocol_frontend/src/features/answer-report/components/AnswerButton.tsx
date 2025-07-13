import React, { useState } from 'react';
import { CheckCircle, Loader2 } from 'lucide-react';
import { useReportStore } from '../store/reportStore';
import { ReportApiService } from '../services/reportApi';
import { useRouter } from 'next/navigation';
import { useScenarioStore } from '../../scenario-question/store/scenarioStore';
import { ScenarioApiService } from '../../scenario-question/services/scenarioApi';
import ScenarioQuestionModal from '../../scenario-question/components/ScenarioQuestionModal';

interface AnswerButtonProps {
  threadId: string;
  userId: string;
  className?: string;
}

export default function AnswerButton({ threadId, userId, className = '' }: AnswerButtonProps) {
  const router = useRouter();
  const [isScenarioModalOpen, setIsScenarioModalOpen] = useState(false);

  const {
    isGenerating,
    generationStatus,
    currentProgress,
    setGenerating,
    setGenerationStatus,
    setGenerationError,
    setCurrentReport,
    setCurrentProgress,
    setReportVisible,
    resetReportState
  } = useReportStore();

  const {
    currentQuestion,
    isGeneratingQuestion,
    generationError: scenarioError,
    setCurrentQuestion,
    setGeneratingQuestion,
    setGenerationError: setScenarioError,
    setQuestionVisible,
    resetScenarioState
  } = useScenarioStore();

  const handleGenerateScenarioQuestion = async () => {
    try {
      console.log('开始生成场景问题', { threadId, userId });

      // 重置状态
      resetScenarioState();
      setGeneratingQuestion(true);
      setScenarioError(null);

      // 1. 生成场景问题
      const questionResponse = await ScenarioApiService.generateScenarioQuestion({
        thread_id: threadId,
        user_id: userId,
      });

      if (!questionResponse.success || !questionResponse.question_data) {
        throw new Error(questionResponse.message || '生成场景问题失败');
      }

      console.log('场景问题生成成功', questionResponse.question_data);

      // 2. 设置问题数据并显示模态框
      setCurrentQuestion(questionResponse.question_data);
      setIsScenarioModalOpen(true);

    } catch (error) {
      console.error('生成场景问题失败:', error);
      setScenarioError(error instanceof Error ? error.message : '生成场景问题失败');
    } finally {
      setGeneratingQuestion(false);
    }
  };

  const handleScenarioComplete = async (scenarioDescription: string) => {
    try {
      console.log('场景描述完成，开始生成信件报告', { threadId, userId, scenarioDescription });

      // 重置报告状态
      resetReportState();
      setGenerating(true);
      setGenerationStatus('正在生成您的专属信件...');

      // 1. 发起信件报告生成请求（现在包含场景描述）
      const generateResponse = await ReportApiService.generateReport({
        thread_id: threadId,
        user_id: userId,
      });

      if (!generateResponse.success || !generateResponse.task_id) {
        throw new Error(generateResponse.message || '启动报告生成失败');
      }

      console.log('报告生成任务已启动', { taskId: generateResponse.task_id });
      setGenerationStatus('正在分析对话内容...');

      // 2. 轮询报告状态，支持流式更新
      const reportId = await ReportApiService.pollReportStatus(
        generateResponse.task_id,
        (status) => {
          console.log('报告生成状态更新:', status);
          switch (status) {
            case 'generating':
              setGenerationStatus('正在深度分析您的对话...');
              break;
            default:
              setGenerationStatus('正在生成报告...');
          }
        },
        (progress) => {
          console.log('报告进度更新:', progress);
          setCurrentProgress(progress);

          // 根据完成的部分更新状态文本
          if (progress.completed_sections && progress.completed_sections.length > 0) {
            const sectionNames = [
              '战略验尸',
              '内心博弈分析',
              '催化剂事件分析',
              '重生策略与行动预案',
              '行动锚点锻造'
            ];
            const completedCount = progress.completed_sections.length;
            const currentSectionName = progress.current_section && progress.current_section <= 5
              ? sectionNames[progress.current_section - 1]
              : '';

            if (progress.current_section && progress.current_section <= 5) {
              setGenerationStatus(`正在生成第${progress.current_section}部分：${currentSectionName}...`);
            } else {
              setGenerationStatus(`已完成 ${completedCount}/5 个部分`);
            }
          }
        }
      );

      console.log('报告生成完成', { reportId });
      setGenerationStatus('正在获取报告...');

      // 3. 获取完整报告
      const reportResponse = await ReportApiService.getReport(reportId);
      
      if (!reportResponse.success) {
        throw new Error('获取报告失败');
      }

      console.log('报告获取成功', reportResponse.report);
      
      // 4. 设置报告数据并跳转到报告页面
      setCurrentReport(reportResponse.report);
      setGenerating(false);
      
      // 跳转到报告页面
      router.push(`/chat/${threadId}/report`);

    } catch (error) {
      console.error('生成报告失败:', error);
      setGenerationError(error instanceof Error ? error.message : '生成报告失败');
      setGenerating(false);
    }
  };

  return (
    <>
      <div className={`flex flex-col items-center space-y-2 ${className}`}>
        <button
          onClick={handleGenerateScenarioQuestion}
          disabled={isGeneratingQuestion || isGenerating}
          className={`
            flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
            ${isGeneratingQuestion || isGenerating
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-500 hover:bg-green-600 active:bg-green-700'
            }
            text-white shadow-lg hover:shadow-xl
          `}
        >
          {isGeneratingQuestion ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>生成问题中...</span>
            </>
          ) : isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>生成报告中...</span>
            </>
          ) : (
            <>
              <CheckCircle className="w-5 h-5" />
              <span>我已获得答案</span>
            </>
          )}
        </button>

        {/* 显示状态信息 */}
        {isGeneratingQuestion && (
          <div className="text-sm text-blue-600 text-center max-w-xs">
            正在为您生成个性化的场景想象问题...
          </div>
        )}

        {isGenerating && generationStatus && (
          <div className="text-sm text-green-600 text-center max-w-xs">
            {generationStatus}
          </div>
        )}

        {/* 显示错误信息 */}
        {scenarioError && (
          <div className="text-sm text-red-600 text-center max-w-xs">
            {scenarioError}
          </div>
        )}
      </div>

      {/* 场景问题模态框 */}
      <ScenarioQuestionModal
        threadId={threadId}
        userId={userId}
        isOpen={isScenarioModalOpen}
        onClose={() => setIsScenarioModalOpen(false)}
        onComplete={handleScenarioComplete}
      />
    </>
  );
}
