'use client';

import React, { useState, useEffect, type FormEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send, CornerDownRight, ArrowLeft, ArrowRight, BarChart3 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { useTypewriter } from "@/hooks/use-typewriter";
import { CharacterResponse } from "@/types/api";
import AnalysisModal from "./AnalysisModal";

// --- 类型定义 ---
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

interface BookOfAnswersProps {
  turns: Turn[];
  onSendMessage: (question: string) => void;
  isLoading: boolean;
  conversationAnalysis: any;
  roomAnnouncement?: string;
}

// --- 专家颜色映射 ---
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

// --- 专家回复组件 (带打字机效果) ---
const ExpertResponse = ({ 
  expert, 
  isPageActive 
}: { 
  expert: ExpertMessage; 
  isPageActive: boolean;
}) => {
  const [currentPhase, setCurrentPhase] = useState<'bodyLanguage' | 'thinking' | 'speaking' | 'complete'>('bodyLanguage');
  const [allComplete, setAllComplete] = useState(false);

  const bodyLanguageTypewriter = useTypewriter(expert.bodyLanguage, 30);
  const thinkingTypewriter = useTypewriter(expert.thinking, 25);
  const speakingTypewriter = useTypewriter(expert.speaking, 20);

  useEffect(() => {
    if (isPageActive && !allComplete) {
      setCurrentPhase('bodyLanguage');
      bodyLanguageTypewriter.restart();
    }
  }, [isPageActive]);

  useEffect(() => {
    if (currentPhase === 'bodyLanguage' && !bodyLanguageTypewriter.isTyping && bodyLanguageTypewriter.displayedText) {
      setTimeout(() => {
        setCurrentPhase('thinking');
        thinkingTypewriter.restart();
      }, 500);
    } else if (currentPhase === 'thinking' && !thinkingTypewriter.isTyping && thinkingTypewriter.displayedText) {
      setTimeout(() => {
        setCurrentPhase('speaking');
        speakingTypewriter.restart();
      }, 500);
    } else if (currentPhase === 'speaking' && !speakingTypewriter.isTyping && speakingTypewriter.displayedText) {
      setCurrentPhase('complete');
      setAllComplete(true);
    }
  }, [currentPhase, bodyLanguageTypewriter.isTyping, thinkingTypewriter.isTyping, speakingTypewriter.isTyping]);

  const skipAll = () => {
    bodyLanguageTypewriter.skipAnimation();
    thinkingTypewriter.skipAnimation();
    speakingTypewriter.skipAnimation();
    setCurrentPhase('complete');
    setAllComplete(true);
  };

  return (
    <div className="space-y-4 relative">
      {/* 专家名称 */}
      <div className="flex items-center space-x-3 mb-8">
        <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center text-white font-medium text-sm">
          {expert.name.charAt(0)}
        </div>
        <h3 className="font-medium text-lg text-black">
          {expert.name}
        </h3>
      </div>

      {/* 一键显示按钮 */}
      {!allComplete && isPageActive && (
        <Button
          variant="ghost"
          size="sm"
          className="absolute top-0 right-0 text-gray-400 hover:text-black hover:bg-gray-100"
          onClick={skipAll}
        >
          一键显示
          <CornerDownRight className="w-4 h-4 ml-2" />
        </Button>
      )}

      {/* 肢体语言 */}
      {expert.bodyLanguage && (
        <div className="border-l-2 border-gray-300 pl-4 mb-6">
          <div className="flex items-center mb-2">
            <span className="text-gray-600 font-medium text-sm">肢体语言</span>
          </div>
          <div className="text-gray-700 text-base italic leading-relaxed">
            {allComplete ? expert.bodyLanguage : bodyLanguageTypewriter.displayedText}
            {currentPhase === 'bodyLanguage' && bodyLanguageTypewriter.isTyping && (
              <span className="animate-pulse">|</span>
            )}
          </div>
        </div>
      )}

      {/* 内心思考 */}
      {expert.thinking && (currentPhase !== 'bodyLanguage' || allComplete) && (
        <div className="border-l-2 border-gray-300 pl-4 mb-6">
          <div className="flex items-center mb-2">
            <span className="text-gray-600 font-medium text-sm">内心思考</span>
          </div>
          <div className="text-gray-700 text-base italic leading-relaxed">
            {allComplete ? expert.thinking : thinkingTypewriter.displayedText}
            {currentPhase === 'thinking' && thinkingTypewriter.isTyping && (
              <span className="animate-pulse">|</span>
            )}
          </div>
        </div>
      )}

      {/* 发言内容 */}
      {(currentPhase === 'speaking' || currentPhase === 'complete' || allComplete) && (
        <div className="mb-6">
          <div className="flex items-center mb-3">
            <span className="text-gray-600 font-medium text-sm">发言</span>
          </div>
          <div className="ebook-text text-lg">
            {allComplete ? expert.speaking : speakingTypewriter.displayedText}
            {currentPhase === 'speaking' && speakingTypewriter.isTyping && (
              <span className="animate-pulse">|</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// --- 书页组件 ---
const BookPage = ({
  turn,
  direction,
  isActive,
  roomAnnouncement
}: {
  turn: Turn;
  direction: number;
  isActive: boolean;
  roomAnnouncement?: string;
}) => {
  const pageVariants = {
    initial: (direction: number) => ({
      opacity: 0,
      rotateY: direction > 0 ? 180 : -180,
      transition: { duration: 0.6 },
    }),
    animate: {
      opacity: 1,
      rotateY: 0,
      transition: { duration: 0.6 },
    },
    exit: (direction: number) => ({
      opacity: 0,
      rotateY: direction > 0 ? -180 : 180,
      transition: { duration: 0.6 },
    }),
  };

  return (
    <motion.div
      key={turn.id}
      custom={direction}
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="absolute inset-0 flex ebook-page rounded-lg overflow-hidden"
      style={{ transformStyle: "preserve-3d" }}
    >
      {/* 左页 - 房间宣告和用户问题 */}
      <div className="w-1/2 p-16 flex flex-col justify-center bg-white border-r border-gray-200">
        <div className="max-w-lg mx-auto">
          {/* 房间宣告 - 只在第一页显示 */}
          {roomAnnouncement && turn.id === 1 && (
            <div className="mb-12">
              <h2 className="text-sm text-amber-700 mb-4 uppercase tracking-wider font-medium font-serif">房间宣告</h2>
              <div className="bg-amber-50/80 border border-amber-200/50 rounded-lg p-6 mb-8">
                <p className="text-amber-800 font-medium text-lg font-serif leading-relaxed">
                  {roomAnnouncement}
                </p>
              </div>
              <div className="w-16 h-px bg-amber-600 mb-8"></div>
            </div>
          )}

          <h2 className="text-sm text-gray-500 mb-8 uppercase tracking-wider font-medium">你的提问</h2>
          <p className="ebook-text text-2xl mb-12">
            {turn.userQuestion}
          </p>
          <div className="w-16 h-px bg-black"></div>
        </div>
      </div>

      {/* 右页 - 专家回答 */}
      <div className="w-1/2 p-16 bg-white overflow-y-auto">
        <div className="space-y-12">
          {turn.expertResponses.map((expert, index) => (
            <React.Fragment key={expert.id}>
              <ExpertResponse expert={expert} isPageActive={isActive} />
              {index < turn.expertResponses.length - 1 && (
                <hr className="border-gray-200 my-10" />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </motion.div>
  );
};

// --- 主组件 ---
export default function BookOfAnswers({
  turns,
  onSendMessage,
  isLoading,
  conversationAnalysis,
  roomAnnouncement
}: BookOfAnswersProps) {
  const [input, setInput] = useState("");
  const [[page, direction], setPage] = useState([0, 0]);
  const [showAnalysis, setShowAnalysis] = useState(false);

  // 当有新的turn时，自动跳转到最新页
  useEffect(() => {
    if (turns.length > 0) {
      setPage([turns.length - 1, 1]);
    }
  }, [turns.length]);

  const paginate = (newDirection: number) => {
    setPage([page + newDirection, newDirection]);
  };

  const handleSendMessage = (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    onSendMessage(input.trim());
    setInput("");
  };

  return (
    <div className="h-screen w-screen overflow-hidden ebook-reader flex flex-col relative bg-white">
      {/* 右上角回顾分析按钮 */}
      <Button
        onClick={() => setShowAnalysis(true)}
        className="absolute top-4 right-4 z-40 bg-black/80 hover:bg-black text-white shadow-lg backdrop-blur-sm border border-gray-300/50"
        size="sm"
      >
        <BarChart3 className="w-4 h-4 mr-2" />
        回顾分析
      </Button>

      {/* 书本容器 - 占满整个屏幕 */}
      <div className="flex-1 flex items-center justify-center">
        <div
          className="w-full h-full relative bg-white"
          style={{ perspective: "2000px" }}
        >
          <AnimatePresence initial={false} custom={direction}>
            {turns.length > 0 && (
              <BookPage
                turn={turns[page]}
                direction={direction}
                isActive={true}
                roomAnnouncement={roomAnnouncement}
              />
            )}
          </AnimatePresence>

          {turns.length === 0 && (
            <div className="w-full h-full flex items-center justify-center text-black text-3xl bg-white rounded-lg">
              <div className="text-center">
                <div className="text-8xl mb-6">📖</div>
                <p className="font-serif text-gray-600">向答案之书提问...</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 底部浮动输入区域 - 超紧凑设计 */}
      <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-xl px-3 transition-all duration-300 ease-in-out opacity-40 hover:opacity-100 group">
        <div className="bg-white/95 backdrop-blur-md border border-gray-200 rounded-lg shadow-lg p-2 transition-all duration-300 ease-in-out group-hover:bg-white group-hover:shadow-xl">
          {/* 导航控制 */}
          {turns.length > 1 && (
            <div className="flex justify-center items-center gap-1 mb-1">
              <Button
                variant="outline"
                onClick={() => paginate(-1)}
                disabled={page === 0}
                size="sm"
                className="text-black border-gray-300 hover:bg-gray-100 font-serif transition-all duration-200 text-xs px-2 py-1"
              >
                <ArrowLeft className="mr-1 w-3 h-3" /> 上一页
              </Button>
              <span className="text-gray-600 text-xs bg-gray-100 px-2 py-1 rounded font-serif">
                {page + 1}/{turns.length}
              </span>
              <Button
                variant="outline"
                onClick={() => paginate(1)}
                disabled={page === turns.length - 1}
                size="sm"
                className="text-black border-gray-300 hover:bg-gray-100 font-serif transition-all duration-200 text-xs px-2 py-1"
              >
                下一页 <ArrowRight className="ml-1 w-3 h-3" />
              </Button>
            </div>
          )}

          {/* 输入表单 */}
          <form
            onSubmit={handleSendMessage}
            className="flex items-center gap-1 bg-gray-50 border border-gray-200 rounded-lg p-1.5 shadow-sm transition-all duration-200 hover:bg-gray-100 hover:shadow-md"
          >
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(e);
                  }
                }}
                placeholder="问题..."
                className="flex-1 resize-none bg-transparent border-none focus-visible:ring-0 text-xs text-black placeholder:text-gray-500 font-serif py-0.5"
                rows={1}
              />
              <Button
                type="submit"
                size="sm"
                variant="ghost"
                disabled={isLoading || !input.trim()}
                className="text-black hover:text-black hover:bg-gray-200 transition-all duration-200 h-6 w-6 p-0"
              >
                {isLoading ? (
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-black" />
                ) : (
                  <Send className="w-3 h-3" />
                )}
              </Button>
          </form>
        </div>
      </div>

      {/* 分析模态框 */}
      <AnalysisModal
        isOpen={showAnalysis}
        onClose={() => setShowAnalysis(false)}
        analysis={conversationAnalysis}
      />
    </div>
  );
}