'use client';

import BookOfAnswers from '@/components/BookOfAnswers';
import { useState } from 'react';

// 测试数据
const mockTurns = [
  {
    id: 1,
    userQuestion: "人生的意义是什么？",
    expertResponses: [
      {
        id: 1,
        name: "苏格拉底",
        bodyLanguage: "轻抚胡须，眼神深邃地凝视远方",
        thinking: "这个问题触及了哲学的核心。我必须引导他们通过自己的思考来发现答案，而不是直接给出答案。",
        speaking: "我的朋友，你问的是一个古老而永恒的问题。但让我反问你：你认为什么样的生活才是值得过的生活？是追求快乐，还是追求智慧？或者，也许答案就在你提出这个问题的过程中？",
        color: "blue"
      },
      {
        id: 2,
        name: "孔子",
        bodyLanguage: "端坐正襟，双手合于膝上，神情庄重",
        thinking: "人生之意义，在于修身齐家治国平天下。但首先要让他明白，意义来自于我们对他人和社会的贡献。",
        speaking: "人生的意义在于'仁'。当我们能够爱人如己，当我们能够'己所不欲，勿施于人'，当我们能够在家庭中尽孝，在社会中尽责，这便是有意义的人生。意义不在于索取，而在于给予。",
        color: "amber"
      }
    ]
  },
  {
    id: 2,
    userQuestion: "如何面对人生的困难和挫折？",
    expertResponses: [
      {
        id: 3,
        name: "尼采",
        bodyLanguage: "激动地站起身来，眼中闪烁着火焰般的光芒",
        thinking: "困难和痛苦不是要被避免的，而是要被拥抱的！它们是使人变得更强大的必要条件。",
        speaking: "我告诉你一个秘密：'凡不能毁灭我的，必使我更强大！'困难不是你的敌人，而是你的老师。每一次挫折都是超越自我的机会。不要寻求舒适的生活，而要寻求有意义的斗争！",
        color: "red"
      }
    ]
  }
];

export default function TestBookPage() {
  const [turns, setTurns] = useState(mockTurns);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = (question: string) => {
    setIsLoading(true);
    
    // 模拟API调用
    setTimeout(() => {
      const newTurn = {
        id: turns.length + 1,
        userQuestion: question,
        expertResponses: [
          {
            id: Date.now(),
            name: "爱因斯坦",
            bodyLanguage: "沉思地摸着头发，眼神专注而温和",
            thinking: "这是一个很好的问题。我需要用简单的语言来解释复杂的概念。",
            speaking: "想象力比知识更重要。知识是有限的，而想象力拥抱整个世界，刺激着进步，孕育着进化。保持好奇心，永远不要停止提问。",
            color: "green"
          }
        ]
      };
      
      setTurns(prev => [...prev, newTurn]);
      setIsLoading(false);
    }, 2000);
  };

  return (
    <BookOfAnswers
      turns={turns}
      onSendMessage={handleSendMessage}
      isLoading={isLoading}
      conversationAnalysis={null}
      threadId="test-thread-123"
      userId="test-user-123"
    />
  );
}