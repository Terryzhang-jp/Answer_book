'use client';

import { useState, useEffect, useCallback } from 'react';

interface StreamingTextProps {
  text: string;
  speed?: number; // Characters per second
  onComplete?: () => void;
  className?: string;
  showSkipButton?: boolean; // Whether to show skip button
  skipButtonText?: string; // Skip button text
}

export const StreamingText: React.FC<StreamingTextProps> = ({
  text,
  speed = 10, // Default 10 characters per second
  onComplete,
  className = '',
  showSkipButton = false,
  skipButtonText = 'Show All'
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const [isSkipped, setIsSkipped] = useState(false);

  // Skip streaming effect, show all content directly
  const handleSkip = useCallback(() => {
    setIsSkipped(true);
    setDisplayedText(text);
    setIsComplete(true);
    onComplete?.();
  }, [text, onComplete]);

  useEffect(() => {
    if (!text) {
      setIsComplete(true);
      onComplete?.();
      return;
    }

    setDisplayedText('');
    setIsComplete(false);
    setIsSkipped(false);

    let currentIndex = 0;
    const intervalTime = 1000 / speed; // Millisecond interval

    const timer = setInterval(() => {
      if (currentIndex < text.length && !isSkipped) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(timer);
        if (!isSkipped) {
          setIsComplete(true);
          onComplete?.();
        }
      }
    }, intervalTime);

    return () => clearInterval(timer);
  }, [text, speed, onComplete, isSkipped]);

  return (
    <span className="relative inline-block w-full">
      <span className={className}>
        {displayedText}
        {!isComplete && <span className="animate-pulse">|</span>}
      </span>

      {/* Skip button */}
      {showSkipButton && !isComplete && !isSkipped && (
        <button
          onClick={handleSkip}
          className="ml-2 px-2 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
          title="Skip streaming effect, show all content directly"
        >
          {skipButtonText}
        </button>
      )}
    </span>
  );
};

interface StreamingCharacterResponseProps {
  message: {
    characterName: string;
    bodyLanguage?: string;
    thinking?: string;
    speaking?: string;
  };
  speed?: number;
  guestIndex?: number; // Guest index
  totalGuests?: number; // Total guests
  onComplete?: () => void; // Completion callback
  shouldStart?: boolean; // Should start
  showSkipButton?: boolean; // Whether to show skip button
}

export const StreamingCharacterResponse: React.FC<StreamingCharacterResponseProps> = ({
  message,
  speed = 10,
  guestIndex = 0,
  totalGuests = 1,
  onComplete,
  shouldStart = true,
  showSkipButton = false
}) => {
  const [currentPhase, setCurrentPhase] = useState<'waiting' | 'bodyLanguage' | 'thinking' | 'speaking' | 'complete'>('waiting');
  const [isReady, setIsReady] = useState(false);
  const [isSkipped, setIsSkipped] = useState(false);

  // Show all content at once
  const handleSkipAll = useCallback(() => {
    setIsSkipped(true);
    setCurrentPhase('complete');
    onComplete?.();
  }, [onComplete]);

  // Handle startup logic
  useEffect(() => {
    if (shouldStart && !isSkipped) {
      // If should start, begin immediately (first guest) or with slight delay (subsequent guests)
      const delay = guestIndex === 0 ? 0 : 500; // Subsequent guests delay 500ms
      const timer = setTimeout(() => {
        setIsReady(true);
        setCurrentPhase('bodyLanguage');
      }, delay);

      return () => clearTimeout(timer);
    }
  }, [shouldStart, guestIndex, isSkipped]);

  const handlePhaseComplete = useCallback(() => {
    if (isSkipped) return; // If already skipped, don't handle phase completion

    if (currentPhase === 'bodyLanguage') {
      setCurrentPhase('thinking');
    } else if (currentPhase === 'thinking') {
      setCurrentPhase('speaking');
    } else if (currentPhase === 'speaking') {
      setCurrentPhase('complete');
      // When guest fully completes, notify parent component
      onComplete?.();
    }
  }, [currentPhase, onComplete, isSkipped]);

  // If no body language, start from thinking
  useEffect(() => {
    if (!message.bodyLanguage && currentPhase === 'bodyLanguage') {
      setCurrentPhase('thinking');
    }
  }, [message.bodyLanguage, currentPhase]);

  // If no thinking, go from body language directly to speaking
  useEffect(() => {
    if (!message.thinking && currentPhase === 'thinking') {
      setCurrentPhase('speaking');
    }
  }, [message.thinking, currentPhase]);

  // If still waiting, show waiting state
  if (!isReady) {
    return (
      <div className="space-y-3">
        <div className="bg-gray-100 border-l-4 border-gray-300 p-3 rounded">
          <div className="flex items-center">
            <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mr-2"></div>
            <span className="text-gray-500 text-sm">
              {shouldStart ?
                `Preparing ${message.characterName}...` :
                `Waiting for ${message.characterName}'s turn... (${guestIndex + 1}/${totalGuests})`
              }
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3 relative">
      {/* Show all button - fixed at top right */}
      {showSkipButton && currentPhase !== 'complete' && !isSkipped && (
        <div className="fixed top-4 right-4 z-50">
          <button
            onClick={handleSkipAll}
            className="px-4 py-2 text-sm bg-blue-500 hover:bg-blue-600 text-white rounded-lg shadow-lg transition-colors flex items-center space-x-2"
            title="Skip streaming effect, show all content directly"
          >
            <span>⚡</span>
            <span>Show All</span>
          </button>
        </div>
      )}
      {/* Body Language */}
      {message.bodyLanguage && (
        <div className="bg-purple-800/20 border-l-4 border-purple-400 p-3 rounded">
          <div className="flex items-center mb-2">
            <span className="text-black font-medium text-sm">🎭 Body Language</span>
          </div>
          <div className="text-black text-sm italic leading-relaxed">
            {currentPhase === 'bodyLanguage' && !isSkipped ? (
              <StreamingText
                text={message.bodyLanguage}
                speed={speed}
                onComplete={handlePhaseComplete}
              />
            ) : (
              message.bodyLanguage
            )}
          </div>
        </div>
      )}

      {/* Inner Thoughts */}
      {message.thinking && (currentPhase === 'thinking' || currentPhase === 'speaking' || currentPhase === 'complete') && (
        <div className="bg-orange-800/20 border-l-4 border-orange-400 p-3 rounded">
          <div className="flex items-center mb-2">
            <span className="text-black font-medium text-sm">💭 Inner Thoughts</span>
          </div>
          <div className="text-black text-sm italic leading-relaxed">
            {currentPhase === 'thinking' && !isSkipped ? (
              <StreamingText
                text={message.thinking}
                speed={speed}
                onComplete={handlePhaseComplete}
              />
            ) : (currentPhase === 'speaking' || currentPhase === 'complete') ? (
              message.thinking
            ) : (
              ''
            )}
          </div>
        </div>
      )}

      {/* Speaking */}
      {(currentPhase === 'speaking' || currentPhase === 'complete') && (
        <div className="bg-gray-50 border-l-4 border-gray-400 p-3 rounded">
          <div className="flex items-center mb-2">
            <span className="text-gray-700 font-medium text-sm">💬 Speaking</span>
          </div>
          <div className="text-black text-sm leading-relaxed">
            {currentPhase === 'speaking' && !isSkipped ? (
              <StreamingText
                text={message.speaking || ''}
                speed={speed}
                onComplete={handlePhaseComplete}
              />
            ) : currentPhase === 'complete' ? (
              message.speaking
            ) : (
              ''
            )}
          </div>
        </div>
      )}
    </div>
  );
};
