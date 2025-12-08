'use client';

import React from 'react';
import { CheckCircle, Clock, Loader2 } from 'lucide-react';
import { ReportData } from '../types/report';

interface StreamingProgressProps {
  progress: Partial<ReportData> | null;
  isGenerating: boolean;
  generationStatus: string;
}

const SECTION_NAMES = [
  'Part 1: Strategic Autopsy',
  'Part 2: Internal Struggle Analysis',
  'Part 3: Catalyst Event Analysis',
  'Part 4: Rebirth Strategy & Action Plan',
  'Part 5: Action Anchor Forging'
];

export default function StreamingProgress({ progress, isGenerating, generationStatus }: StreamingProgressProps) {
  if (!isGenerating && !progress) {
    return null;
  }

  const completedSections = progress?.completed_sections || [];
  const currentSection = progress?.current_section || 0;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
      <div className="flex items-center mb-4">
        <Loader2 className="w-5 h-5 text-blue-500 animate-spin mr-3" />
        <h3 className="text-lg font-semibold text-gray-900">Report Generation Progress</h3>
      </div>

      {/* Status text */}
      <p className="text-sm text-gray-600 mb-6">{generationStatus}</p>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Overall Progress</span>
          <span>{completedSections.length}/5 completed</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${(completedSections.length / 5) * 100}%` }}
          />
        </div>
      </div>

      {/* Section status */}
      <div className="space-y-3">
        {SECTION_NAMES.map((sectionName, index) => {
          const isCompleted = completedSections.includes(index);
          const isCurrent = currentSection === index + 1;
          const isPending = index >= completedSections.length && !isCurrent;

          return (
            <div key={index} className="flex items-center">
              <div className="flex-shrink-0 mr-3">
                {isCompleted ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
                ) : (
                  <Clock className="w-5 h-5 text-gray-300" />
                )}
              </div>

              <div className="flex-1">
                <p className={`text-sm font-medium ${
                  isCompleted ? 'text-green-600' :
                  isCurrent ? 'text-blue-600' :
                  'text-gray-400'
                }`}>
                  {sectionName}
                </p>

                {isCompleted && (
                  <p className="text-xs text-green-500 mt-1">✓ Completed</p>
                )}

                {isCurrent && (
                  <p className="text-xs text-blue-500 mt-1">Analyzing...</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Preview of completed sections */}
      {progress && completedSections.length > 0 && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-4">Completed Sections Preview</h4>
          <div className="space-y-4">
            {completedSections.map((sectionIndex) => (
              <div key={sectionIndex} className="bg-gray-50 rounded-lg p-4">
                <h5 className="text-sm font-medium text-gray-800 mb-2">
                  {SECTION_NAMES[sectionIndex]}
                </h5>
                <div className="text-xs text-gray-600">
                  {sectionIndex === 0 && progress.strategic_autopsy && (
                    <p>Core Issue: {progress.strategic_autopsy.core_confusion?.substring(0, 100)}...</p>
                  )}
                  {sectionIndex === 1 && progress.internal_struggle && (
                    <p>Contending Parties: {progress.internal_struggle.contending_parties?.join(' vs ')}</p>
                  )}
                  {sectionIndex === 2 && progress.catalyst_event && (
                    <p>Key Insight: {progress.catalyst_event.key_insight?.substring(0, 100)}...</p>
                  )}
                  {sectionIndex === 3 && progress.rebirth_strategy && (
                    <p>Strategy Name: {progress.rebirth_strategy.strategy_name}</p>
                  )}
                  {sectionIndex === 4 && progress.action_anchor && (
                    <p>Action Proverb: {progress.action_anchor.proverb}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
