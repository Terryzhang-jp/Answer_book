/**
 * Scenario question modal component
 */

import React, { useState } from 'react';
import { X, Lightbulb, Send, Loader2 } from 'lucide-react';
import { useScenarioStore } from '../store/scenarioStore';
import { ScenarioApiService } from '../services/scenarioApi';

interface ScenarioQuestionModalProps {
  threadId: string;
  userId: string;
  isOpen: boolean;
  onClose: () => void;
  onComplete: (scenarioDescription: string) => void;
}

export default function ScenarioQuestionModal({
  threadId,
  userId,
  isOpen,
  onClose,
  onComplete
}: ScenarioQuestionModalProps) {
  const {
    currentQuestion,
    userScenarioDescription,
    isSubmittingResponse,
    submissionError,
    setUserScenarioDescription,
    setSubmittingResponse,
    setSubmissionError
  } = useScenarioStore();

  const [localDescription, setLocalDescription] = useState('');

  const handleSubmit = async () => {
    if (!localDescription.trim()) {
      setSubmissionError('Please enter your scenario description');
      return;
    }

    try {
      setSubmittingResponse(true);
      setSubmissionError(null);

      await ScenarioApiService.submitScenarioResponse({
        thread_id: threadId,
        user_id: userId,
        scenario_description: localDescription.trim()
      });

      setUserScenarioDescription(localDescription.trim());
      onComplete(localDescription.trim());
      onClose();

    } catch (error) {
      console.error('Failed to submit scenario description:', error);
      setSubmissionError(error instanceof Error ? error.message : 'Submission failed');
    } finally {
      setSubmittingResponse(false);
    }
  };

  if (!isOpen || !currentQuestion) {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-2">
            <Lightbulb className="w-6 h-6 text-yellow-500" />
            <h2 className="text-xl font-semibold text-gray-900">
              Imagine Your Future Scenario
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Core concept */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-800 text-center font-medium">
              💭 "Your future life is only the life you can imagine"
            </p>
          </div>

          {/* Scenario question */}
          <div className="text-center space-y-4">
            <h3 className="text-xl font-semibold text-gray-900">
              {currentQuestion.scenario_question}
            </h3>
            <p className="text-gray-600 text-sm">
              {currentQuestion.imagination_guide}
            </p>
          </div>

          {/* User input area */}
          <div className="space-y-4">
            <textarea
              value={localDescription}
              onChange={(e) => setLocalDescription(e.target.value)}
              placeholder="Just share freely, write whatever comes to mind..."
              className="w-full h-32 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              disabled={isSubmittingResponse}
            />
            <div className="text-sm text-gray-500 text-center">
              No right answers, just write whatever comes to mind ✨
            </div>
          </div>

          {/* Error message */}
          {submissionError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <p className="text-red-800 text-sm">{submissionError}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            disabled={isSubmittingResponse}
          >
            Skip
          </button>

          <button
            onClick={handleSubmit}
            disabled={isSubmittingResponse || !localDescription.trim()}
            className={`
              flex items-center space-x-2 px-6 py-2 rounded-lg font-medium transition-all duration-200
              ${isSubmittingResponse || !localDescription.trim()
                ? 'bg-gray-300 cursor-not-allowed text-gray-500'
                : 'bg-green-500 hover:bg-green-600 text-white shadow-lg hover:shadow-xl'
              }
            `}
          >
            {isSubmittingResponse ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Submitting...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Done</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
