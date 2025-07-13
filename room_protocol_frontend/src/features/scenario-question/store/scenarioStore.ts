/**
 * 场景问题状态管理
 */

import { create } from 'zustand';
import { ScenarioQuestionData } from '../types/scenario';

interface ScenarioState {
  // 当前场景问题数据
  currentQuestion: ScenarioQuestionData | null;
  
  // 用户的场景描述
  userScenarioDescription: string;
  
  // 生成状态
  isGeneratingQuestion: boolean;
  isSubmittingResponse: boolean;
  
  // 错误状态
  generationError: string | null;
  submissionError: string | null;
  
  // 显示状态
  isQuestionVisible: boolean;
  
  // Actions
  setCurrentQuestion: (question: ScenarioQuestionData | null) => void;
  setUserScenarioDescription: (description: string) => void;
  setGeneratingQuestion: (isGenerating: boolean) => void;
  setSubmittingResponse: (isSubmitting: boolean) => void;
  setGenerationError: (error: string | null) => void;
  setSubmissionError: (error: string | null) => void;
  setQuestionVisible: (visible: boolean) => void;
  resetScenarioState: () => void;
}

export const useScenarioStore = create<ScenarioState>((set) => ({
  // Initial state
  currentQuestion: null,
  userScenarioDescription: '',
  isGeneratingQuestion: false,
  isSubmittingResponse: false,
  generationError: null,
  submissionError: null,
  isQuestionVisible: false,

  // Actions
  setCurrentQuestion: (question) => set({ currentQuestion: question }),
  
  setUserScenarioDescription: (description) => set({ userScenarioDescription: description }),
  
  setGeneratingQuestion: (isGenerating) => set({ isGeneratingQuestion: isGenerating }),
  
  setSubmittingResponse: (isSubmitting) => set({ isSubmittingResponse: isSubmitting }),
  
  setGenerationError: (error) => set({ generationError: error }),
  
  setSubmissionError: (error) => set({ submissionError: error }),
  
  setQuestionVisible: (visible) => set({ isQuestionVisible: visible }),
  
  resetScenarioState: () => set({
    currentQuestion: null,
    userScenarioDescription: '',
    isGeneratingQuestion: false,
    isSubmittingResponse: false,
    generationError: null,
    submissionError: null,
    isQuestionVisible: false,
  }),
}));
