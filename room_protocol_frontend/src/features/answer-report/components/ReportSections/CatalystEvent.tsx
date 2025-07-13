import React from 'react';
import { Lightbulb, ArrowRight, TrendingUp } from 'lucide-react';
import { CatalystEvent } from '../../types/report';

interface CatalystEventSectionProps {
  data: CatalystEvent;
}

export default function CatalystEventSection({ data }: CatalystEventSectionProps) {
  return (
    <div className="space-y-8">
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">第三部分：催化剂事件分析</h2>
        <p className="text-gray-600">详细重构对话中的关键转折点，看清观念如何被重塑</p>
      </div>

      {/* 初始观念 */}
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <div className="w-6 h-6 bg-gray-400 rounded-full mr-3 flex items-center justify-center">
            <span className="text-white text-sm font-bold">初</span>
          </div>
          <h3 className="text-xl font-semibold text-gray-900">初始观念</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-gray-400">
          <p className="text-gray-800 leading-relaxed">{data.initial_stance}</p>
        </div>
      </div>

      {/* 转化箭头 */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-2 text-blue-500">
          <ArrowRight className="w-8 h-8" />
          <span className="text-sm font-medium">催化剂触发</span>
          <ArrowRight className="w-8 h-8" />
        </div>
      </div>

      {/* 关键洞察 */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Lightbulb className="w-6 h-6 text-yellow-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">关键洞察</h3>
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

      {/* 转化箭头 */}
      <div className="flex justify-center">
        <div className="flex items-center space-x-2 text-green-500">
          <ArrowRight className="w-8 h-8" />
          <span className="text-sm font-medium">观念演化</span>
          <ArrowRight className="w-8 h-8" />
        </div>
      </div>

      {/* 观念演化 */}
      <div className="bg-green-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <TrendingUp className="w-6 h-6 text-green-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">观念演化</h3>
        </div>
        <div className="bg-white rounded-lg p-4 border-l-4 border-green-500">
          <p className="text-gray-800 leading-relaxed">{data.conceptual_evolution}</p>
        </div>
      </div>

      {/* 演化流程图 */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4 text-center">认知跃迁过程</h4>
        <div className="flex items-center justify-between">
          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-gray-400 rounded-full mx-auto mb-2 flex items-center justify-center">
              <span className="text-white font-bold">旧</span>
            </div>
            <p className="text-sm text-gray-600">原有假设</p>
          </div>
          
          <ArrowRight className="w-8 h-8 text-blue-500 mx-4" />
          
          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-yellow-500 rounded-full mx-auto mb-2 flex items-center justify-center">
              <Lightbulb className="w-8 h-8 text-white" />
            </div>
            <p className="text-sm text-gray-600">催化洞察</p>
          </div>
          
          <ArrowRight className="w-8 h-8 text-blue-500 mx-4" />
          
          <div className="text-center flex-1">
            <div className="w-16 h-16 bg-green-500 rounded-full mx-auto mb-2 flex items-center justify-center">
              <span className="text-white font-bold">新</span>
            </div>
            <p className="text-sm text-gray-600">新的框架</p>
          </div>
        </div>
      </div>

      {/* 核心原则提醒 */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "顿悟不是凭空产生的，它是一个准备好的头脑与一个恰当的洞察相遇的结果。"
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — 催化剂事件分析核心原则
        </p>
      </div>
    </div>
  );
}
