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
      console.log('Starting to generate scenario question', { threadId, userId });

      // Reset state
      resetScenarioState();
      setGeneratingQuestion(true);
      setScenarioError(null);

      // 1. Generate scenario question
      const questionResponse = await ScenarioApiService.generateScenarioQuestion({
        thread_id: threadId,
        user_id: userId,
      });

      if (!questionResponse.success || !questionResponse.question_data) {
        throw new Error(questionResponse.message || 'Failed to generate scenario question');
      }

      console.log('Scenario question generated successfully', questionResponse.question_data);

      // 2. Set question data and show modal
      setCurrentQuestion(questionResponse.question_data);
      setIsScenarioModalOpen(true);

    } catch (error) {
      console.error('Failed to generate scenario question:', error);
      setScenarioError(error instanceof Error ? error.message : 'Failed to generate scenario question');
    } finally {
      setGeneratingQuestion(false);
    }
  };

  const handleScenarioComplete = async (scenarioDescription: string) => {
    try {
      console.log('Scenario description complete, starting letter report generation', { threadId, userId, scenarioDescription });

      // Reset report state
      resetReportState();
      setGenerating(true);
      setGenerationStatus('Generating your personalized letter...');

      // 1. Initiate letter report generation request (now includes scenario description)
      const generateResponse = await ReportApiService.generateReport({
        thread_id: threadId,
        user_id: userId,
      });

      if (!generateResponse.success || !generateResponse.task_id) {
        throw new Error(generateResponse.message || 'Failed to start report generation');
      }

      console.log('Report generation task started', { taskId: generateResponse.task_id });
      setGenerationStatus('Analyzing conversation content...');

      // 2. Poll report status, support streaming updates
      const reportId = await ReportApiService.pollReportStatus(
        generateResponse.task_id,
        (status) => {
          console.log('Report generation status update:', status);
          switch (status) {
            case 'generating':
              setGenerationStatus('Deeply analyzing your conversation...');
              break;
            default:
              setGenerationStatus('Generating report...');
          }
        },
        (progress) => {
          console.log('Report progress update:', progress);
          setCurrentProgress(progress);

          // Update status text based on completed sections
          if (progress.completed_sections && progress.completed_sections.length > 0) {
            const sectionNames = [
              'Strategic Autopsy',
              'Internal Struggle Analysis',
              'Catalyst Event Analysis',
              'Rebirth Strategy & Action Plan',
              'Action Anchor Forging'
            ];
            const completedCount = progress.completed_sections.length;
            const currentSectionName = progress.current_section && progress.current_section <= 5
              ? sectionNames[progress.current_section - 1]
              : '';

            if (progress.current_section && progress.current_section <= 5) {
              setGenerationStatus(`Generating Part ${progress.current_section}: ${currentSectionName}...`);
            } else {
              setGenerationStatus(`Completed ${completedCount}/5 sections`);
            }
          }
        }
      );

      console.log('Report generation complete', { reportId });
      setGenerationStatus('Fetching report...');

      // 3. Get complete report
      const reportResponse = await ReportApiService.getReport(reportId);
      
      if (!reportResponse.success) {
        throw new Error('Failed to fetch report');
      }

      console.log('Report fetched successfully', reportResponse.report);

      // 4. Set report data and navigate to report page
      setCurrentReport(reportResponse.report);
      setGenerating(false);
      
      // Navigate to report page
      router.push(`/chat/${threadId}/report`);

    } catch (error) {
      console.error('Failed to generate report:', error);
      setGenerationError(error instanceof Error ? error.message : 'Failed to generate report');
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
              <span>Generating question...</span>
            </>
          ) : isGenerating ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Generating report...</span>
            </>
          ) : (
            <>
              <CheckCircle className="w-5 h-5" />
              <span>I Got My Answer</span>
            </>
          )}
        </button>

        {/* Display status message */}
        {isGeneratingQuestion && (
          <div className="text-sm text-blue-600 text-center max-w-xs">
            Generating personalized scenario imagination question...
          </div>
        )}

        {isGenerating && generationStatus && (
          <div className="text-sm text-green-600 text-center max-w-xs">
            {generationStatus}
          </div>
        )}

        {/* Display error message */}
        {scenarioError && (
          <div className="text-sm text-red-600 text-center max-w-xs">
            {scenarioError}
          </div>
        )}
      </div>

      {/* Scenario question modal */}
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
