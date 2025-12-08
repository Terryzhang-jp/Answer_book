import React from 'react';
import { Target, Search, AlertTriangle } from 'lucide-react';
import { StrategicAutopsy } from '../../types/report';

interface StrategicAutopsySectionProps {
  data: StrategicAutopsy;
}

export default function StrategicAutopsySection({ data }: StrategicAutopsySectionProps) {
  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Part 1: Strategic Autopsy</h2>
        <p className="text-gray-600">Dissecting vague, chaotic confusion into a clear, structured analysis framework with identified core issues</p>
      </div>

      {/* Problem Categorization */}
      <div className="bg-blue-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Target className="w-6 h-6 text-blue-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Problem Categorization</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
          <p className="text-gray-800 leading-relaxed">{data.problem_categorization}</p>
        </div>
      </div>

      {/* Dimensional Analysis */}
      <div className="bg-green-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Search className="w-6 h-6 text-green-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Dimensional Analysis</h3>
        </div>
        <div className="space-y-4">
          {data.dimensional_analysis.map((analysis, index) => (
            <div key={index} className="bg-white rounded-lg p-4 border-l-4 border-green-500">
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3 mt-1">
                  <span className="text-green-600 font-semibold text-sm">{index + 1}</span>
                </div>
                <p className="text-gray-800 leading-relaxed flex-1">{analysis}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Core Issue Diagnosis */}
      <div className="bg-red-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Core Issue Diagnosis</h3>
        </div>
        <div className="bg-white rounded-lg p-6 border-l-4 border-red-500">
          <blockquote className="text-xl font-medium text-gray-900 italic text-center">
            "{data.core_confusion}"
          </blockquote>
          <p className="text-sm text-gray-600 text-center mt-2">
            — The core issue of the problem
          </p>
        </div>
      </div>

      {/* Core Principle Reminder */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "A problem well-defined is a problem half-solved."
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — Core Principle of Strategic Autopsy
        </p>
      </div>
    </div>
  );
}
