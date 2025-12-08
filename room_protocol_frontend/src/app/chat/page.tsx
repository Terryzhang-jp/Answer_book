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

  const [sequentialMode, setSequentialMode] = useState(true); // Sequential display mode, enabled by default
  const [completedGuests, setCompletedGuests] = useState<Set<string>>(new Set()); // Completed guests
  
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

  // Report generation status
  const {
    isGenerating,
    generationStatus,
    currentProgress
  } = useReportStore();

  // If no conversation, redirect to home page
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

      // Temporarily disable insight generation
      // console.log('Reset insight state, start new insight generation');
      // resetInsightDisplay(); // Reset state first

      // console.log('Start insight display');
      // startInsightDisplay('', ''); // Directly start display state

      const response = await ApiService.askQuestion({
        question: newQuestion.trim(),
        user_id: 'user_' + Date.now(),
        thread_id: currentThreadId || undefined, // 传递当前的thread_id以继续对话
      });

      // API call complete, close insight display (disabled)
      // console.log('API call complete, close insight display');
      // completeInsightDisplay();

      addResponse(response);
      setNewQuestion('');
      // Clear completed state, prepare for new conversation
      setCompletedGuests(new Set());
    } catch (error) {
      console.error('Question failed:', error);
      setError(error instanceof Error ? error.message : 'Failed to submit question, please try again');
    } finally {
      setIsLoading(false);
      setLoading(false);
      // Note: Don't close subconscious detection here, let it complete naturally
    }
  };

  const handleBackToHome = () => {
    clearConversation();
    router.push('/');
  };

  const handleStartNewDiscussion = () => {
    // Confirm if user wants to start a new discussion
    if (messages.length > 0) {
      const confirmed = window.confirm('Are you sure you want to start a new discussion? The current conversation will be cleared.');
      if (!confirmed) return;
    }

    // Clear all data and navigate to home page
    startNewDiscussion();
    router.push('/');
  };



  // Insight display completion handler
  const handleInsightComplete = () => {
    console.log('Insight display complete');
    completeInsightDisplay();
  };

  // Insight display skip handler
  const handleInsightSkip = () => {
    console.log('User skipped Insight display');
    skipInsightDisplay();
  };

  // Toggle expert expansion state
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

  // Get all messages sorted by time (for unified timeline)
  const getAllMessagesInOrder = () => {
    return [...messages].sort((a, b) =>
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
  };

  // Get different types of messages (for right panel display)
  const userMessages = messages.filter(msg => msg.type === 'user');
  const systemMessages = messages.filter(msg => msg.type === 'system');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black">
      {/* Room announcement bar - full width at top */}
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
                <span className="text-sm text-amber-300 font-semibold">[Room Announcement - Centered]</span>
              </div>
              <p className="text-amber-100 font-medium text-lg">{roomAnnouncement}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content area - three column layout */}
      <div className={`flex ${roomAnnouncement ? 'h-[calc(100vh-80px)]' : 'h-screen'}`}>
        {/* Left panel - Analysis display area (30%) */}
        <div className="w-[30%] bg-white border-r border-gray-300 p-4 overflow-y-auto">
          <h2 className="text-lg font-semibold text-black mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2 text-gray-600" />
            Conversation Analysis
          </h2>

          <div className="space-y-4">
            {/* Streaming report generation progress */}
            {isGenerating && (
              <StreamingProgress
                progress={currentProgress}
                isGenerating={isGenerating}
                generationStatus={generationStatus}
              />
            )}

            {conversationAnalysis && !isGenerating ? (
              <>
                {/* User question analysis */}
                <div className="bg-white border border-gray-300 rounded-xl p-4">
                  <h3 className="text-black font-semibold mb-2 flex items-center">
                    <Target className="w-4 h-4 mr-2" />
                    Question Analysis
                  </h3>
                  <p className="text-gray-800 text-sm leading-relaxed">
                    {conversationAnalysis.user_question_analysis}
                  </p>
                </div>

                {/* Expert invitation reason */}
                {conversationAnalysis.expert_selection_reason && (
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-5 shadow-sm">
                    <h3 className="text-black font-semibold mb-3 flex items-center">
                      <User className="w-5 h-5 mr-2 text-blue-600" />
                      Expert Invitation Reason
                    </h3>
                    <div className="text-gray-800 text-sm leading-relaxed whitespace-pre-line">
                      {conversationAnalysis.expert_selection_reason}
                    </div>
                  </div>
                )}

                {/* Conversation summary */}
                {conversationAnalysis.conversation_timeline && conversationAnalysis.conversation_timeline.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="text-black font-semibold mb-3 flex items-center">
                      <MessageSquare className="w-4 h-4 mr-2 text-gray-600" />
                      Conversation Summary
                    </h3>
                    <div className="space-y-2">
                      {conversationAnalysis.conversation_timeline.map((entry, index) => (
                        <div key={index} className="text-sm leading-relaxed">
                          <span className={`font-medium ${
                            entry.speaker === '用户' || entry.speaker === 'User' ? 'text-blue-600' : 'text-green-600'
                          }`}>
                            • {entry.speaker}
                          </span>
                          <span className="text-gray-700 ml-1">
                            {entry.action}: {entry.content}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Conversation evolution */}
                <div className="bg-white border border-gray-300 rounded-xl p-4">
                  <h3 className="text-black font-semibold mb-2 flex items-center">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Conversation Evolution
                  </h3>
                  <div className="space-y-2">
                    <div>
                      <p className="text-gray-700 text-xs font-medium mb-1">Discussion Depth:</p>
                      <p className="text-gray-800 text-sm">{conversationAnalysis.conversation_evolution.discussion_depth}</p>
                    </div>
                    {conversationAnalysis.conversation_evolution.topic_progression.length > 0 && (
                      <div>
                        <p className="text-gray-700 text-xs font-medium mb-1">Topic Progression:</p>
                        <ul className="text-gray-800 text-sm space-y-1">
                          {conversationAnalysis.conversation_evolution.topic_progression.map((topic, index) => (
                            <li key={index} className="text-xs">• {topic}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {/* Expert insights - grouped by guest with collapse */}
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
                              {expert.is_current ? 'Current Expert' : 'Historical Expert'}
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
                        {/* Areas of expertise */}
                        {expert.expertise_areas.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-xs font-medium mb-1">Areas of Expertise:</p>
                            <div className="flex flex-wrap gap-1">
                              {expert.expertise_areas.map((area, areaIndex) => (
                                <span key={areaIndex} className="bg-gray-200 text-gray-800 text-xs px-2 py-1 rounded">
                                  {area}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Key insights */}
                        {expert.key_insights.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-xs font-medium mb-1">Key Insights:</p>
                            <ul className="text-gray-800 text-xs space-y-1">
                              {expert.key_insights.map((insight, insightIndex) => (
                                <li key={insightIndex}>• {insight}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Helpful points */}
                        {expert.helpful_points.length > 0 && (
                          <div>
                            <p className="text-gray-700 text-xs font-medium mb-1 flex items-center">
                              <Lightbulb className="w-3 h-3 mr-1" />
                              Helpful Points:
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

                {/* Suggested directions */}
                {conversationAnalysis.suggested_directions.length > 0 && (
                  <div className="bg-white border border-gray-300 rounded-xl p-4">
                    <h3 className="text-black font-semibold mb-2 flex items-center">
                      <Lightbulb className="w-4 h-4 mr-2" />
                      Suggested Directions
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
                <p className="text-sm">No analysis data yet</p>
                <p className="text-xs mt-1">Analysis will appear after starting a conversation</p>
              </div>
            )}
          </div>
        </div>

        {/* Middle panel - Unified timeline (50%) */}
        <div className="w-1/2 bg-white border-r border-gray-300 flex flex-col">
          <div className="p-4 border-b border-gray-300">
            <h2 className="text-lg font-semibold text-black flex items-center">
              <MessageCircle className="w-5 h-5 mr-2 text-gray-600" />
              Conversation Timeline
            </h2>
          </div>

          <div className="flex-1 p-4 overflow-y-auto">
            <div className="space-y-4">
              {getAllMessagesInOrder().map((message, index) => {
                // Calculate guest index in current message group
                const allMessages = getAllMessagesInOrder();
                const currentMessageGroup = allMessages.filter(m =>
                  m.timestamp === message.timestamp && (m.type === 'expert' || m.type === 'system')
                );
                const guestIndex = currentMessageGroup.findIndex(m => m.id === message.id);
                const totalGuests = currentMessageGroup.length;

                // Handle guest completion callback
                const handleGuestComplete = () => {
                  setCompletedGuests(prev => new Set([...prev, message.id]));
                };

                // Determine if current guest should start (in sequential mode)
                const shouldStart = !sequentialMode || guestIndex === 0 ||
                  (guestIndex > 0 && completedGuests.has(currentMessageGroup[guestIndex - 1]?.id));
                if (message.type === 'user') {
                  // User message
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
                          <span className="text-gray-700 text-sm font-medium">User</span>
                        </div>
                        <p className="text-black text-sm leading-relaxed">{message.content}</p>
                      </div>
                    </motion.div>
                  );
                } else if (message.type === 'expert' || message.type === 'system') {
                  // Expert/system message
                  return (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="flex justify-start"
                    >
                      <div className="max-w-[90%] bg-white border border-gray-300 rounded-2xl p-4">
                        {/* Character name */}
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

              {/* Loading state */}
              {(isLoading || storeLoading) && (
                <div className="flex justify-center">
                  <div className="bg-gray-800/50 rounded-2xl p-4 flex items-center space-x-3">
                    <div className="w-6 h-6 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-gray-300 text-sm">The wise are thinking...</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
        {/* Right panel - User interaction area (20%) */}
        <div className="w-[20%] bg-white flex flex-col">
          {/* Top - System area */}
          <div className="p-4 border-b border-gray-300">
            <button
              onClick={handleBackToHome}
              className="flex items-center space-x-2 text-gray-600 hover:text-black transition-colors mb-4"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Back to Home</span>
            </button>

            <h2 className="text-lg font-semibold text-black mb-3 flex items-center">
              <User className="w-5 h-5 mr-2 text-gray-600" />
              User Area
            </h2>

            {/* Display mode toggle */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sequentialMode}
                  onChange={(e) => setSequentialMode(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm text-gray-700">
                  Sequential guest display (one by one)
                </span>
              </label>
              <p className="text-xs text-gray-500 mt-1">
                {sequentialMode ? 'Guests will speak in turn' : 'All guests speak simultaneously'}
              </p>
            </div>

            {/* System messages */}
            {systemMessages.map((message) => (
              <div key={message.id} className="bg-white border border-gray-300 rounded-lg p-3 mb-3">
                <div className="flex items-center mb-2">
                  <Settings className="w-4 h-4 text-gray-600 mr-2" />
                  <span className="text-sm text-black font-medium">Room Admin</span>
                </div>
                <p className="text-gray-800 text-sm">{message.content}</p>
              </div>
            ))}
          </div>

          {/* Middle - User message area */}
          <div className="flex-1 p-4 overflow-y-auto">
            <h3 className="text-sm font-medium text-black mb-3">My Question History</h3>
            <div className="space-y-3">
              {userMessages.map((message) => (
                <div key={message.id} className="bg-white border border-gray-300 rounded-lg p-3">
                  <div className="flex items-center mb-2">
                    <User className="w-4 h-4 text-gray-600 mr-2" />
                    <span className="text-sm text-black font-medium">Me</span>
                  </div>
                  <p className="text-gray-800 text-sm">{message.content}</p>
                </div>
              ))}
            </div>

            {/* Error message */}
            {error && (
              <div className="bg-red-50 border border-red-300 rounded-lg p-3 mt-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Bottom - Action area */}
          <div className="p-4 border-t border-gray-300 space-y-3">
            <h3 className="text-sm font-medium text-black mb-2">Action Panel</h3>

            {/* Action button group */}
            <div className="flex justify-center">
              {/* New discussion button */}
              <button
                onClick={handleStartNewDiscussion}
                disabled={isLoading}
                className="py-2 px-4 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center space-x-2 text-sm"
              >
                <Plus className="w-4 h-4" />
                <span>New Discussion</span>
              </button>
            </div>

            {/* New question input */}
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
                placeholder="Ask a new question on the current topic..."
                className="w-full h-16 px-3 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent resize-none text-sm"
                disabled={isLoading}
              />
              <div className="text-xs text-gray-400 text-right">
                Enter to send • Shift+Enter for new line
              </div>
              <button
                type="submit"
                disabled={!newQuestion.trim() || isLoading}
                className="w-full py-2 px-4 bg-amber-600 hover:bg-amber-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center justify-center space-x-2 text-sm"
              >
                <Send className="w-4 h-4" />
                <span>Send Question</span>
              </button>
            </form>

            {/* I got the answer button */}
            {currentThreadId && messages.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-600">
                <AnswerButton
                  threadId={currentThreadId}
                  userId={`user_${currentThreadId}`}
                  className="w-full"
                />
              </div>
            )}

            {/* Clear hint */}
            <div className="text-xs text-gray-500 text-center">
              💡 &ldquo;New Discussion&rdquo; will clear the current conversation and start a new topic
            </div>
          </div>
        </div>
      </div>



      {/* Insight display component - temporarily disabled */}
      {/* {currentThreadId && insightDisplay.isActive && (
        <InsightDisplay
          key={`insight-${currentThreadId}-${insightDisplay.sessionId}`}
          userId={`user_${currentThreadId}`}
          threadId={currentThreadId}
          onComplete={handleInsightComplete}
          onSkip={handleInsightSkip}
        />
      )} */}

      {/* Report generation modal */}
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
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Generating Report</h3>
              <p className="text-gray-600 text-sm">
                {generationStatus || 'Generating your personalized Answer Book letter...'}
              </p>
            </div>
            <div className="text-xs text-gray-500">
              Please wait, this may take a few minutes
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
