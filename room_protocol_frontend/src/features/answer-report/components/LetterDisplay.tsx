/**
 * Letter display component
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
    link.download = `Answer_Book_Letter_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'A Letter from the Answer Book',
          text: letterContent,
        });
      } catch (error) {
        console.log('Share failed:', error);
        // Fallback to copy to clipboard
        handleCopy();
      }
    } else {
      // Fallback to copy to clipboard
      handleCopy();
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(letterContent);
      alert('Letter content copied to clipboard');
    } catch (error) {
      console.error('Copy failed:', error);
      alert('Copy failed, please manually select and copy the text');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <Mail className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">A Letter from the Answer Book</h1>
            <p className="text-sm text-gray-600">Personalized life guidance tailored for you</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleDownload}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            <span>Download</span>
          </button>

          <button
            onClick={handleShare}
            className="flex items-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
          >
            <Share2 className="w-4 h-4" />
            <span>Share</span>
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
              // Handle different types of lines
              if (line.trim() === '') {
                return <br key={index} />;
              }

              // Title line
              if (line.includes('来自答案之书的一封信') || line.toLowerCase().includes('letter from the answer book')) {
                return (
                  <h2 key={index} className="text-2xl font-bold text-center mb-6 text-gray-900">
                    {line.trim()}
                  </h2>
                );
              }

              // Greeting line
              if ((line.includes('亲爱的') && line.includes('：')) || (line.toLowerCase().includes('dear') && line.includes(':'))) {
                return (
                  <p key={index} className="text-lg font-medium mb-4 text-gray-900">
                    {line.trim()}
                  </p>
                );
              }

              // Closing lines
              if (line.includes('此致') || line.includes('敬礼') || line.includes('答案之书') ||
                  line.toLowerCase().includes('sincerely') || line.toLowerCase().includes('the answer book') ||
                  /^\d{4}年\d{1,2}月\d{1,2}日$/.test(line.trim()) || /^\d{4}-\d{2}-\d{2}$/.test(line.trim())) {
                return (
                  <p key={index} className="text-right mt-6 text-gray-700 font-medium">
                    {line.trim()}
                  </p>
                );
              }

              // Regular paragraph
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
        <p>This letter is personalized guidance generated based on your conversation and future imagination</p>
        <p className="mt-1">May it bring inspiration and strength to your life journey</p>
      </div>
    </div>
  );
}
