'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, BookOpen, Sparkles, X } from 'lucide-react';
import { ApiService } from '@/services/api';
import { useConversationStore } from '@/store/conversation';

export default function Home() {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [focusMode, setFocusMode] = useState(false);
  const router = useRouter();
  const { addUserMessage, addResponse, setLoading, setError } = useConversationStore();

  // 监听ESC键关闭专注模式
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && focusMode) {
        setFocusMode(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [focusMode]);

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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-zinc-900 flex items-center justify-center p-4 relative overflow-hidden">
      {/* 星空背景效果 */}
      <div className="absolute inset-0 overflow-hidden">
        {/* 大星星 */}
        {[...Array(50)].map((_, i) => (
          <motion.div
            key={`star-large-${i}`}
            className="absolute w-1 h-1 bg-white rounded-full opacity-80"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.3, 1, 0.3],
              scale: [0.8, 1.2, 0.8],
            }}
            transition={{
              duration: 2 + Math.random() * 3,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}

        {/* 中等星星 */}
        {[...Array(100)].map((_, i) => (
          <motion.div
            key={`star-medium-${i}`}
            className="absolute w-0.5 h-0.5 bg-slate-300 rounded-full opacity-60"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.2, 0.8, 0.2],
            }}
            transition={{
              duration: 3 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          />
        ))}

        {/* 小星星 */}
        {[...Array(200)].map((_, i) => (
          <div
            key={`star-small-${i}`}
            className="absolute w-px h-px bg-slate-400 rounded-full opacity-40"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}

        {/* 流星效果 - 增加更多随机流星 */}
        {[...Array(12)].map((_, i) => {
          const startX = Math.random() * 100;
          const startY = Math.random() * 60;
          const endX = startX + (Math.random() * 300 + 150) * (Math.random() > 0.5 ? 1 : -1);
          const endY = startY + (Math.random() * 200 + 100);
          const duration = 0.8 + Math.random() * 1.5;
          const delay = i * 3 + Math.random() * 8;
          const repeatDelay = 10 + Math.random() * 20;

          return (
            <motion.div
              key={`meteor-${i}`}
              className="absolute opacity-0"
              style={{
                left: `${startX}%`,
                top: `${startY}%`,
              }}
              animate={{
                x: [0, endX - startX],
                y: [0, endY - startY],
                opacity: [0, 1, 1, 0],
              }}
              transition={{
                duration: duration,
                repeat: Infinity,
                delay: delay,
                repeatDelay: repeatDelay,
                ease: "easeOut",
              }}
            >
              {/* 流星头部 */}
              <div className="w-1.5 h-1.5 bg-white rounded-full blur-sm"></div>
              {/* 流星尾巴 */}
              <div
                className="absolute top-0 left-0 bg-gradient-to-r from-white via-blue-200 to-transparent opacity-80"
                style={{
                  width: `${20 + Math.random() * 30}px`,
                  height: '2px',
                  transform: 'rotate(45deg) translateX(-50%)',
                  transformOrigin: 'left center',
                }}
              ></div>
            </motion.div>
          );
        })}

        {/* 快速流星 */}
        {[...Array(8)].map((_, i) => {
          const startX = Math.random() * 100;
          const startY = Math.random() * 40;
          const angle = Math.random() * 60 + 30; // 30-90度角
          const distance = 400 + Math.random() * 200;
          const endX = startX + Math.cos(angle * Math.PI / 180) * distance;
          const endY = startY + Math.sin(angle * Math.PI / 180) * distance;

          return (
            <motion.div
              key={`fast-meteor-${i}`}
              className="absolute w-0.5 h-0.5 bg-cyan-300 rounded-full opacity-0"
              style={{
                left: `${startX}%`,
                top: `${startY}%`,
                boxShadow: '0 0 4px #67e8f9',
              }}
              animate={{
                x: [0, endX - startX],
                y: [0, endY - startY],
                opacity: [0, 1, 0],
                scale: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 0.5 + Math.random() * 0.5,
                repeat: Infinity,
                delay: i * 4 + Math.random() * 12,
                repeatDelay: 20 + Math.random() * 15,
                ease: "linear",
              }}
            />
          );
        })}

        {/* 慢速大流星 */}
        {[...Array(4)].map((_, i) => {
          const startX = Math.random() * 80 + 10;
          const startY = Math.random() * 30;
          const endX = startX + (Math.random() * 400 + 200) * (Math.random() > 0.5 ? 1 : -1);
          const endY = startY + Math.random() * 300 + 150;

          return (
            <motion.div
              key={`big-meteor-${i}`}
              className="absolute opacity-0"
              style={{
                left: `${startX}%`,
                top: `${startY}%`,
              }}
              animate={{
                x: [0, endX - startX],
                y: [0, endY - startY],
                opacity: [0, 0.8, 0.8, 0],
              }}
              transition={{
                duration: 2 + Math.random() * 1.5,
                repeat: Infinity,
                delay: i * 8 + Math.random() * 15,
                repeatDelay: 30 + Math.random() * 25,
                ease: "easeInOut",
              }}
            >
              {/* 大流星头部 */}
              <div className="w-2 h-2 bg-yellow-200 rounded-full blur-sm"></div>
              {/* 大流星尾巴 */}
              <div
                className="absolute top-0 left-0 bg-gradient-to-r from-yellow-200 via-orange-300 to-transparent opacity-70"
                style={{
                  width: `${40 + Math.random() * 60}px`,
                  height: '3px',
                  transform: 'rotate(35deg) translateX(-50%)',
                  transformOrigin: 'left center',
                }}
              ></div>
              {/* 额外光晕 */}
              <div className="absolute top-0 left-0 w-3 h-3 bg-yellow-100 rounded-full blur-md opacity-50 -translate-x-0.5 -translate-y-0.5"></div>
            </motion.div>
          );
        })}

        {/* 彩色流星 */}
        {[...Array(6)].map((_, i) => {
          const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'];
          const color = colors[i % colors.length];
          const startX = Math.random() * 100;
          const startY = Math.random() * 50;
          const endX = startX + (Math.random() * 250 + 100) * (Math.random() > 0.5 ? 1 : -1);
          const endY = startY + Math.random() * 200 + 80;

          return (
            <motion.div
              key={`color-meteor-${i}`}
              className="absolute opacity-0"
              style={{
                left: `${startX}%`,
                top: `${startY}%`,
              }}
              animate={{
                x: [0, endX - startX],
                y: [0, endY - startY],
                opacity: [0, 0.9, 0.9, 0],
                rotate: [0, 360],
              }}
              transition={{
                duration: 1.2 + Math.random() * 0.8,
                repeat: Infinity,
                delay: i * 5 + Math.random() * 10,
                repeatDelay: 25 + Math.random() * 20,
                ease: "easeOut",
              }}
            >
              <div
                className="w-1 h-1 rounded-full blur-sm"
                style={{ backgroundColor: color, boxShadow: `0 0 6px ${color}` }}
              ></div>
              <div
                className="absolute top-0 left-0 opacity-60"
                style={{
                  width: `${15 + Math.random() * 25}px`,
                  height: '1.5px',
                  background: `linear-gradient(to right, ${color}, transparent)`,
                  transform: 'rotate(45deg) translateX(-50%)',
                  transformOrigin: 'left center',
                }}
              ></div>
            </motion.div>
          );
        })}

        {/* 螺旋流星 */}
        {[...Array(3)].map((_, i) => {
          const centerX = 20 + Math.random() * 60;
          const centerY = 20 + Math.random() * 40;
          const radius = 50 + Math.random() * 30;

          return (
            <motion.div
              key={`spiral-meteor-${i}`}
              className="absolute w-1 h-1 bg-purple-300 rounded-full opacity-0"
              style={{
                left: `${centerX}%`,
                top: `${centerY}%`,
                boxShadow: '0 0 4px #d8b4fe',
              }}
              animate={{
                x: [0, radius, 0, -radius, 0],
                y: [0, radius/2, radius, radius/2, 0],
                opacity: [0, 1, 1, 1, 0],
                scale: [0.5, 1, 1.2, 1, 0.5],
              }}
              transition={{
                duration: 3 + Math.random() * 2,
                repeat: Infinity,
                delay: i * 10 + Math.random() * 15,
                repeatDelay: 40 + Math.random() * 30,
                ease: "easeInOut",
              }}
            />
          );
        })}

        {/* 星云效果 */}
        {[...Array(5)].map((_, i) => (
          <motion.div
            key={`nebula-${i}`}
            className="absolute rounded-full opacity-5"
            style={{
              left: `${Math.random() * 80 + 10}%`,
              top: `${Math.random() * 80 + 10}%`,
              width: `${100 + Math.random() * 200}px`,
              height: `${100 + Math.random() * 200}px`,
              background: `radial-gradient(circle, ${
                ['rgba(99, 102, 241, 0.3)', 'rgba(139, 92, 246, 0.3)', 'rgba(59, 130, 246, 0.3)', 'rgba(16, 185, 129, 0.3)'][i % 4]
              } 0%, transparent 70%)`,
            }}
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.05, 0.15, 0.05],
            }}
            transition={{
              duration: 8 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}

        {/* 闪烁的亮星 */}
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={`bright-star-${i}`}
            className="absolute w-2 h-2 opacity-60"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0.3, 1, 0.3],
              scale: [0.5, 1, 0.5],
            }}
            transition={{
              duration: 2 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 3,
            }}
          >
            <div className="w-full h-full bg-white rounded-full blur-sm"></div>
            <div className="absolute inset-0 w-full h-full bg-white rounded-full"></div>
          </motion.div>
        ))}
      </div>

      {/* 书本背景 */}
      <div className="absolute inset-0 flex items-center justify-center z-10">
        <div className="w-full h-full max-w-5xl max-h-[85vh] relative" style={{ aspectRatio: '4/3' }}>
          {/* 书本阴影 */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-800/30 to-gray-900/40 rounded-3xl transform rotate-1 scale-105 blur-xl"></div>

          {/* 书本主体 */}
          <div className="relative w-full h-full bg-gradient-to-br from-slate-800 via-gray-800 to-zinc-800 rounded-3xl shadow-2xl border-4 border-slate-700/50 overflow-hidden">
            {/* 主要背景渐变 */}
            <div className="absolute inset-0 bg-gradient-to-br from-slate-700/80 via-gray-800/90 to-slate-900/95"></div>

            {/* 次要渐变层 */}
            <div className="absolute inset-0 bg-gradient-to-tr from-blue-900/10 via-transparent to-purple-900/10"></div>

            {/* 书本纹理层 */}
            <div className="absolute inset-0 opacity-15">
              <div className="w-full h-full bg-slate-700/40" style={{
                backgroundImage: `
                  radial-gradient(circle at 25% 25%, rgba(148, 163, 184, 0.1) 0%, transparent 50%),
                  radial-gradient(circle at 75% 75%, rgba(100, 116, 139, 0.1) 0%, transparent 50%),
                  linear-gradient(45deg, rgba(71, 85, 105, 0.05) 25%, transparent 25%),
                  linear-gradient(-45deg, rgba(71, 85, 105, 0.05) 25%, transparent 25%)
                `,
                backgroundSize: '200px 200px, 150px 150px, 20px 20px, 20px 20px'
              }}></div>
            </div>

            {/* 装饰性光晕 */}
            <div className="absolute top-8 right-8 w-32 h-32 bg-gradient-radial from-blue-400/10 to-transparent rounded-full blur-xl"></div>
            <div className="absolute bottom-12 left-12 w-24 h-24 bg-gradient-radial from-purple-400/8 to-transparent rounded-full blur-lg"></div>

            {/* 书脊装饰 - 增强版 */}
            <div className="absolute left-0 top-0 w-10 h-full bg-gradient-to-b from-slate-600 via-gray-700 to-slate-800 shadow-inner">
              <div className="w-full h-full bg-gradient-to-r from-transparent via-slate-500/30 to-transparent"></div>
              {/* 书脊装饰线 */}
              <div className="absolute left-2 top-8 bottom-8 w-0.5 bg-gradient-to-b from-slate-400/50 via-slate-500/30 to-slate-400/50"></div>
              <div className="absolute left-6 top-12 bottom-12 w-0.5 bg-gradient-to-b from-slate-400/30 via-slate-500/20 to-slate-400/30"></div>
            </div>

            {/* 顶部装饰边框 */}
            <div className="absolute top-0 left-10 right-0 h-1 bg-gradient-to-r from-slate-600 via-slate-500 to-slate-600"></div>

            {/* 底部装饰边框 */}
            <div className="absolute bottom-0 left-10 right-0 h-1 bg-gradient-to-r from-slate-600 via-slate-500 to-slate-600"></div>

            {/* 角落装饰 */}
            <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-slate-500/40 rounded-tr-lg"></div>
            <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-slate-500/40 rounded-br-lg"></div>
            <div className="absolute top-4 left-12 w-8 h-8 border-t-2 border-l-2 border-slate-500/40 rounded-tl-lg"></div>
            <div className="absolute bottom-4 left-12 w-8 h-8 border-b-2 border-l-2 border-slate-500/40 rounded-bl-lg"></div>

            {/* 页面内容区域 */}
            <div className="relative z-10 w-full h-full p-12 pl-20 flex flex-col">
              {/* 书本标题 */}
              <motion.div
                className="text-center mb-8 relative"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8 }}
              >
                {/* 标题背景装饰 */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-slate-700/20 to-transparent rounded-xl blur-sm"></div>

                <div className="relative z-10">
                  <div className="flex items-center justify-center mb-4">
                    <motion.div
                      animate={{ rotate: [0, 5, -5, 0] }}
                      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <BookOpen className="w-8 h-8 text-blue-300 mr-3 drop-shadow-lg" />
                    </motion.div>
                    <h1 className="text-4xl font-serif font-bold bg-gradient-to-r from-slate-100 via-blue-100 to-slate-100 bg-clip-text text-transparent tracking-wide drop-shadow-lg">
                      答案之书
                    </h1>
                    <motion.div
                      animate={{ scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                    >
                      <Sparkles className="w-6 h-6 text-purple-300 ml-3 drop-shadow-lg" />
                    </motion.div>
                  </div>

                  {/* 装饰性分割线 */}
                  <div className="flex items-center justify-center mb-4">
                    <div className="w-8 h-0.5 bg-gradient-to-r from-transparent to-blue-400"></div>
                    <div className="w-16 h-0.5 bg-gradient-to-r from-blue-400 via-purple-400 to-blue-400 mx-2"></div>
                    <div className="w-8 h-0.5 bg-gradient-to-r from-blue-400 to-transparent"></div>
                  </div>

                  <p className="text-lg text-slate-200 font-serif italic mb-1 drop-shadow-sm">向智者提问，获得深度洞察</p>
                  <p className="text-sm text-slate-300 drop-shadow-sm">与历史上最伟大的思想家进行对话</p>
                </div>
              </motion.div>

              {/* 书本内容区域 */}
              <div className="flex-1 flex flex-col justify-center items-center relative">
                {/* 装饰性文字 */}
                <motion.div
                  className="absolute top-0 left-0 right-0 text-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 1, delay: 0.5 }}
                >
                  <p className="text-slate-400/80 text-sm font-serif italic">
                    "知识的真正目的是为了行动，而不是为了思辨。" —— 亚里士多德
                  </p>
                </motion.div>

                {/* 提示框 */}
                <motion.div
                  className="bg-slate-700/80 border border-slate-600/50 rounded-xl p-6 text-left mb-6 max-w-2xl"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.8, delay: 0.3 }}
                >
                  <p className="text-slate-200 text-sm mb-2 font-serif">
                    💡 <strong>提示：</strong>你可以指明邀请特定的智者参与对话
                  </p>
                  <p className="text-slate-300 text-xs leading-relaxed font-serif">
                    例如："请苏格拉底和孔子讨论教育的本质"、"邀请爱因斯坦解释相对论"、"让马斯克谈谈创新思维"等。任何历史人物、思想家、科学家都可以被邀请！
                  </p>
                </motion.div>

                {/* 问题输入框 - 整合到书本内容中 */}
                <motion.div
                  className="relative bg-slate-700/60 border border-slate-600/40 rounded-xl p-4 max-w-2xl w-full mb-6 overflow-hidden"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: 0.5 }}
                >
                  {/* 输入框背景装饰 */}
                  <div className="absolute inset-0 bg-gradient-to-br from-slate-600/30 via-transparent to-slate-800/30"></div>
                  <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-slate-400/50 to-transparent"></div>

                  <div className="relative z-10">
                  <form onSubmit={handleSubmit} className="space-y-3">
                    <div className="relative">
                      <textarea
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        onFocus={() => setFocusMode(true)}
                        placeholder="请输入你想探索的问题..."
                        className="w-full h-16 px-3 py-2 bg-slate-600/50 border border-slate-500/50 rounded-lg text-slate-100 placeholder-slate-400/80 focus:outline-none focus:ring-1 focus:ring-slate-400 focus:border-transparent resize-none backdrop-blur-sm font-serif text-sm cursor-pointer"
                        maxLength={300}
                        disabled={isLoading}
                        readOnly
                      />
                      <div className="absolute bottom-2 right-2 text-xs text-slate-400/80">
                        {question.length}/300
                      </div>
                    </div>

                    <motion.button
                      type="submit"
                      disabled={!question.trim() || isLoading}
                      className="relative w-full py-3 px-4 bg-gradient-to-r from-blue-600/90 via-indigo-600/90 to-purple-600/90 text-white font-medium rounded-lg hover:from-blue-500/90 hover:via-indigo-500/90 hover:to-purple-500/90 focus:outline-none focus:ring-2 focus:ring-blue-400/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center space-x-2 shadow-lg hover:shadow-xl text-sm overflow-hidden"
                      style={{
                        boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
                      }}
                      whileHover={{
                        scale: 1.03,
                        boxShadow: '0 6px 25px rgba(59, 130, 246, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)'
                      }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {/* 按钮背景光效 */}
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-400/20 via-indigo-400/20 to-purple-400/20 rounded-lg blur-sm"></div>

                      {/* 按钮内容 */}
                      <div className="relative z-10 flex items-center justify-center space-x-2">
                        {isLoading ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            <span className="font-serif">正在邀请智者...</span>
                          </>
                        ) : (
                          <>
                            <Send className="w-4 h-4" />
                            <span className="font-serif tracking-wide">开始对话</span>
                          </>
                        )}
                      </div>

                      {/* 按钮顶部高光 */}
                      <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-white/30 to-transparent rounded-t-lg"></div>
                    </motion.button>
                  </form>
                  </div>
                </motion.div>

                {/* 示例问题卡片 */}
                <motion.div
                  className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl w-full mb-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.8, delay: 0.7 }}
                >
                  {[
                    "请苏格拉底和孔子讨论教育的真正目的是什么？",
                    "邀请爱因斯坦和霍金解释时间的本质",
                    "让马克思和亚当·斯密辩论资本主义的未来",
                    "请达芬奇和乔布斯谈论创新与艺术的关系"
                  ].map((example, index) => (
                    <motion.button
                      key={index}
                      onClick={() => setQuestion(example)}
                      className="relative p-3 bg-slate-700/60 border border-slate-600/40 rounded-lg text-xs text-slate-200 hover:bg-slate-600/60 hover:border-slate-500/60 transition-all duration-200 text-left leading-relaxed shadow-sm hover:shadow-md font-serif overflow-hidden"
                      disabled={isLoading}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, delay: 0.9 + index * 0.1 }}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {/* 卡片装饰 */}
                      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-slate-400/30 to-transparent"></div>
                      <div className="absolute bottom-0 right-0 w-4 h-4 border-r border-b border-slate-500/30 rounded-br-lg"></div>

                      <div className="relative z-10">
                        {example}
                      </div>
                    </motion.button>
                  ))}
                </motion.div>

                {/* 底部装饰 */}
                <motion.div
                  className="absolute bottom-0 left-0 right-0 text-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 1, delay: 1 }}
                >
                  <div className="w-24 h-0.5 bg-gradient-to-r from-transparent via-slate-400 to-transparent mx-auto mb-2"></div>
                  <p className="text-slate-400/80 text-xs font-serif">第一页</p>
                </motion.div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 专注模式覆盖层 */}
      <AnimatePresence>
        {focusMode && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* 背景遮罩 */}
            <div className="absolute inset-0 bg-black/95 backdrop-blur-sm"></div>

            {/* 专注模式内容 */}
            <div className="relative z-10 w-full max-w-2xl mx-auto px-8">
              {/* 关闭按钮 */}
              <motion.button
                onClick={() => setFocusMode(false)}
                className="absolute -top-16 right-0 w-12 h-12 bg-slate-700/80 hover:bg-slate-600/80 rounded-full flex items-center justify-center text-slate-300 hover:text-white transition-all duration-200"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <X className="w-6 h-6" />
              </motion.button>

              {/* 呼吸文字 */}
              <motion.div
                className="text-center mb-12"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
              >
                <motion.p
                  className="text-xl text-slate-200 font-serif leading-relaxed"
                  animate={{
                    opacity: [0.6, 1, 0.6],
                    scale: [0.98, 1.02, 0.98],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                  }}
                >
                  静下心来 闭上眼睛 询问自己的内心
                </motion.p>
                <motion.p
                  className="text-lg text-slate-300 font-serif mt-2"
                  animate={{
                    opacity: [0.4, 0.8, 0.4],
                  }}
                  transition={{
                    duration: 4,
                    repeat: Infinity,
                    ease: "easeInOut",
                    delay: 0.5,
                  }}
                >
                  你想问的是什么
                </motion.p>
              </motion.div>

              {/* 专注模式输入框 */}
              <motion.div
                className="relative"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3, duration: 0.4 }}
              >
                <div className="relative">
                  <textarea
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="在这里写下你内心深处的问题..."
                    className="w-full h-32 px-6 py-4 bg-slate-800/80 border-2 border-slate-600/50 rounded-2xl text-slate-100 placeholder-slate-400/80 focus:outline-none focus:ring-2 focus:ring-blue-400/50 focus:border-blue-400/50 resize-none backdrop-blur-sm font-serif text-lg leading-relaxed"
                    maxLength={300}
                    disabled={isLoading}
                    autoFocus
                  />
                  <div className="absolute bottom-4 right-4 text-sm text-slate-400/80">
                    {question.length}/300
                  </div>
                </div>

                {/* 专注模式提交按钮 */}
                <motion.button
                  onClick={(e) => {
                    e.preventDefault();
                    setFocusMode(false);
                    if (question.trim()) {
                      handleSubmit(e as any);
                    }
                  }}
                  disabled={!question.trim() || isLoading}
                  className="w-full mt-6 py-4 px-6 bg-gradient-to-r from-blue-600/90 via-indigo-600/90 to-purple-600/90 text-white font-medium rounded-2xl hover:from-blue-500/90 hover:via-indigo-500/90 hover:to-purple-500/90 focus:outline-none focus:ring-2 focus:ring-blue-400/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center space-x-3 shadow-lg text-lg font-serif"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                >
                  {isLoading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                      <span>正在邀请智者...</span>
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      <span>开始深度对话</span>
                    </>
                  )}
                </motion.button>
              </motion.div>

              {/* 底部提示 */}
              <motion.p
                className="text-center text-slate-400 text-sm mt-8 font-serif"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                按 ESC 键退出专注模式
              </motion.p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
