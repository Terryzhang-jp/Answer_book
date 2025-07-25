'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, BarChart3, Target, User, TrendingUp, Lightbulb, MessageSquare, Brain, ChevronDown, ChevronRight } from 'lucide-react';
import { ConversationAnalysis } from '@/types/api';
import { useState } from 'react';

interface AnalysisModalProps {
  isOpen: boolean;
  onClose: () => void;
  analysis: ConversationAnalysis | null;
}

export default function AnalysisModal({ isOpen, onClose, analysis }: AnalysisModalProps) {
  const [expandedExperts, setExpandedExperts] = useState<Set<string>>(new Set());

  const toggleExpertExpansion = (expertName: string) => {
    setExpandedExperts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(expertName)) {
        newSet.delete(expertName);
      } else {
        newSet.add(expertName);
      }
      return newSet;
    });
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          transition={{ duration: 0.3 }}
          className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
        >
          {/* 头部 */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">回顾分析</h2>
                <p className="text-sm text-gray-500">深度洞察与对话分析</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* 内容区域 */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-80px)]">
            {analysis ? (
              <div className="space-y-6">
                {/* 问题分析 */}
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
                  <h3 className="text-gray-900 font-semibold mb-3 flex items-center">
                    <Target className="w-5 h-5 mr-2 text-blue-600" />
                    问题分析
                  </h3>
                  <p className="text-gray-800 text-sm leading-relaxed">
                    {analysis.user_question_analysis}
                  </p>
                </div>

                {/* 专家邀请理由 */}
                {analysis.expert_selection_reason && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5">
                    <h3 className="text-gray-900 font-semibold mb-3 flex items-center">
                      <User className="w-5 h-5 mr-2 text-blue-600" />
                      专家邀请理由
                    </h3>
                    <div className="text-gray-800 text-sm leading-relaxed whitespace-pre-line">
                      {analysis.expert_selection_reason}
                    </div>
                  </div>
                )}

                {/* 对话纪要 */}
                {analysis.conversation_timeline && analysis.conversation_timeline.length > 0 && (
                  <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
                    <h3 className="text-gray-900 font-semibold mb-3 flex items-center">
                      <MessageSquare className="w-5 h-5 mr-2 text-gray-600" />
                      对话纪要
                    </h3>
                    <div className="space-y-3">
                      {analysis.conversation_timeline.map((entry, index) => (
                        <div key={index} className="text-sm leading-relaxed">
                          <span className={`font-medium ${
                            entry.speaker === '用户' ? 'text-blue-600' : 'text-green-600'
                          }`}>
                            • {entry.speaker}
                          </span>
                          <span className="text-gray-700 ml-1">
                            {entry.action}：{entry.content}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 对话演进 */}
                <div className="bg-gray-50 border border-gray-200 rounded-xl p-5">
                  <h3 className="text-gray-900 font-semibold mb-3 flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2 text-green-600" />
                    对话演进
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-gray-700 text-sm font-medium mb-1">讨论深度:</p>
                      <p className="text-gray-800 text-sm">{analysis.conversation_evolution.discussion_depth}</p>
                    </div>
                    {analysis.conversation_evolution.topic_progression.length > 0 && (
                      <div>
                        <p className="text-gray-700 text-sm font-medium mb-1">话题演进:</p>
                        <ul className="text-gray-800 text-sm space-y-1">
                          {analysis.conversation_evolution.topic_progression.map((topic, index) => (
                            <li key={index} className="text-sm">• {topic}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {/* 专家洞察 */}
                {analysis.all_experts_insights.map((expert) => (
                  <div key={expert.expert_name} className="bg-white border border-gray-200 rounded-xl shadow-sm">
                    <button
                      onClick={() => toggleExpertExpansion(expert.expert_name)}
                      className="w-full p-5 text-left hover:bg-gray-50 transition-colors rounded-xl"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-3">
                            <Brain className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="text-gray-900 font-semibold">{expert.expert_name}</h3>
                            <p className="text-gray-600 text-sm">
                              {expert.is_current ? '当前专家' : '历史专家'} • {expert.total_contributions} 次贡献
                            </p>
                          </div>
                        </div>
                        {expandedExperts.has(expert.expert_name) ? (
                          <ChevronDown className="w-5 h-5 text-gray-600" />
                        ) : (
                          <ChevronRight className="w-5 h-5 text-gray-600" />
                        )}
                      </div>
                    </button>

                    {expandedExperts.has(expert.expert_name) && (
                      <div className="px-5 pb-5 space-y-4">
                        {/* 专业领域 */}
                        {expert.expertise_areas.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-sm font-medium mb-2">专业领域:</p>
                            <div className="flex flex-wrap gap-2">
                              {expert.expertise_areas.map((area, areaIndex) => (
                                <span key={areaIndex} className="bg-blue-100 text-blue-800 text-xs px-3 py-1 rounded-full">
                                  {area}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* 核心观点 */}
                        {expert.key_insights.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-sm font-medium mb-2">核心观点:</p>
                            <ul className="text-gray-800 text-sm space-y-1">
                              {expert.key_insights.map((insight, insightIndex) => (
                                <li key={insightIndex}>• {insight}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* 帮助要点 */}
                        {expert.helpful_points.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-sm font-medium mb-2 flex items-center">
                              <Lightbulb className="w-4 h-4 mr-1 text-yellow-500" />
                              可帮助的要点:
                            </p>
                            <ul className="text-gray-800 text-sm space-y-1">
                              {expert.helpful_points.map((point, pointIndex) => (
                                <li key={pointIndex}>• {point}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}

                {/* 建议方向 */}
                {analysis.suggested_directions.length > 0 && (
                  <div className="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl p-5">
                    <h3 className="text-gray-900 font-semibold mb-3 flex items-center">
                      <Lightbulb className="w-5 h-5 mr-2 text-green-600" />
                      建议方向
                    </h3>
                    <ul className="text-gray-800 text-sm space-y-2">
                      {analysis.suggested_directions.map((direction, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-green-600 mr-2">•</span>
                          <span>{direction}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <BarChart3 className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500 text-lg">暂无分析数据</p>
                <p className="text-gray-400 text-sm mt-2">开始对话后将显示详细分析</p>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}