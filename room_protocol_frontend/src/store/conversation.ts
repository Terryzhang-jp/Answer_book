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
  isAlreadyShown?: boolean; // 标记是否已在模态框中显示过
}

interface ConversationState {
  // 当前对话状态
  currentThreadId: string | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;

  // 房间状态
  roomAnnouncement: string | null;
  currentExperts: string[];
  dialogueMode: 'single' | 'free_dialogue';

  // 分析数据
  conversationAnalysis: ConversationAnalysis | null;



  // Insight显示状态
  insightDisplay: {
    enabled: boolean;
    sessionId: string | null;
    insight: string;
    isActive: boolean;
    isCompleted: boolean;
    isLoading: boolean;
  };

  // 专家模态框状态
  expertModal: {
    isOpen: boolean;
    experts: CharacterResponse[];
    currentIndex: number;
    showAll: boolean;
    isAutoPlaying: boolean;
  };

  // 背景遮罩状态
  isWaitingForExperts: boolean;

  // 操作方法
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addUserMessage: (content: string) => void;
  addResponse: (response: AnswerResponse, isAlreadyShown?: boolean) => void;
  clearConversation: () => void;
  startNewDiscussion: () => void;
  setThreadId: (threadId: string) => void;



  // Insight显示操作方法
  startInsightDisplay: (sessionId: string, insight: string) => void;
  completeInsightDisplay: () => void;
  skipInsightDisplay: () => void;
  setInsightLoading: (loading: boolean) => void;
  resetInsightDisplay: () => void;

  // 专家模态框操作方法
  openExpertModal: (experts: CharacterResponse[]) => void;
  closeExpertModal: () => void;
  nextExpert: () => void;
  showAllExperts: () => void;
  setWaitingForExperts: (waiting: boolean) => void;
}

export const useConversationStore = create<ConversationState>((set) => ({
  // 初始状态
  currentThreadId: null,
  messages: [],
  isLoading: false,
  error: null,
  roomAnnouncement: null,
  currentExperts: [],
  dialogueMode: 'single',
  conversationAnalysis: null,



  // Insight显示初始状态
  insightDisplay: {
    enabled: false,
    sessionId: null,
    insight: '',
    isActive: false,
    isCompleted: false,
    isLoading: false,
  },

  // 专家模态框初始状态
  expertModal: {
    isOpen: false,
    experts: [],
    currentIndex: 0,
    showAll: false,
    isAutoPlaying: true,
  },

  // 背景遮罩初始状态
  isWaitingForExperts: false,

  // 设置加载状态
  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  // 设置错误信息
  setError: (error: string | null) => {
    set({ error });
  },

  // 添加用户消息
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

  // 添加系统响应
  addResponse: (response: AnswerResponse, isAlreadyShown: boolean = false) => {
    const newMessages: Message[] = [];
    const baseTimestamp = Date.now();

    // 处理角色回应
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
        isAlreadyShown, // 添加已显示标记
      };
      newMessages.push(message);
    });

    // 更新专家列表
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

  // 清空对话
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

  // 开启新讨论（清空所有数据包括localStorage）
  startNewDiscussion: () => {
    // 清空localStorage中的相关数据（SSR兼容）
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
    console.log(`清空了 ${clearedCount}/${keysToRemove.length} 个localStorage项`);

    // 重置store状态
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

  // 设置线程ID
  setThreadId: (threadId: string) => {
    set({ currentThreadId: threadId });
  },



  // Insight显示操作方法

  // 开始Insight显示
  startInsightDisplay: (sessionId: string, insight: string) => {
    set((state) => ({
      insightDisplay: {
        ...state.insightDisplay,
        enabled: true,
        sessionId,
        insight,
        isActive: true,
        isCompleted: false,
        isLoading: insight ? false : true, // 如果没有insight内容，设置为加载状态
      }
    }));
  },

  // 完成Insight显示
  completeInsightDisplay: () => {
    set((state) => ({
      insightDisplay: {
        ...state.insightDisplay,
        isActive: false,
        isCompleted: true,
      }
    }));
  },

  // 跳过Insight显示
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

  // 设置Insight加载状态
  setInsightLoading: (loading: boolean) => {
    set((state) => ({
      insightDisplay: {
        ...state.insightDisplay,
        isLoading: loading,
      }
    }));
  },

  // 重置Insight显示状态
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

  // 打开专家模态框
  openExpertModal: (experts: CharacterResponse[]) => {
    set(() => ({
      expertModal: {
        isOpen: true,
        experts,
        currentIndex: 0,
        showAll: false,
        isAutoPlaying: true,
      },
      isWaitingForExperts: false,
    }));
  },

  // 关闭专家模态框
  closeExpertModal: () => {
    set(() => ({
      expertModal: {
        isOpen: false,
        experts: [],
        currentIndex: 0,
        showAll: false,
        isAutoPlaying: true,
      },
    }));
  },

  // 切换到下一个专家
  nextExpert: () => {
    set((state) => ({
      expertModal: {
        ...state.expertModal,
        currentIndex: Math.min(state.expertModal.currentIndex + 1, state.expertModal.experts.length - 1),
      }
    }));
  },

  // 显示所有专家
  showAllExperts: () => {
    set((state) => ({
      expertModal: {
        ...state.expertModal,
        showAll: true,
        isAutoPlaying: false,
      }
    }));
  },

  // 设置等待专家状态
  setWaitingForExperts: (waiting: boolean) => {
    set({ isWaitingForExperts: waiting });
  },
}));
