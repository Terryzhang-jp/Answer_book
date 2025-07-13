import { create } from 'zustand';
import { ReportData } from '../types/report';

interface ReportState {
  // 当前报告数据
  currentReport: ReportData | null;
  currentProgress: Partial<ReportData> | null; // 流式进度数据

  // 生成状态
  isGenerating: boolean;
  generationStatus: string;
  generationError: string | null;

  // 显示状态
  isReportVisible: boolean;
  currentSection: number; // 当前显示的部分 (0-4)

  // Actions
  setCurrentReport: (report: ReportData | null) => void;
  setCurrentProgress: (progress: Partial<ReportData> | null) => void;
  setGenerating: (isGenerating: boolean) => void;
  setGenerationStatus: (status: string) => void;
  setGenerationError: (error: string | null) => void;
  setReportVisible: (visible: boolean) => void;
  setCurrentSection: (section: number) => void;
  resetReportState: () => void;
}

export const useReportStore = create<ReportState>((set) => ({
  // Initial state
  currentReport: null,
  currentProgress: null,
  isGenerating: false,
  generationStatus: '',
  generationError: null,
  isReportVisible: false,
  currentSection: 0,

  // Actions
  setCurrentReport: (report) => set({ currentReport: report }),

  setCurrentProgress: (progress) => set({ currentProgress: progress }),

  setGenerating: (isGenerating) => set({ isGenerating }),

  setGenerationStatus: (status) => set({ generationStatus: status }),

  setGenerationError: (error) => set({ generationError: error }),

  setReportVisible: (visible) => set({ isReportVisible: visible }),

  setCurrentSection: (section) => set({ currentSection: section }),

  resetReportState: () => set({
    currentReport: null,
    currentProgress: null,
    isGenerating: false,
    generationStatus: '',
    generationError: null,
    isReportVisible: false,
    currentSection: 0,
  }),
}));
