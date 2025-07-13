'use client';

import { useState, useEffect, useCallback } from 'react';

interface StreamingTextProps {
  text: string;
  speed?: number; // 每秒字符数
  onComplete?: () => void;
  className?: string;
  showSkipButton?: boolean; // 是否显示跳过按钮
  skipButtonText?: string; // 跳过按钮文本
}

export const StreamingText: React.FC<StreamingTextProps> = ({
  text,
  speed = 10, // 默认每秒20个字符
  onComplete,
  className = '',
  showSkipButton = false,
  skipButtonText = '一键显示'
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [isSkipped, setIsSkipped] = useState(false);

  // 跳过流式效果，直接显示全部内容
  const handleSkip = useCallback(() => {
    setIsSkipped(true);
    setDisplayedText(text);
    setIsComplete(true);
    onComplete?.();
  }, [text, onComplete]);

  useEffect(() => {
    if (!text) {
      setIsComplete(true);
      onComplete?.();
      return;
    }

    setDisplayedText('');
    setIsComplete(false);
    setIsSkipped(false);

    let currentIndex = 0;
    const intervalTime = 1000 / speed; // 毫秒间隔

    const timer = setInterval(() => {
      if (currentIndex < text.length && !isSkipped) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(timer);
        if (!isSkipped) {
          setIsComplete(true);
          onComplete?.();
        }
      }
    }, intervalTime);

    return () => clearInterval(timer);
  }, [text, speed, onComplete, isSkipped]);

  return (
    <span className="relative inline-block w-full">
      <span className={className}>
        {displayedText}
        {!isComplete && <span className="animate-pulse">|</span>}
      </span>

      {/* 跳过按钮 */}
      {showSkipButton && !isComplete && !isSkipped && (
        <button
          onClick={handleSkip}
          className="ml-2 px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
          title="跳过流式效果，直接显示全部内容"
        >
          {skipButtonText}
        </button>
      )}
    </span>
  );
};

interface StreamingCharacterResponseProps {
  message: {
    characterName: string;
    bodyLanguage?: string;
    thinking?: string;
    speaking?: string;
  };
  speed?: number;
  guestIndex?: number; // 嘉宾索引
  totalGuests?: number; // 总嘉宾数
  onComplete?: () => void; // 完成回调
  shouldStart?: boolean; // 是否应该开始
  showSkipButton?: boolean; // 是否显示跳过按钮
}

export const StreamingCharacterResponse: React.FC<StreamingCharacterResponseProps> = ({
  message,
  speed = 10,
  guestIndex = 0,
  totalGuests = 1,
  onComplete,
  shouldStart = true,
  showSkipButton = false
}) => {
  const [currentPhase, setCurrentPhase] = useState<'waiting' | 'bodyLanguage' | 'thinking' | 'speaking' | 'complete'>('waiting');
  const [isReady, setIsReady] = useState(false);
  const [isSkipped, setIsSkipped] = useState(false);

  // 一键显示所有内容
  const handleSkipAll = useCallback(() => {
    setIsSkipped(true);
    setCurrentPhase('complete');
    onComplete?.();
  }, [onComplete]);

  // 处理启动逻辑
  useEffect(() => {
    if (shouldStart && !isSkipped) {
      // 如果应该开始，立即开始（第一个嘉宾）或稍微延迟（后续嘉宾）
      const delay = guestIndex === 0 ? 0 : 500; // 后续嘉宾稍微延迟500ms
      const timer = setTimeout(() => {
        setIsReady(true);
        setCurrentPhase('bodyLanguage');
      }, delay);

      return () => clearTimeout(timer);
    }
  }, [shouldStart, guestIndex, isSkipped]);

  const handlePhaseComplete = useCallback(() => {
    if (isSkipped) return; // 如果已跳过，不处理阶段完成

    if (currentPhase === 'bodyLanguage') {
      setCurrentPhase('thinking');
    } else if (currentPhase === 'thinking') {
      setCurrentPhase('speaking');
    } else if (currentPhase === 'speaking') {
      setCurrentPhase('complete');
      // 当嘉宾完全完成时，通知父组件
      onComplete?.();
    }
  }, [currentPhase, onComplete, isSkipped]);

  // 如果没有肢体语言，直接从思考开始
  useEffect(() => {
    if (!message.bodyLanguage && currentPhase === 'bodyLanguage') {
      setCurrentPhase('thinking');
    }
  }, [message.bodyLanguage, currentPhase]);

  // 如果没有思考，从肢体语言直接到发言
  useEffect(() => {
    if (!message.thinking && currentPhase === 'thinking') {
      setCurrentPhase('speaking');
    }
  }, [message.thinking, currentPhase]);

  // 如果还在等待，显示等待状态
  if (!isReady) {
    return (
      <div className="space-y-3">
        <div className="bg-gray-100 border-l-4 border-gray-300 p-3 rounded">
          <div className="flex items-center">
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mr-2"></div>
            <span className="text-gray-500 text-sm">
              {shouldStart ?
                `正在准备 ${message.characterName}...` :
                `等待轮到 ${message.characterName}... (${guestIndex + 1}/${totalGuests})`
              }
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 relative">
      {/* 一键显示按钮 - 固定在右上角 */}
      {showSkipButton && currentPhase !== 'complete' && !isSkipped && (
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={handleSkipAll}
            className="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg shadow-lg transition-colors flex items-center space-x-2"
            title="跳过流式效果，直接显示全部内容"
          >
            <span>⚡</span>
            <span>一键显示</span>
          </button>
        </div>
      )}
      {/* 肢体语言 */}
      {message.bodyLanguage && (
        <div className="bg-purple-800/20 border-l-4 border-purple-400 p-3 rounded">
          <div className="flex items-center mb-2">
            <span className="text-black font-medium text-sm">🎭 肢体语言</span>
          </div>
          <div className="text-black text-sm italic leading-relaxed">
            {currentPhase === 'bodyLanguage' && !isSkipped ? (
              <StreamingText
                text={message.bodyLanguage}
                speed={speed}
                onComplete={handlePhaseComplete}
              />
            ) : (
              message.bodyLanguage
            )}
          </div>
        </div>
      )}

      {/* 内心思考 */}
      {message.thinking && (currentPhase === 'thinking' || currentPhase === 'speaking' || currentPhase === 'complete') && (
        <div className="bg-orange-800/20 border-l-4 border-orange-400 p-3 rounded">
          <div className="flex items-center mb-2">
            <span className="text-black font-medium text-sm">💭 内心思考</span>
          </div>
          <div className="text-black text-sm italic leading-relaxed">
            {currentPhase === 'thinking' && !isSkipped ? (
              <StreamingText
                text={message.thinking}
                speed={speed}
                onComplete={handlePhaseComplete}
              />
            ) : (currentPhase === 'speaking' || currentPhase === 'complete') ? (
              message.thinking
            ) : (
              ''
            )}
          </div>
        </div>
      )}

      {/* 发言 */}
      {(currentPhase === 'speaking' || currentPhase === 'complete') && (
        <div className="bg-gray-50 border-l-4 border-gray-400 p-3 rounded">
          <div className="flex items-center mb-2">
            <span className="text-gray-700 font-medium text-sm">💬 发言</span>
          </div>
          <div className="text-black text-sm leading-relaxed">
            {currentPhase === 'speaking' && !isSkipped ? (
              <StreamingText
                text={message.speaking || ''}
                speed={speed}
                onComplete={handlePhaseComplete}
              />
            ) : currentPhase === 'complete' ? (
              message.speaking
            ) : (
              ''
            )}
          </div>
        </div>
      )}
    </div>
  );
};
