'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';

interface BackgroundOverlayProps {
  isActive: boolean;
  message?: string;
}

export default function BackgroundOverlay({ 
  isActive, 
  message = "智者正在思考..." 
}: BackgroundOverlayProps) {
  return (
    <AnimatePresence>
      {isActive && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 flex items-center justify-center"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="bg-gray-800/90 rounded-2xl p-6 flex items-center space-x-4 shadow-2xl"
          >
            <Loader2 className="w-8 h-8 text-amber-400 animate-spin" />
            <span className="text-white text-lg font-medium">{message}</span>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
