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

      // Add user message to store
      addUserMessage(question);

      // Call create room API
      const response = await ApiService.createRoom({
        question: question.trim(),
        user_id: 'user_' + Date.now(),
      });

      // Add response to store
      addResponse(response);

      // Navigate to chat page
      router.push('/chat');
    } catch (error) {
      console.error('Question failed:', error);
      setError(error instanceof Error ? error.message : 'Failed to submit question, please try again');
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
            <h1 className="text-5xl font-bold text-white">The Answer Book</h1>
            <Sparkles className="w-8 h-8 text-amber-400 ml-4" />
          </div>
          
          <p className="text-xl text-gray-300 mb-2">
            Ask the wise, gain deep insights
          </p>
          <p className="text-sm text-gray-400 mb-3">
            Have conversations with history's greatest thinkers
          </p>
          <div className="bg-amber-900/20 border border-amber-500/30 rounded-xl p-4 text-left">
            <p className="text-amber-200 text-sm mb-2">
              💡 <strong>Tip:</strong> You can invite specific wise figures to join the conversation
            </p>
            <p className="text-amber-100 text-xs leading-relaxed">
              For example: "Have Socrates and Confucius discuss the essence of education", "Invite Einstein to explain relativity", "Let Musk talk about innovative thinking", etc. Any historical figure, thinker, or scientist can be invited!
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
              placeholder="Enter the question you want to explore..."
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
                <span>Inviting the wise...</span>
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                <span>Start Conversation</span>
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
          <p className="text-sm text-gray-400 mb-4">Or try these thought-provoking questions:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-4xl mx-auto">
            {[
              "Have Socrates and Confucius discuss what is the true purpose of education?",
              "Invite Einstein and Hawking to explain the nature of time",
              "Let Marx and Adam Smith debate the future of capitalism",
              "Have Da Vinci and Steve Jobs discuss the relationship between innovation and art",
              "Invite Nietzsche and Buddha to explore suffering and wisdom",
              "Let Turing and Musk predict the impact of AI on humanity"
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
