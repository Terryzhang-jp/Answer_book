'use client';

import { useState, useEffect, useCallback } from 'react';

interface UseTypewriterReturn {
  displayedText: string;
  isTyping: boolean;
  skipAnimation: () => void;
  restart: () => void;
}

export function useTypewriter(
  text: string,
  speed: number = 50
): UseTypewriterReturn {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isSkipped, setIsSkipped] = useState(false);

  const skipAnimation = useCallback(() => {
    setIsSkipped(true);
    setDisplayedText(text);
    setIsTyping(false);
  }, [text]);

  const restart = useCallback(() => {
    setDisplayedText('');
    setIsTyping(true);
    setIsSkipped(false);
  }, []);

  useEffect(() => {
    if (!text) {
      setIsTyping(false);
      return;
    }

    if (isSkipped) {
      setDisplayedText(text);
      setIsTyping(false);
      return;
    }

    setIsTyping(true);
    let currentIndex = 0;
    const intervalTime = 1000 / speed;

    const timer = setInterval(() => {
      if (currentIndex < text.length && !isSkipped) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(timer);
        setIsTyping(false);
      }
    }, intervalTime);

    return () => clearInterval(timer);
  }, [text, speed, isSkipped]);

  return {
    displayedText,
    isTyping,
    skipAnimation,
    restart,
  };
}