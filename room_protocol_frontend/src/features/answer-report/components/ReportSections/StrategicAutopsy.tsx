import React from 'react';
import { Target, Search, AlertTriangle } from 'lucide-react';
import { StrategicAutopsy } from '../../types/report';

interface StrategicAutopsySectionProps {
  data: StrategicAutopsy;
}

export default function StrategicAutopsySection({ data }: StrategicAutopsySectionProps) {
  return (
    <div className="space-y-8">
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">第一部分：战略验尸</h2>
        <p className="text-gray-600">将模糊、混沌的困惑，解剖成结构清晰、有明确症结的分析框架</p>
      </div>

      {/* 问题定性 */}
      <div className="bg-blue-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Target className="w-6 h-6 text-blue-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">问题定性</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
          <p className="text-gray-800 leading-relaxed">{data.problem_categorization}</p>
        </div>
      </div>

      {/* 维度剖析 */}
      <div className="bg-green-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Search className="w-6 h-6 text-green-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">维度剖析</h3>
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

      {/* 症结诊断 */}
      <div className="bg-red-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">症结诊断</h3>
        </div>
        <div className="bg-white rounded-lg p-6 border-l-4 border-red-500">
          <blockquote className="text-xl font-medium text-gray-900 italic text-center">
            "{data.core_confusion}"
          </blockquote>
          <p className="text-sm text-gray-600 text-center mt-2">
            — 问题的核心症结
          </p>
        </div>
      </div>

      {/* 核心原则提醒 */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "问题被正确地定义，就等于解决了一半。"
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — 战略验尸核心原则
        </p>
      </div>
    </div>
  );
}
