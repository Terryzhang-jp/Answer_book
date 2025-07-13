'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Send, BookOpen, Sparkles } from 'lucide-react';
import { ApiService } from '@/services/api';
import { useConversationStore } from '@/store/conversation';

export default function Home() {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  const { addUserMessage, addResponse, setLoading, setError } = useConversationStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || isLoading) return;

    try {
      setIsLoading(true);
      setLoading(true);
      setError(null);

      // 添加用户消息到store
      addUserMessage(question);

      // 调用创建房间API
      const response = await ApiService.createRoom({
        question: question.trim(),
        user_id: 'user_' + Date.now(),
      });

      // 添加响应到store
      addResponse(response);

      // 跳转到聊天页面
      router.push('/chat');
    } catch (error) {
      console.error('提问失败:', error);
      setError(error instanceof Error ? error.message : '提问失败，请重试');
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black flex items-center justify-center p-4">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-amber-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl"></div>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="relative z-10 w-full max-w-2xl mx-auto text-center"
      >
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-12"
        >
          <div className="flex items-center justify-center mb-6">
            <BookOpen className="w-12 h-12 text-amber-400 mr-4" />
            <h1 className="text-5xl font-bold text-white">答案之书</h1>
            <Sparkles className="w-8 h-8 text-amber-400 ml-4" />
          </div>
          
          <p className="text-xl text-gray-300 mb-2">
            向智者提问，获得深度洞察
          </p>
          <p className="text-sm text-gray-400 mb-3">
            与历史上最伟大的思想家进行对话
          </p>
          <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-4 text-left">
            <p className="text-amber-200 text-sm mb-2">
              💡 <strong>提示：</strong>你可以指明邀请特定的智者参与对话
            </p>
            <p className="text-amber-100 text-xs leading-relaxed">
              例如："请苏格拉底和孔子讨论教育的本质"、"邀请爱因斯坦解释相对论"、"让马斯克谈谈创新思维"等。任何历史人物、思想家、科学家都可以被邀请！
            </p>
          </div>
        </motion.div>

        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          <div className="relative">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="请输入你想探索的问题..."
              className="w-full h-32 px-6 py-4 bg-gray-800/50 border border-gray-600 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent resize-none backdrop-blur-sm"
              disabled={isLoading}
            />
            
            <div className="absolute bottom-3 right-3 text-xs text-gray-500">
              {question.length}/500
            </div>
          </div>

          <motion.button
            type="submit"
            disabled={!question.trim() || isLoading}
            className="w-full py-4 px-8 bg-gradient-to-r from-amber-500 to-orange-500 text-white font-semibold rounded-2xl hover:from-amber-600 hover:to-orange-600 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:ring-offset-2 focus:ring-offset-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>正在邀请智者...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>开始对话</span>
              </>
            )}
          </motion.button>
        </motion.form>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-12"
        >
          <p className="text-sm text-gray-400 mb-4">或者尝试这些复杂问题：</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-4xl mx-auto">
            {[
              "请苏格拉底和孔子讨论教育的真正目的是什么？",
              "邀请爱因斯坦和霍金解释时间的本质",
              "让马克思和亚当·斯密辩论资本主义的未来",
              "请达芬奇和乔布斯谈论创新与艺术的关系",
              "邀请尼采和佛陀探讨痛苦与智慧",
              "让图灵和马斯克预测AI对人类的影响"
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setQuestion(example)}
                className="px-4 py-3 bg-gray-700/50 text-gray-300 rounded-xl text-sm hover:bg-gray-600/50 transition-colors text-left leading-relaxed w-full"
                disabled={isLoading}
              >
                {example}
              </button>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
