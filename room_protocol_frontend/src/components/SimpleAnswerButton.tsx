'use client';

import React from 'react';
import { CheckCircle } from 'lucide-react';

interface SimpleAnswerButtonProps {
  threadId: string;
  userId: string;
  className?: string;
}

export default function SimpleAnswerButton({ threadId, userId, className = '' }: SimpleAnswerButtonProps) {
  const handleClick = () => {
    // 简单的提示，后续可以扩展
    alert('答案功能正在开发中，敬请期待！');
  };

  return (
    <button
      onClick={handleClick}
      className={`
        flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all duration-200
        bg-green-500 hover:bg-green-600 active:bg-green-700
        text-white shadow-lg hover:shadow-xl
        ${className}
      `}
    >
      <CheckCircle className="w-5 h-5" />
      <span>我已获得答案</span>
    </button>
  );
}