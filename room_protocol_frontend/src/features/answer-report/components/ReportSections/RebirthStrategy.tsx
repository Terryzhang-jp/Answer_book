import React from 'react';
import { Rocket, Target, Heart, TrendingUp, CheckSquare } from 'lucide-react';
import { RebirthStrategy } from '../../types/report';

interface RebirthStrategySectionProps {
  data: RebirthStrategy;
}

export default function RebirthStrategySection({ data }: RebirthStrategySectionProps) {
  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Part 4: Rebirth Strategy & Action Plan</h2>
        <p className="text-gray-600">Converging all analysis into specific, executable strategies and startup steps</p>
      </div>

      {/* Strategy Name */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-6">
        <div className="text-center">
          <Rocket className="w-12 h-12 text-purple-600 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Strategy Name</h3>
          <div className="bg-white rounded-lg p-4 border-2 border-purple-200">
            <h4 className="text-xl font-bold text-purple-600">{data.strategy_name}</h4>
          </div>
        </div>
      </div>

      {/* Core Logic and Benefits */}
      <div className="bg-blue-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Target className="w-6 h-6 text-blue-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Core Logic & Benefits</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
          <p className="text-gray-800 leading-relaxed">{data.core_logic}</p>
        </div>
      </div>

      {/* Personal Significance */}
      <div className="bg-pink-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Heart className="w-6 h-6 text-pink-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Personal Significance</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-pink-500">
          <p className="text-gray-800 leading-relaxed">{data.personal_significance}</p>
        </div>
      </div>

      {/* Success Analysis */}
      <div className="bg-green-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <TrendingUp className="w-6 h-6 text-green-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Success Analysis</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-green-500">
          <p className="text-gray-800 leading-relaxed">{data.success_analysis}</p>
        </div>
      </div>

      {/* Action Plan */}
      <div className="bg-orange-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <CheckSquare className="w-6 h-6 text-orange-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">Action Plan</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Goal */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-orange-500">
            <h4 className="font-semibold text-orange-600 mb-2">Clear Goal</h4>
            <p className="text-gray-800 text-sm">{data.action_plan.goal}</p>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-orange-500">
            <h4 className="font-semibold text-orange-600 mb-2">Defined Timeline</h4>
            <p className="text-gray-800 text-sm">{data.action_plan.timeline}</p>
          </div>
        </div>

        {/* Specific Steps */}
        <div className="bg-white rounded-lg p-4 border-l-4 border-orange-500 mb-4">
          <h4 className="font-semibold text-orange-600 mb-3">Specific Steps</h4>
          <div className="space-y-2">
            {data.action_plan.steps.map((step, index) => (
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 bg-orange-100 rounded-full flex items-center justify-center mr-3 mt-0.5">
                  <span className="text-orange-600 font-semibold text-xs">{index + 1}</span>
                </div>
                <p className="text-gray-800 text-sm">{step}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Success Criteria */}
        <div className="bg-white rounded-lg p-4 border-l-4 border-orange-500">
          <h4 className="font-semibold text-orange-600 mb-2">Success Criteria</h4>
          <p className="text-gray-800 text-sm">{data.action_plan.success_criteria}</p>
        </div>
      </div>

      {/* Core Principle Reminder */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "A good strategy not only tells you what to do, but also why to do it, and how to take the first step."
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — Core Principle of Rebirth Strategy & Action Plan
        </p>
      </div>
    </div>
  );
}
