import { create } from 'zustand';
import {
  AnswerResponse,
  CharacterResponse,
  ConversationAnalysis
} from '@/types/api';
import { safeClearItems } from '@/utils/storage';

interface Message {
  id: string;
  type: 'user' | 'system' | 'expert';
  content: string;
  timestamp: string;
  characterName?: string;
  characterRole?: string;
  thinking?: string;
  speaking?: string;
  bodyLanguage?: string;
}

interface ConversationState {
  // Current conversation state
  currentThreadId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;

  // Room state
  roomAnnouncement: string | null;
  currentExperts: string[];
  dialogueMode: 'single' | 'free_dialogue';

  // Analysis data
  conversationAnalysis: ConversationAnalysis | null;



  // Insight display state
  insightDisplay: {
    enabled: boolean;
    sessionId: string | null;
    insight: string;
    isActive: boolean;
    isCompleted: boolean;
    isLoading: boolean;
  };

  // Action methods
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addUserMessage: (content: string) => void;
  addResponse: (response: AnswerResponse) => void;
  clearConversation: () => void;
  startNewDiscussion: () => void;
  setThreadId: (threadId: string) => void;



  // Insight display action methods
  startInsightDisplay: (sessionId: string, insight: string) => void;
  completeInsightDisplay: () => void;
  skipInsightDisplay: () => void;
  setInsightLoading: (loading: boolean) => void;
  resetInsightDisplay: () => void;
}

export const useConversationStore = create<ConversationState>((set) => ({
  // Initial state
  currentThreadId: null,
  messages: [],
  isLoading: false,
  error: null,
  roomAnnouncement: null,
  currentExperts: [],
  dialogueMode: 'single',
  conversationAnalysis: null,



  // Insight display initial state
  insightDisplay: {
    enabled: false,
    sessionId: null,
    insight: '',
    isActive: false,
    isCompleted: false,
    isLoading: false,
  },

  // Set loading state
  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  // Set error message
  setError: (error: string | null) => {
    set({ error });
  },

  // Add user message
  addUserMessage: (content: string) => {
    const message: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  // Add system response
  addResponse: (response: AnswerResponse) => {
    const newMessages: Message[] = [];
    const baseTimestamp = Date.now();

    // Process character responses
    response.character_responses.forEach((charResponse: CharacterResponse, index: number) => {
      const message: Message = {
        id: `${baseTimestamp}-${index}-${charResponse.character_name}`,
        type: charResponse.character_role === 'system' ? 'system' : 'expert',
        content: charResponse.speaking,
        timestamp: response.timestamp,
        characterName: charResponse.character_name,
        characterRole: charResponse.character_role,
        thinking: charResponse.thinking,
        speaking: charResponse.speaking,
        bodyLanguage: charResponse.body_language,
      };
      newMessages.push(message);
    });

    // Update expert list
    const experts = response.character_responses
      .filter(char => char.character_role !== 'system')
      .map(char => char.character_name);

    set((state) => ({
      messages: [...state.messages, ...newMessages],
      currentThreadId: response.thread_id,
      roomAnnouncement: response.room_announcement,
      currentExperts: experts,
      dialogueMode: response.dialogue_mode,
      conversationAnalysis: response.conversation_analysis || null,
    }));
  },

  // Clear conversation
  clearConversation: () => {
    set({
      currentThreadId: null,
      messages: [],
      roomAnnouncement: null,
      currentExperts: [],
      dialogueMode: 'single',
      conversationAnalysis: null,
      error: null,

      insightDisplay: {
        enabled: false,
        sessionId: null,
        insight: '',
        isActive: false,
        isCompleted: false,
        isLoading: false,
      },
    });
  },

  // Start new discussion (clear all data including localStorage)
  startNewDiscussion: () => {
    // Clear localStorage related data (SSR compatible)
    const keysToRemove = [
      'conversation-storage',
      'chat-history',
      'current-thread',
      'session-data',
      'thread-timestamps',
      'room-announcement',
      'current-experts'
    ];

    const clearedCount = safeClearItems(keysToRemove);
    console.log(`Cleared ${clearedCount}/${keysToRemove.length} localStorage items`);

    // Reset store state
    set({
      currentThreadId: null,
      messages: [],
      roomAnnouncement: null,
      currentExperts: [],
      dialogueMode: 'single',
      conversationAnalysis: null,
      error: null,
      isLoading: false,

      insightDisplay: {
        enabled: false,
        sessionId: null,
        insight: '',
        isActive: false,
        isCompleted: false,
        isLoading: false,
      },
    });
  },

  // Set thread ID
  setThreadId: (threadId: string) => {
    set({ currentThreadId: threadId });
  },



  // Insight display action methods

  // Start insight display
  startInsightDisplay: (sessionId: string, insight: string) => {
    set((state) => ({
      insightDisplay: {
        ...state.insightDisplay,
        enabled: true,
        sessionId,
        insight,
        isActive: true,
        isCompleted: false,
        isLoading: insight ? false : true, // Set to loading state if no insight content
      }
    }));
  },

  // Complete insight display
  completeInsightDisplay: () => {
    set((state) => ({
      insightDisplay: {
        ...state.insightDisplay,
        isActive: false,
        isCompleted: true,
      }
    }));
  },

  // Skip insight display
  skipInsightDisplay: () => {
    set((state) => ({
      insightDisplay: {
        ...state.insightDisplay,
        enabled: false,
        isActive: false,
        isCompleted: true,
      }
    }));
  },

  // Set insight loading state
  setInsightLoading: (loading: boolean) => {
    set((state) => ({
      insightDisplay: {
        ...state.insightDisplay,
        isLoading: loading,
      }
    }));
  },

  // Reset insight display state
  resetInsightDisplay: () => {
    set(() => ({
      insightDisplay: {
        enabled: false,
        sessionId: null,
        insight: '',
        isActive: false,
        isCompleted: false,
        isLoading: false,
      }
    }));
  },
}));
