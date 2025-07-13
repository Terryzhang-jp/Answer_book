import React from 'react';
import { Anchor, Zap, Quote } from 'lucide-react';
import { ActionAnchor } from '../../types/report';

interface ActionAnchorSectionProps {
  data: ActionAnchor;
}

export default function ActionAnchorSection({ data }: ActionAnchorSectionProps) {
  return (
    <div className="space-y-8">
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">第五部分：行动锚点锻造</h2>
        <p className="text-gray-600">将整个报告的智慧，浓缩成长期行动指南的个人箴言</p>
      </div>

      {/* 核心动词 */}
      <div className="bg-indigo-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Zap className="w-6 h-6 text-indigo-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">核心动词</h3>
        </div>
        <div className="bg-white rounded-lg p-6 border-l-4 border-indigo-500">
          <div className="text-center">
            <div className="w-20 h-20 bg-indigo-100 rounded-full mx-auto mb-4 flex items-center justify-center">
              <span className="text-2xl font-bold text-indigo-600">{data.core_verb}</span>
            </div>
            <p className="text-gray-600">最能代表策略精髓的行动词汇</p>
          </div>
        </div>
      </div>

      {/* 行动箴言 */}
      <div className="bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 rounded-lg p-8">
        <div className="flex items-center justify-center mb-6">
          <Anchor className="w-8 h-8 text-purple-600 mr-3" />
          <h3 className="text-2xl font-semibold text-gray-900">行动箴言</h3>
        </div>
        
        <div className="bg-white rounded-lg p-8 border-2 border-purple-200 shadow-lg">
          <div className="text-center">
            <Quote className="w-12 h-12 text-purple-400 mx-auto mb-4" />
            <blockquote className="text-3xl font-bold text-gray-900 mb-4 leading-relaxed">
              {data.proverb}
            </blockquote>
            <div className="w-24 h-1 bg-gradient-to-r from-purple-400 to-pink-400 mx-auto mb-4"></div>
            <p className="text-gray-600 italic">
              您的专属行动指南
            </p>
          </div>
        </div>
      </div>

      {/* 使用指南 */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 text-center">如何使用这句箴言</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full mx-auto mb-3 flex items-center justify-center">
              <span className="text-yellow-600 font-bold">1</span>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">每日提醒</h4>
            <p className="text-sm text-gray-600">将这句话设为手机壁纸或便签，每天提醒自己</p>
          </div>
          
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full mx-auto mb-3 flex items-center justify-center">
              <span className="text-yellow-600 font-bold">2</span>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">决策指南</h4>
            <p className="text-sm text-gray-600">在面临选择时，问问自己是否符合这个原则</p>
          </div>
          
          <div className="bg-white rounded-lg p-4 text-center">
            <div className="w-12 h-12 bg-yellow-100 rounded-full mx-auto mb-3 flex items-center justify-center">
              <span className="text-yellow-600 font-bold">3</span>
            </div>
            <h4 className="font-semibold text-gray-900 mb-2">行动检验</h4>
            <p className="text-sm text-gray-600">定期回顾自己的行动是否体现了这个核心理念</p>
          </div>
        </div>
      </div>

      {/* 最终祝福 */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-8 text-center">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">答案之书的祝福</h3>
        <p className="text-gray-700 leading-relaxed mb-4">
          通过这次深度对话分析，您已经找到了内心的答案。这句箴言将成为您前行路上的明灯，
          指引您在迷茫时找到方向，在困顿时获得力量。
        </p>
        <p className="text-lg font-medium text-purple-600">
          愿您带着这份智慧，勇敢地走向属于自己的未来。
        </p>
      </div>

      {/* 核心原则提醒 */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "语言塑造思想，思想指导行动。"
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — 行动锚点锻造核心原则
        </p>
      </div>
    </div>
  );
}
