'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  ArrowLeft,
  MessageCircle,
  Brain,
  User,
  Settings,
  RotateCcw,
  Plus,
  BarChart3,
  ChevronDown,
  ChevronRight,
  Lightbulb,
  Target,
  TrendingUp,
  MessageSquare
} from 'lucide-react';
import { ApiService } from '@/services/api';
import { useConversationStore } from '@/store/conversation';
import InsightDisplay from '@/components/InsightDisplay';
import AnswerButton from '@/features/answer-report/components/AnswerButton';
import StreamingProgress from '@/features/answer-report/components/StreamingProgress';
import { useReportStore } from '@/features/answer-report/store/reportStore';
import { StreamingCharacterResponse } from '@/components/StreamingText';

export default function ChatPage() {
  const router = useRouter();
  const [newQuestion, setNewQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedExperts, setExpandedExperts] = useState<Set<string>>(new Set());

  const [sequentialMode, setSequentialMode] = useState(true); // 顺序显示模式，默认开启
  const [completedGuests, setCompletedGuests] = useState<Set<string>>(new Set()); // 已完成的嘉宾
  
  const {
    messages,
    currentThreadId,
    roomAnnouncement,
    conversationAnalysis,
    isLoading: storeLoading,
    error,
    insightDisplay,
    addUserMessage,
    addResponse,
    setLoading,
    setError,
    clearConversation,
    startNewDiscussion,
    startInsightDisplay,
    resetInsightDisplay,
    completeInsightDisplay,
    skipInsightDisplay
  } = useConversationStore();

  // 报告生成状态
  const {
    isGenerating,
    generationStatus,
    currentProgress
  } = useReportStore();

  // 如果没有对话，重定向到首页
  useEffect(() => {
    if (!currentThreadId && messages.length === 0) {
      router.push('/');
    }
  }, [currentThreadId, messages.length, router]);



  const handleNewQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newQuestion.trim() || isLoading) return;

    try {
      setIsLoading(true);
      setLoading(true);
      setError(null);

      addUserMessage(newQuestion);

      // 暂时禁用insight生成
      // console.log('重置insight状态，开始新的insight生成');
      // resetInsightDisplay(); // 先重置状态

      // console.log('启动insight显示');
      // startInsightDisplay('', ''); // 直接启动显示状态

      const response = await ApiService.askQuestion({
        question: newQuestion.trim(),
        user_id: 'user_' + Date.now(),
        thread_id: currentThreadId || undefined, // 传递当前的thread_id以继续对话
      });

      // API调用完成，关闭insight显示（已禁用）
      // console.log('API调用完成，关闭insight显示');
      // completeInsightDisplay();

      addResponse(response);
      setNewQuestion('');
      // 清理完成状态，为新的对话做准备
      setCompletedGuests(new Set());
    } catch (error) {
      console.error('提问失败:', error);
      setError(error instanceof Error ? error.message : '提问失败，请重试');
    } finally {
      setIsLoading(false);
      setLoading(false);
      // 注意：不在这里关闭潜意识探测，让它自然完成
    }
  };

  const handleBackToHome = () => {
    clearConversation();
    router.push('/');
  };

  const handleStartNewDiscussion = () => {
    // 确认用户是否要开启新讨论
    if (messages.length > 0) {
      const confirmed = window.confirm('确定要开启新的讨论吗？当前的对话记录将被清空。');
      if (!confirmed) return;
    }

    // 清空所有数据并跳转到首页
    startNewDiscussion();
    router.push('/');
  };



  // Insight显示完成处理
  const handleInsightComplete = () => {
    console.log('Insight显示完成');
    completeInsightDisplay();
  };

  // Insight显示跳过处理
  const handleInsightSkip = () => {
    console.log('用户跳过Insight显示');
    skipInsightDisplay();
  };

  // 切换专家展开状态
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

  // 获取所有消息并按时间排序（用于统一时间线）
  const getAllMessagesInOrder = () => {
    return [...messages].sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  };

  // 获取不同类型的消息（用于右栏显示）
  const userMessages = messages.filter(msg => msg.type === 'user');
  const systemMessages = messages.filter(msg => msg.type === 'system');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* 房间宣告栏 - 顶部全宽 */}
      <AnimatePresence>
        {roomAnnouncement && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="bg-gradient-to-r from-amber-600/30 to-orange-600/30 border-b border-amber-500/50 p-4 shadow-lg"
          >
            <div className="max-w-7xl mx-auto text-center">
              <div className="flex items-center justify-center mb-2">
                <Settings className="w-5 h-5 text-amber-300 mr-2" />
                <span className="text-sm text-amber-300 font-semibold">[房间宣告 - Centered]</span>
              </div>
              <p className="text-amber-100 font-medium text-lg">{roomAnnouncement}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 主要内容区域 - 三栏布局 */}
      <div className={`flex ${roomAnnouncement ? 'h-[calc(100vh-80px)]' : 'h-screen'}`}>
        {/* 左栏 - 分析展示区域 (30%) */}
        <div className="w-[30%] bg-white border-r border-gray-300 p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold text-black mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-gray-600" />
            对话分析
          </h2>

          <div className="space-y-4">
            {/* 流式报告生成进度 */}
            {isGenerating && (
              <StreamingProgress
                progress={currentProgress}
                isGenerating={isGenerating}
                generationStatus={generationStatus}
              />
            )}

            {conversationAnalysis && !isGenerating ? (
              <>
                {/* 用户问题分析 */}
                <div className="bg-white border border-gray-300 rounded-xl p-4">
                  <h3 className="text-black font-semibold mb-2 flex items-center">
                    <Target className="w-4 h-4 mr-2" />
                    问题分析
                  </h3>
                  <p className="text-gray-800 text-sm leading-relaxed">
                    {conversationAnalysis.user_question_analysis}
                  </p>
                </div>

                {/* 专家邀请理由 */}
                {conversationAnalysis.expert_selection_reason && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5 shadow-sm">
                    <h3 className="text-black font-semibold mb-3 flex items-center">
                      <User className="w-5 h-5 mr-2 text-blue-600" />
                      专家邀请理由
                    </h3>
                    <div className="text-gray-800 text-sm leading-relaxed whitespace-pre-line">
                      {conversationAnalysis.expert_selection_reason}
                    </div>
                  </div>
                )}

                {/* 对话纪要 */}
                {conversationAnalysis.conversation_timeline && conversationAnalysis.conversation_timeline.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-black font-semibold mb-3 flex items-center">
                      <MessageSquare className="w-4 h-4 mr-2 text-gray-600" />
                      对话纪要
                    </h3>
                    <div className="space-y-2">
                      {conversationAnalysis.conversation_timeline.map((entry, index) => (
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
                <div className="bg-white border border-gray-300 rounded-xl p-4">
                  <h3 className="text-black font-semibold mb-2 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    对话演进
                  </h3>
                  <div className="space-y-2">
                    <div>
                      <p className="text-gray-700 text-xs font-medium mb-1">讨论深度:</p>
                      <p className="text-gray-800 text-sm">{conversationAnalysis.conversation_evolution.discussion_depth}</p>
                    </div>
                    {conversationAnalysis.conversation_evolution.topic_progression.length > 0 && (
                      <div>
                        <p className="text-gray-700 text-xs font-medium mb-1">话题演进:</p>
                        <ul className="text-gray-800 text-sm space-y-1">
                          {conversationAnalysis.conversation_evolution.topic_progression.map((topic, index) => (
                            <li key={index} className="text-xs">• {topic}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {/* 专家洞察 - 按嘉宾分组折叠 */}
                {conversationAnalysis.all_experts_insights.map((expert) => (
                  <div key={expert.expert_name} className="bg-white border border-gray-300 rounded-xl">
                    <button
                      onClick={() => toggleExpertExpansion(expert.expert_name)}
                      className="w-full p-4 text-left hover:bg-gray-50 transition-colors rounded-xl"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center mr-3">
                            <Brain className="w-4 h-4 text-white" />
                          </div>
                          <div>
                            <h3 className="text-black font-semibold text-sm">{expert.expert_name}</h3>
                            <p className="text-gray-600 text-xs">
                              {expert.is_current ? '当前专家' : '历史专家'}
                            </p>
                          </div>
                        </div>
                        {expandedExperts.has(expert.expert_name) ? (
                          <ChevronDown className="w-4 h-4 text-gray-600" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-gray-600" />
                        )}
                      </div>
                    </button>

                    {expandedExperts.has(expert.expert_name) && (
                      <div className="px-4 pb-4 space-y-3">
                        {/* 专业领域 */}
                        {expert.expertise_areas.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-xs font-medium mb-1">专业领域:</p>
                            <div className="flex flex-wrap gap-1">
                              {expert.expertise_areas.map((area, areaIndex) => (
                                <span key={areaIndex} className="bg-gray-200 text-gray-800 text-xs px-2 py-1 rounded">
                                  {area}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* 核心观点 */}
                        {expert.key_insights.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-xs font-medium mb-1">核心观点:</p>
                            <ul className="text-gray-800 text-xs space-y-1">
                              {expert.key_insights.map((insight, insightIndex) => (
                                <li key={insightIndex}>• {insight}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* 帮助要点 */}
                        {expert.helpful_points.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-xs font-medium mb-1 flex items-center">
                              <Lightbulb className="w-3 h-3 mr-1" />
                              可帮助的要点:
                            </p>
                            <ul className="text-gray-800 text-xs space-y-1">
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
                {conversationAnalysis.suggested_directions.length > 0 && (
                  <div className="bg-white border border-gray-300 rounded-xl p-4">
                    <h3 className="text-black font-semibold mb-2 flex items-center">
                      <Lightbulb className="w-4 h-4 mr-2" />
                      建议方向
                    </h3>
                    <ul className="text-gray-800 text-sm space-y-1">
                      {conversationAnalysis.suggested_directions.map((direction, index) => (
                        <li key={index} className="text-xs">• {direction}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center text-gray-600 py-8">
                <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p className="text-sm">暂无分析数据</p>
                <p className="text-xs mt-1">开始对话后将显示分析结果</p>
              </div>
            )}
          </div>
        </div>

        {/* 中栏 - 统一时间线 (50%) */}
        <div className="w-1/2 bg-white border-r border-gray-300 flex flex-col">
          <div className="p-4 border-b border-gray-300">
            <h2 className="text-lg font-semibold text-black flex items-center">
              <MessageCircle className="w-5 h-5 mr-2 text-gray-600" />
              对话时间线
            </h2>
          </div>

          <div className="flex-1 p-4 overflow-y-auto">
            <div className="space-y-4">
              {getAllMessagesInOrder().map((message, index) => {
                // 计算当前消息组中的嘉宾索引
                const allMessages = getAllMessagesInOrder();
                const currentMessageGroup = allMessages.filter(m =>
                  m.timestamp === message.timestamp && (m.type === 'expert' || m.type === 'system')
                );
                const guestIndex = currentMessageGroup.findIndex(m => m.id === message.id);
                const totalGuests = currentMessageGroup.length;

                // 处理嘉宾完成回调
                const handleGuestComplete = () => {
                  setCompletedGuests(prev => new Set([...prev, message.id]));
                };

                // 判断当前嘉宾是否应该开始（顺序模式下）
                const shouldStart = !sequentialMode || guestIndex === 0 ||
                  (guestIndex > 0 && completedGuests.has(currentMessageGroup[guestIndex - 1]?.id));
                if (message.type === 'user') {
                  // 用户消息
                  return (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="flex justify-end"
                    >
                      <div className="max-w-[80%] bg-white border border-gray-300 rounded-2xl p-3">
                        <div className="flex items-center mb-2">
                          <div className="w-6 h-6 bg-gray-600 rounded-full flex items-center justify-center mr-2">
                            <User className="w-3 h-3 text-white" />
                          </div>
                          <span className="text-gray-700 text-sm font-medium">用户</span>
                        </div>
                        <p className="text-black text-sm leading-relaxed">{message.content}</p>
                      </div>
                    </motion.div>
                  );
                } else if (message.type === 'expert' || message.type === 'system') {
                  // 专家/系统消息
                  return (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="flex justify-start"
                    >
                      <div className="max-w-[90%] bg-white border border-gray-300 rounded-2xl p-4">
                        {/* 角色名称 */}
                        <div className="flex items-center mb-3">
                          <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center mr-3">
                            <Brain className="w-4 h-4 text-white" />
                          </div>
                          <span className="text-black font-semibold">{message.characterName}</span>
                        </div>

                        <StreamingCharacterResponse
                          message={{
                            characterName: message.characterName || '',
                            bodyLanguage: message.bodyLanguage,
                            thinking: message.thinking,
                            speaking: message.speaking
                          }}
                          speed={20}
                          guestIndex={sequentialMode ? guestIndex : 0}
                          totalGuests={totalGuests}
                          onComplete={handleGuestComplete}
                          shouldStart={shouldStart}
                          showSkipButton={true}
                        />
                      </div>
                    </motion.div>
                  );
                }
                return null;
              })}

              {/* 加载状态 */}
              {(isLoading || storeLoading) && (
                <div className="flex justify-center">
                  <div className="bg-gray-800/50 rounded-2xl p-4 flex items-center space-x-3">
                    <div className="w-6 h-6 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-gray-300 text-sm">智者正在思考...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
        {/* 右栏 - 用户交互区域 (20%) */}
        <div className="w-[20%] bg-white flex flex-col">
          {/* 顶部 - 系统区域 */}
          <div className="p-4 border-b border-gray-300">
            <button
              onClick={handleBackToHome}
              className="flex items-center space-x-2 text-gray-600 hover:text-black transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>返回首页</span>
            </button>

            <h2 className="text-lg font-semibold text-black mb-3 flex items-center">
              <User className="w-5 h-5 mr-2 text-gray-600" />
              用户区域
            </h2>

            {/* 显示模式切换 */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sequentialMode}
                  onChange={(e) => setSequentialMode(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-gray-700">
                  顺序显示嘉宾（一个接一个）
                </span>
              </label>
              <p className="text-xs text-gray-500 mt-1">
                {sequentialMode ? '嘉宾将依次发言' : '所有嘉宾同时发言'}
              </p>
            </div>

            {/* 系统消息 */}
            {systemMessages.map((message) => (
              <div key={message.id} className="bg-white border border-gray-300 rounded-lg p-3 mb-3">
                <div className="flex items-center mb-2">
                  <Settings className="w-4 h-4 text-gray-600 mr-2" />
                  <span className="text-sm text-black font-medium">房间管理员</span>
                </div>
                <p className="text-gray-800 text-sm">{message.content}</p>
              </div>
            ))}
          </div>

          {/* 中部 - 用户消息区域 */}
          <div className="flex-1 p-4 overflow-y-auto">
            <h3 className="text-sm font-medium text-black mb-3">我的提问历史</h3>
            <div className="space-y-3">
              {userMessages.map((message) => (
                <div key={message.id} className="bg-white border border-gray-300 rounded-lg p-3">
                  <div className="flex items-center mb-2">
                    <User className="w-4 h-4 text-gray-600 mr-2" />
                    <span className="text-sm text-black font-medium">我</span>
                  </div>
                  <p className="text-gray-800 text-sm">{message.content}</p>
                </div>
              ))}
            </div>

            {/* 错误提示 */}
            {error && (
              <div className="bg-red-50 border border-red-300 rounded-lg p-3 mt-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* 底部 - 操作区域 */}
          <div className="p-4 border-t border-gray-300 space-y-3">
            <h3 className="text-sm font-medium text-black mb-2">操作面板</h3>

            {/* 操作按钮组 */}
            <div className="flex justify-center">
              {/* 开启新讨论按钮 */}
              <button
                onClick={handleStartNewDiscussion}
                disabled={isLoading}
                className="py-2 px-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center space-x-2 text-sm"
              >
                <Plus className="w-4 h-4" />
                <span>新讨论</span>
              </button>
            </div>

            {/* 新问题输入 */}
            <form onSubmit={handleNewQuestion} className="space-y-2">
              <textarea
                value={newQuestion}
                onChange={(e) => setNewQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (newQuestion.trim() && !isLoading) {
                      handleNewQuestion(e as any);
                    }
                  }
                }}
                placeholder="在当前话题中提出新问题..."
                className="w-full h-16 px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent resize-none text-sm"
                disabled={isLoading}
              />
              <div className="text-xs text-gray-400 text-right">
                回车发送 • Shift+回车换行
              </div>
              <button
                type="submit"
                disabled={!newQuestion.trim() || isLoading}
                className="w-full py-2 px-4 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center space-x-2 text-sm"
              >
                <Send className="w-4 h-4" />
                <span>发送问题</span>
              </button>
            </form>

            {/* 我已获得答案按钮 */}
            {currentThreadId && messages.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-600">
                <AnswerButton
                  threadId={currentThreadId}
                  userId={`user_${currentThreadId}`}
                  className="w-full"
                />
              </div>
            )}

            {/* 清空提示 */}
            <div className="text-xs text-gray-500 text-center">
              💡 &ldquo;新讨论&rdquo;会清空当前对话，开始全新话题
            </div>
          </div>
        </div>
      </div>



      {/* Insight显示组件 - 暂时禁用 */}
      {/* {currentThreadId && insightDisplay.isActive && (
        <InsightDisplay
          key={`insight-${currentThreadId}-${insightDisplay.sessionId}`}
          userId={`user_${currentThreadId}`}
          threadId={currentThreadId}
          onComplete={handleInsightComplete}
          onSkip={handleInsightSkip}
        />
      )} */}

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
