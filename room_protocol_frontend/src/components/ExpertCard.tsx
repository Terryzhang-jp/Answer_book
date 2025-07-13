'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, User } from 'lucide-react';
import { StreamingText } from './StreamingText';
import { CharacterResponse } from '@/types/api';

interface ExpertCardProps {
  expert: CharacterResponse;
  isActive: boolean;
  showAll: boolean;
  onComplete?: () => void;
}

export default function ExpertCard({ 
  expert, 
  isActive, 
  showAll, 
  onComplete 
}: ExpertCardProps) {
  const [currentPhase, setCurrentPhase] = useState<'waiting' | 'bodyLanguage' | 'thinking' | 'speaking' | 'complete'>('waiting');
  const [allComplete, setAllComplete] = useState(false);

  // 当showAll为true时，立即显示所有内容
  useEffect(() => {
    if (showAll && isActive) {
      setCurrentPhase('complete');
      setAllComplete(true);
      onComplete?.();
    }
  }, [showAll, isActive]); // 移除onComplete依赖

  // 当卡片激活时开始显示
  useEffect(() => {
    if (isActive && !showAll && currentPhase === 'waiting') {
      setCurrentPhase('bodyLanguage');
    }
  }, [isActive, showAll]); // 移除currentPhase依赖，避免循环

  const handlePhaseComplete = () => {
    if (showAll || allComplete) return;

    if (currentPhase === 'bodyLanguage') {
      setCurrentPhase('thinking');
    } else if (currentPhase === 'thinking') {
      setCurrentPhase('speaking');
    } else if (currentPhase === 'speaking') {
      setCurrentPhase('complete');
      setAllComplete(true);
      onComplete?.();
    }
  };

  if (!isActive) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-xl max-w-2xl w-full mx-4"
    >
      {/* 专家头部信息 */}
      <div className="flex items-center mb-4">
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mr-4">
          <Brain className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">{expert.character_name}</h3>
          <span className="text-sm text-gray-500 capitalize">{expert.character_role}</span>
        </div>
      </div>

      {/* 专家回复内容 */}
      <div className="space-y-4">
        {/* 肢体语言 */}
        {(currentPhase === 'bodyLanguage' || currentPhase === 'thinking' || currentPhase === 'speaking' || currentPhase === 'complete' || showAll || allComplete) && (
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <User className="w-4 h-4 text-gray-600 mr-2" />
              <span className="text-sm font-medium text-gray-700">肢体语言</span>
            </div>
            {showAll || allComplete || currentPhase !== 'bodyLanguage' ? (
              <p className="text-gray-800">{expert.body_language}</p>
            ) : (
              <StreamingText
                text={expert.body_language}
                speed={15}
                onComplete={handlePhaseComplete}
                className="text-gray-800"
              />
            )}
          </div>
        )}

        {/* 内心思考 */}
        {(currentPhase === 'thinking' || currentPhase === 'speaking' || currentPhase === 'complete' || showAll || allComplete) && (
          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <Brain className="w-4 h-4 text-blue-600 mr-2" />
              <span className="text-sm font-medium text-blue-700">内心思考</span>
            </div>
            {showAll || allComplete || currentPhase !== 'thinking' ? (
              <p className="text-blue-800">{expert.thinking}</p>
            ) : (
              <StreamingText
                text={expert.thinking}
                speed={12}
                onComplete={handlePhaseComplete}
                className="text-blue-800"
              />
            )}
          </div>
        )}

        {/* 发言内容 */}
        {(currentPhase === 'speaking' || currentPhase === 'complete' || showAll || allComplete) && (
          <div className="bg-green-50 rounded-lg p-4">
            <div className="flex items-center mb-2">
              <div className="w-4 h-4 bg-green-600 rounded-full mr-2"></div>
              <span className="text-sm font-medium text-green-700">发言</span>
            </div>
            {showAll || allComplete || currentPhase !== 'speaking' ? (
              <p className="text-green-800 text-lg leading-relaxed">{expert.speaking}</p>
            ) : (
              <StreamingText
                text={expert.speaking}
                speed={10}
                onComplete={handlePhaseComplete}
                className="text-green-800 text-lg leading-relaxed"
              />
            )}
          </div>
        )}
      </div>
    </motion.div>
  );
}
