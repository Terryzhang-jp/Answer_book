import React from 'react';
import { Lightbulb, ArrowRight, TrendingUp } from 'lucide-react';
import { CatalystEvent } from '../../types/report';

interface CatalystEventSectionProps {
  data: CatalystEvent;
}

export default function CatalystEventSection({ data }: CatalystEventSectionProps) {
  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Part 3: Catalyst Event Analysis</h2>
        <p className="text-gray-600">Detailed reconstruction of key turning points in the conversation, seeing how beliefs are reshaped</p>
      </div>

      {/* Initial Stance */}
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <div className="w-6 h-6 bg-gray-400 rounded-full mr-3 flex items-center justify-center">
            <span className="text-white text-sm font-bold">O</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">Initial Stance</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-gray-400">
          <p className="text-gray-800 leading-relaxed">{data.initial_stance}</p>
        </div>
      </div>

      {/* Transformation Arrow */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-2 text-blue-500">
          <ArrowRight className="w-8 h-8" />
          <span className="text-sm font-medium">Catalyst Triggered</span>
          <ArrowRight className="w-8 h-8" />
        </div>
      </div>

      {/* Key Insight */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Lightbulb className="w-6 h-6 text-yellow-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Key Insight</h3>
        </div>
        <div className="bg-white rounded-lg p-6 border-l-4 border-yellow-500">
          <div className="flex items-start">
            <div className="flex-shrink-0 w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mr-4">
              <Lightbulb className="w-6 h-6 text-yellow-600" />
            </div>
            <div>
              <p className="text-gray-800 leading-relaxed font-medium">{data.key_insight}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Transformation Arrow */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-2 text-green-500">
          <ArrowRight className="w-8 h-8" />
          <span className="text-sm font-medium">Belief Evolution</span>
          <ArrowRight className="w-8 h-8" />
        </div>
      </div>

      {/* Conceptual Evolution */}
      <div className="bg-green-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <TrendingUp className="w-6 h-6 text-green-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Conceptual Evolution</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-green-500">
          <p className="text-gray-800 leading-relaxed">{data.conceptual_evolution}</p>
        </div>
      </div>

      {/* Evolution Flow Chart */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 text-center">Cognitive Leap Process</h4>
        <div className="flex items-center justify-between">
          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-gray-400 rounded-full mx-auto mb-2 flex items-center justify-center">
              <span className="text-white font-bold">Old</span>
            </div>
            <p className="text-sm text-gray-600">Previous Assumption</p>
          </div>

          <ArrowRight className="w-8 h-8 text-blue-500 mx-4" />

          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-yellow-500 rounded-full mx-auto mb-2 flex items-center justify-center">
              <Lightbulb className="w-8 h-8 text-white" />
            </div>
            <p className="text-sm text-gray-600">Catalyst Insight</p>
          </div>

          <ArrowRight className="w-8 h-8 text-blue-500 mx-4" />

          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-green-500 rounded-full mx-auto mb-2 flex items-center justify-center">
              <span className="text-white font-bold">New</span>
            </div>
            <p className="text-sm text-gray-600">New Framework</p>
          </div>
        </div>
      </div>

      {/* Core Principle Reminder */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "Epiphanies don't appear from nowhere; they are the result of a prepared mind meeting the right insight."
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — Core Principle of Catalyst Event Analysis
        </p>
      </div>
    </div>
  );
}
