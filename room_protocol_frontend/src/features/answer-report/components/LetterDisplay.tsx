/**
 * 信件显示组件
 */

import React from 'react';
import { Mail, Download, Share2 } from 'lucide-react';

interface LetterDisplayProps {
  letterContent: string;
  threadId: string;
  userId: string;
}

export default function LetterDisplay({ letterContent, threadId, userId }: LetterDisplayProps) {
  const handleDownload = () => {
    const blob = new Blob([letterContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `答案之书的信件_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: '来自答案之书的一封信',
          text: letterContent,
        });
      } catch (error) {
        console.log('分享失败:', error);
        // 降级到复制到剪贴板
        handleCopy();
      }
    } else {
      // 降级到复制到剪贴板
      handleCopy();
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(letterContent);
      alert('信件内容已复制到剪贴板');
    } catch (error) {
      console.error('复制失败:', error);
      alert('复制失败，请手动选择文本复制');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <Mail className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">来自答案之书的一封信</h1>
            <p className="text-sm text-gray-600">为您量身定制的人生指引</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleDownload}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>下载</span>
          </button>
          
          <button
            onClick={handleShare}
            className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            <Share2 className="w-4 h-4" />
            <span>分享</span>
          </button>
        </div>
      </div>

      {/* Letter Content */}
      <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-8 shadow-lg">
        <div className="bg-white rounded-lg p-8 shadow-inner">
          <div 
            className="prose prose-lg max-w-none text-gray-800 leading-relaxed"
            style={{
              fontFamily: "'Noto Serif SC', 'Times New Roman', serif",
              lineHeight: '1.8'
            }}
          >
            {letterContent.split('\n').map((line, index) => {
              // 处理不同类型的行
              if (line.trim() === '') {
                return <br key={index} />;
              }
              
              // 标题行
              if (line.includes('来自答案之书的一封信')) {
                return (
                  <h2 key={index} className="text-2xl font-bold text-center mb-6 text-gray-900">
                    {line.trim()}
                  </h2>
                );
              }
              
              // 称呼行
              if (line.includes('亲爱的') && line.includes('：')) {
                return (
                  <p key={index} className="text-lg font-medium mb-4 text-gray-900">
                    {line.trim()}
                  </p>
                );
              }
              
              // 落款相关行
              if (line.includes('此致') || line.includes('敬礼') || line.includes('答案之书') || /^\d{4}年\d{1,2}月\d{1,2}日$/.test(line.trim())) {
                return (
                  <p key={index} className="text-right mt-6 text-gray-700 font-medium">
                    {line.trim()}
                  </p>
                );
              }
              
              // 普通段落
              return (
                <p key={index} className="mb-4 text-gray-800 text-justify">
                  {line.trim()}
                </p>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>这封信是基于您的对话内容和未来想象生成的个性化指引</p>
        <p className="mt-1">愿它能为您的人生旅程带来启发和力量</p>
      </div>
    </div>
  );
}
