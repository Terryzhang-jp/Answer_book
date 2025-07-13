import React from 'react';
import { Users, MessageSquare, Trophy } from 'lucide-react';
import { InternalStruggle } from '../../types/report';

interface InternalStruggleSectionProps {
  data: InternalStruggle;
}

export default function InternalStruggleSection({ data }: InternalStruggleSectionProps) {
  return (
    <div className="space-y-8">
      {/* 标题 */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">第二部分：内心博弈分析</h2>
        <p className="text-gray-600">将内心不可见的思想斗争，以客观、可视化的方式呈现</p>
      </div>

      {/* 博弈双方 */}
      <div className="bg-purple-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Users className="w-6 h-6 text-purple-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">博弈双方</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {data.contending_parties.map((party, index) => (
            <div key={index} className="bg-white rounded-lg p-4 border-2 border-purple-200">
              <div className="text-center">
                <div className={`w-12 h-12 rounded-full mx-auto mb-3 flex items-center justify-center ${
                  index === 0 ? 'bg-blue-100 text-blue-600' : 'bg-orange-100 text-orange-600'
                }`}>
                  <span className="font-bold text-lg">{index === 0 ? 'A' : 'B'}</span>
                </div>
                <h4 className="font-semibold text-gray-900">{party}</h4>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 证据清单 */}
      <div className="bg-indigo-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <MessageSquare className="w-6 h-6 text-indigo-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">证据清单</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 第一方证据 */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-blue-500">
            <h4 className="font-semibold text-blue-600 mb-3">{data.contending_parties[0]}</h4>
            <div className="space-y-3">
              {data.evidence_list.party1?.map((evidence, index) => (
                <div key={index} className="border-b border-gray-100 pb-2 last:border-b-0">
                  <div className="flex items-center mb-1">
                    <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                      {evidence.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-1">{evidence.content}</p>
                  <blockquote className="text-xs text-gray-500 italic border-l-2 border-gray-200 pl-2">
                    "{evidence.quote}"
                  </blockquote>
                </div>
              ))}
            </div>
          </div>

          {/* 第二方证据 */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-orange-500">
            <h4 className="font-semibold text-orange-600 mb-3">{data.contending_parties[1]}</h4>
            <div className="space-y-3">
              {data.evidence_list.party2?.map((evidence, index) => (
                <div key={index} className="border-b border-gray-100 pb-2 last:border-b-0">
                  <div className="flex items-center mb-1">
                    <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded">
                      {evidence.type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-1">{evidence.content}</p>
                  <blockquote className="text-xs text-gray-500 italic border-l-2 border-gray-200 pl-2">
                    "{evidence.quote}"
                  </blockquote>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 博弈结果 */}
      <div className="bg-yellow-50 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Trophy className="w-6 h-6 text-yellow-600 mr-3" />
          <h3 className="text-xl font-semibold text-gray-900">博弈结果</h3>
        </div>
        <div className="bg-white rounded-lg p-6 border-l-4 border-yellow-500">
          <p className="text-gray-800 leading-relaxed">{data.outcome}</p>
        </div>
      </div>

      {/* 核心原则提醒 */}
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <p className="text-center text-gray-700 italic">
          "你的行为和语言，是你内心价值观的投票。"
        </p>
        <p className="text-center text-sm text-gray-500 mt-1">
          — 内心博弈分析核心原则
        </p>
      </div>
    </div>
  );
}
