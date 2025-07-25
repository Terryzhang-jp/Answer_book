'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Plus, Settings } from 'lucide-react';
import { ApiService } from '@/services/api';
import { useConversationStore } from '@/store/conversation';
import BookOfAnswers from '@/components/BookOfAnswers';
import CompleteAnswerButton from '@/components/CompleteAnswerButton';

import { useReportStore } from '@/features/answer-report/store/reportStore';

// 专家颜色映射
const getExpertColor = (expertName: string): string => {
  const colorMap: Record<string, string> = {
    '苏格拉底': 'blue',
    '孔子': 'amber',
    '爱因斯坦': 'green',
    '达芬奇': 'purple',
    '尼采': 'red',
    '佛陀': 'orange',
    '马克思': 'indigo',
    '亚当·斯密': 'teal',
    '马斯克': 'cyan',
    '乔布斯': 'gray',
  };
  return colorMap[expertName] || 'slate';
};

// Turn类型定义
interface ExpertMessage {
  id: number;
  name: string;
  bodyLanguage: string;
  thinking: string;
  speaking: string;
  color: string;
}

interface Turn {
  id: number;
  userQuestion: string;
  expertResponses: ExpertMessage[];
}

export default function ChatPage() {
  const router = useRouter();
  const [turns, setTurns] = useState<Turn[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const {
    messages,
    currentThreadId,
    roomAnnouncement,
    conversationAnalysis,
    error,
    addUserMessage,
    addResponse,
    setLoading,
    setError,
    clearConversation,
    startNewDiscussion,
  } = useConversationStore();

  // 报告生成状态
  const { isGenerating, generationStatus } = useReportStore();

  // 如果没有对话，重定向到首页
  useEffect(() => {
    if (!currentThreadId && messages.length === 0) {
      router.push('/');
    }
  }, [currentThreadId, messages.length, router]);

  // 将store中的messages转换为Turn格式
  useEffect(() => {
    const userMessages = messages.filter(msg => msg.type === 'user');
    const expertMessages = messages.filter(msg => msg.type === 'expert' || msg.type === 'system');

    // 按时间戳分组专家消息
    const expertsByTimestamp: Record<string, typeof expertMessages> = {};
    expertMessages.forEach(msg => {
      if (!expertsByTimestamp[msg.timestamp]) {
        expertsByTimestamp[msg.timestamp] = [];
      }
      expertsByTimestamp[msg.timestamp].push(msg);
    });

    // 创建Turn数组
    const newTurns: Turn[] = [];
    userMessages.forEach((userMsg, index) => {
      // 找到对应的专家回复（通过时间戳或索引匹配）
      const correspondingExperts = Object.values(expertsByTimestamp)[index] || [];
      
      const expertResponses: ExpertMessage[] = correspondingExperts.map((expertMsg, expertIndex) => ({
        id: parseInt(expertMsg.id) + expertIndex,
        name: expertMsg.characterName || '未知专家',
        bodyLanguage: expertMsg.bodyLanguage || '',
        thinking: expertMsg.thinking || '',
        speaking: expertMsg.speaking || expertMsg.content,
        color: getExpertColor(expertMsg.characterName || ''),
      }));

      newTurns.push({
        id: parseInt(userMsg.id),
        userQuestion: userMsg.content,
        expertResponses,
      });
    });

    setTurns(newTurns);
  }, [messages]);

  const handleSendMessage = async (question: string) => {
    try {
      setIsLoading(true);
      setLoading(true);
      setError(null);

      // 添加用户消息到store
      addUserMessage(question);

      // 调用API
      const response = currentThreadId 
        ? await ApiService.askQuestion({
            question: question.trim(),
            user_id: 'user_' + Date.now(),
            thread_id: currentThreadId,
          })
        : await ApiService.createRoom({
            question: question.trim(),
            user_id: 'user_' + Date.now(),
          });

      // 添加响应到store
      addResponse(response);

    } catch (error) {
      console.error('提问失败:', error);
      setError(error instanceof Error ? error.message : '提问失败，请重试');
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  const handleBackToHome = () => {
    clearConversation();
    router.push('/');
  };

  const handleStartNewDiscussion = () => {
    if (messages.length > 0) {
      const confirmed = window.confirm('确定要开启新的讨论吗？当前的对话记录将被清空。');
      if (!confirmed) return;
    }

    startNewDiscussion();
    router.push('/');
  };

  return (
    <div className="h-screen w-screen bg-gradient-to-br from-slate-900 via-gray-900 to-zinc-900 relative overflow-hidden">
      {/* 书本主体 - 占满整个屏幕 */}
      <div className="relative w-full h-full overflow-hidden">
        {/* 页面内容区域 */}
        <div className="relative z-10 w-full h-full">{/* 去除左边距 */}

              {/* 顶部导航 */}
              <div className="absolute top-4 left-4 z-40 flex space-x-2">
                <button
                  onClick={handleBackToHome}
                  className="flex items-center space-x-2 px-3 py-2 bg-gray-100/80 backdrop-blur-sm border border-gray-200 rounded-lg text-gray-700 hover:text-gray-900 hover:bg-gray-200/80 transition-colors shadow-sm font-serif text-sm"
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>返回首页</span>
                </button>

                <button
                  onClick={handleStartNewDiscussion}
                  disabled={isLoading}
                  className="flex items-center space-x-2 px-3 py-2 bg-green-500/90 hover:bg-green-600/90 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors shadow-sm font-serif text-sm"
                >
                  <Plus className="w-4 h-4" />
                  <span>新讨论</span>
                </button>

                {/* 我已获得答案按钮 */}
                {currentThreadId && turns.length > 0 && (
                  <CompleteAnswerButton
                    threadId={currentThreadId}
                    userId={currentThreadId ? `user_${currentThreadId}` : undefined}
                    className="whitespace-nowrap bg-blue-600 hover:bg-blue-700 text-white font-serif transition-all duration-200 text-sm shadow-sm backdrop-blur-sm px-3 py-2"
                  />
                )}
              </div>


              {/* 错误提示 */}
              {error && (
                <div className="absolute top-16 left-1/2 transform -translate-x-1/2 z-40 bg-red-100/90 border border-red-300 rounded-lg p-3 shadow-lg backdrop-blur-sm">
                  <p className="text-red-800 text-sm font-serif">{error}</p>
                </div>
              )}

          {/* 书本组件 */}
          <BookOfAnswers
            turns={turns}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            conversationAnalysis={conversationAnalysis}
            roomAnnouncement={roomAnnouncement || undefined}
          />
        </div>
      </div>

      {/* 报告生成弹框 */}
      {isGenerating && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center">
            <div className="mb-4">
              <div className="w-16 h-16 mx-auto mb-4 bg-blue-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">正在生成报告</h3>
              <p className="text-gray-600 text-sm">
                {generationStatus || '正在为您生成专属的答案之书信件...'}
              </p>
            </div>
            <div className="text-xs text-gray-500">
              请稍候，这可能需要几分钟时间
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
