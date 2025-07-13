'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, FastForward, ChevronLeft, ChevronRight } from 'lucide-react';
import { CharacterResponse } from '@/types/api';
import ExpertCard from './ExpertCard';

interface ExpertResponseModalProps {
  isOpen: boolean;
  experts: CharacterResponse[];
  currentIndex: number;
  showAll: boolean;
  isAutoPlaying: boolean;
  onClose: () => void;
  onNext: () => void;
  onShowAll: () => void;
}

export default function ExpertResponseModal({
  isOpen,
  experts,
  currentIndex,
  showAll,
  isAutoPlaying,
  onClose,
  onNext,
  onShowAll
}: ExpertResponseModalProps) {
  const [localCurrentIndex, setLocalCurrentIndex] = useState(currentIndex);
  const autoPlayTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 同步外部currentIndex
  useEffect(() => {
    setLocalCurrentIndex(currentIndex);
  }, [currentIndex]);

  // 处理专家回复完成
  const handleExpertComplete = () => {
    if (showAll) return;

    // 清理之前的定时器，避免冲突
    if (autoPlayTimerRef.current) {
      clearTimeout(autoPlayTimerRef.current);
      autoPlayTimerRef.current = null;
    }

    // 如果不是最后一个专家，设置2秒后自动切换
    if (localCurrentIndex < experts.length - 1 && isAutoPlaying) {
      autoPlayTimerRef.current = setTimeout(() => {
        setLocalCurrentIndex(prev => prev + 1);
        onNext();
      }, 2000);
    } else if (localCurrentIndex >= experts.length - 1) {
      // 所有专家完成，2秒后自动关闭
      autoPlayTimerRef.current = setTimeout(() => {
        onClose();
      }, 2000);
    }
  };

  // 清理定时器
  useEffect(() => {
    return () => {
      if (autoPlayTimerRef.current) {
        clearTimeout(autoPlayTimerRef.current);
      }
    };
  }, []);

  // 处理键盘事件
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (!isOpen) return;

      switch (e.key) {
        case 'Escape':
          onClose();
          break;
        case 'ArrowRight':
          if (localCurrentIndex < experts.length - 1) {
            setLocalCurrentIndex(prev => prev + 1);
            onNext();
          }
          break;
        case 'ArrowLeft':
          if (localCurrentIndex > 0) {
            setLocalCurrentIndex(prev => prev - 1);
          }
          break;
        case ' ':
          e.preventDefault();
          onShowAll();
          break;
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyPress);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyPress);
    };
  }, [isOpen, localCurrentIndex, experts.length, onClose, onNext, onShowAll]);

  if (!isOpen || experts.length === 0) {
    return null;
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={(e) => {
          if (e.target === e.currentTarget) {
            onClose();
          }
        }}
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="relative max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* 顶部控制栏 */}
          <div className="bg-white rounded-t-2xl p-4 border-b border-gray-200 sticky top-0 z-10">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {/* 一键显示全部按钮 */}
                {!showAll && (
                  <button
                    onClick={onShowAll}
                    className="flex items-center space-x-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
                  >
                    <FastForward className="w-4 h-4" />
                    <span>一键显示全部</span>
                  </button>
                )}

                {/* 进度指示器 */}
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">
                    {showAll ? `显示全部 (${experts.length}位专家)` : `${localCurrentIndex + 1} / ${experts.length}`}
                  </span>
                </div>
              </div>

              {/* 关闭按钮 */}
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
            </div>

            {/* 导航按钮 */}
            {!showAll && experts.length > 1 && (
              <div className="flex items-center justify-center space-x-4 mt-4">
                <button
                  onClick={() => {
                    if (localCurrentIndex > 0) {
                      setLocalCurrentIndex(prev => prev - 1);
                    }
                  }}
                  disabled={localCurrentIndex === 0}
                  className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>上一位</span>
                </button>

                <button
                  onClick={() => {
                    if (localCurrentIndex < experts.length - 1) {
                      setLocalCurrentIndex(prev => prev + 1);
                      onNext();
                    }
                  }}
                  disabled={localCurrentIndex >= experts.length - 1}
                  className="flex items-center space-x-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                >
                  <span>下一位</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* 专家卡片内容 */}
          <div className="bg-white rounded-b-2xl p-6">
            {showAll ? (
              // 显示所有专家
              <div className="space-y-6">
                {experts.map((expert, index) => (
                  <ExpertCard
                    key={`${expert.character_name}-${index}`}
                    expert={expert}
                    isActive={true}
                    showAll={true}
                    onComplete={() => {}}
                  />
                ))}
              </div>
            ) : (
              // 逐一显示专家
              <div className="flex justify-center">
                <ExpertCard
                  expert={experts[localCurrentIndex]}
                  isActive={true}
                  showAll={false}
                  onComplete={handleExpertComplete}
                />
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
