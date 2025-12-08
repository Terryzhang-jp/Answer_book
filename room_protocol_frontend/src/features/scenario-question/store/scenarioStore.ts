/**
 * Scenario question state management
 */

import { create } from 'zustand';
import { ScenarioQuestionData } from '../types/scenario';

interface ScenarioState {
  // Current scenario question data
  currentQuestion: ScenarioQuestionData | null;

  // User's scenario description
  userScenarioDescription: string;

  // Generation state
  isGeneratingQuestion: boolean;
  isSubmittingResponse: boolean;

  // Error state
  generationError: string | null;
  submissionError: string | null;

  // Display state
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
