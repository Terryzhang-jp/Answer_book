'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Download, Share2, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface ReportData {
  id?: string;
  title?: string;
  content?: string;
  letter_content?: string;
  created_at?: string;
  generated_at?: string;
  thread_id?: string;
  user_id?: string;
}

export default function ReportPage() {
  const params = useParams();
  const router = useRouter();
  const threadId = params.threadId as string;
  
  const [report, setReport] = useState<ReportData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (threadId) {
      fetchReport();
    }
  }, [threadId]);

  const fetchReport = async () => {
    try {
      setIsLoading(true);
      setError(null);

      console.log('正在获取报告，threadId:', threadId);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/report/thread/${threadId}`);
      
      console.log('API响应状态:', response.status);
      
      if (!response.ok) {
        throw new Error(`获取报告失败: ${response.status}`);
      }

      const data = await response.json();
      console.log('API响应数据:', data);
      
      if (!data.success) {
        throw new Error(data.message || '获取报告失败');
      }

      console.log('设置报告数据:', data.report);
      console.log('报告数据类型:', typeof data.report);
      console.log('报告数据结构:', JSON.stringify(data.report, null, 2));
      setReport(data.report);
    } catch (error) {
      console.error('获取报告失败:', error);
      setError(error instanceof Error ? error.message : '获取报告失败');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    router.push(`/chat`);
  };

  const handleDownload = () => {
    if (!report) {
      console.log('没有报告数据可下载');
      return;
    }
    
    console.log('下载报告数据:', report);
    
    // 检查报告内容字段
    let content = '';
    if (typeof report === 'string') {
      content = report;
    } else if (typeof report === 'object' && report.letter_content) {
      // letter_content 可能是嵌套对象
      if (typeof report.letter_content === 'object' && report.letter_content.letter_content) {
        content = report.letter_content.letter_content;
      } else if (typeof report.letter_content === 'string') {
        content = report.letter_content;
      } else {
        content = JSON.stringify(report.letter_content, null, 2);
      }
    } else {
      content = JSON.stringify(report, null, 2);
    }
    const title = report.title || report.id || `答案之书-${new Date().toLocaleDateString()}`;
    
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/plain; charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = `答案之书-${title}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleShare = async () => {
    if (!report) {
      console.log('没有报告数据可分享');
      return;
    }
    
    let content = '';
    if (typeof report === 'string') {
      content = report;
    } else if (typeof report === 'object' && report.letter_content) {
      // letter_content 可能是嵌套对象
      if (typeof report.letter_content === 'object' && report.letter_content.letter_content) {
        content = report.letter_content.letter_content;
      } else if (typeof report.letter_content === 'string') {
        content = report.letter_content;
      }
    }
    const title = report.title || '答案之书';
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `答案之书 - ${title}`,
          text: content,
        });
      } catch (error) {
        console.log('分享取消或失败');
      }
    } else {
      // 复制到剪贴板
      try {
        await navigator.clipboard.writeText(content);
        alert('内容已复制到剪贴板');
      } catch (error) {
        console.error('复制失败:', error);
        alert('复制失败，请手动复制内容');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-amber-600 mx-auto mb-4" />
          <p className="text-lg text-gray-700">正在加载您的答案之书...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">😔</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">加载失败</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={handleBack}
            className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            返回对话
          </button>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-red-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">📖</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">暂无报告</h2>
          <p className="text-gray-600 mb-4">该对话还没有生成答案之书</p>
          <button
            onClick={handleBack}
            className="px-6 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
          >
            返回对话
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-yellow-50 to-orange-50 relative">
      {/* 背景装饰 */}
      <div className="absolute inset-0 opacity-5">
        <div className="absolute top-20 left-20 w-32 h-32 bg-amber-300 rounded-full blur-3xl"></div>
        <div className="absolute top-40 right-32 w-24 h-24 bg-orange-300 rounded-full blur-2xl"></div>
        <div className="absolute bottom-32 left-1/3 w-40 h-40 bg-yellow-300 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-28 h-28 bg-amber-400 rounded-full blur-2xl"></div>
      </div>
      {/* 顶部导航 */}
      <div className="bg-amber-50/90 backdrop-blur-sm border-b border-amber-200/50 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <button
            onClick={handleBack}
            className="flex items-center space-x-2 text-amber-700 hover:text-amber-900 transition-colors font-serif"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>返回对话</span>
          </button>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleShare}
              className="flex items-center space-x-2 px-4 py-2 text-amber-700 hover:text-amber-900 border border-amber-300 rounded-lg transition-colors font-serif bg-white/50"
            >
              <Share2 className="w-4 h-4" />
              <span>分享信件</span>
            </button>
            
            <button
              onClick={handleDownload}
              className="flex items-center space-x-2 px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg transition-colors font-serif shadow-sm"
            >
              <Download className="w-4 h-4" />
              <span>保存信件</span>
            </button>
          </div>
        </div>
      </div>

      {/* 信件内容 */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="relative"
        >
          {/* 信纸背景 */}
          <div className="relative bg-gradient-to-b from-amber-50 to-yellow-50 shadow-2xl" 
               style={{
                 backgroundImage: `
                   linear-gradient(90deg, transparent 0%, transparent calc(100% - 1px), #e5e7eb calc(100% - 1px)),
                   linear-gradient(180deg, transparent 0%, transparent 35px, #d97706 35px, #d97706 36px, transparent 36px)
                 `,
                 backgroundSize: '100% 36px'
               }}>
            
            {/* 信纸的装订孔 */}
            <div className="absolute left-8 top-0 bottom-0 w-px bg-red-300 opacity-60"></div>
            <div className="absolute left-6 top-12 w-2 h-2 bg-gray-300 rounded-full"></div>
            <div className="absolute left-6 top-24 w-2 h-2 bg-gray-300 rounded-full"></div>
            <div className="absolute left-6 top-36 w-2 h-2 bg-gray-300 rounded-full"></div>
            
            {/* 信件头部 - 模拟信纸抬头 */}
            <div className="px-16" style={{ paddingTop: '72px', paddingBottom: '36px' }}>
              <div className="text-center" style={{ marginBottom: '72px' }}>
                <div className="inline-block">
                  <div className="text-6xl opacity-80" style={{ lineHeight: '72px', marginBottom: '0' }}>✉️</div>
                  <h1 className="text-4xl font-serif text-amber-800 tracking-wide" 
                      style={{ lineHeight: '72px', marginBottom: '0' }}>
                    答案之书
                  </h1>
                  <div className="w-32 h-px bg-amber-600 mx-auto" style={{ margin: '18px auto' }}></div>
                  <p className="text-amber-700 text-lg font-serif italic"
                     style={{ lineHeight: '36px', marginBottom: '0' }}>
                    来自智慧的私人信件
                  </p>
                  
                  {/* 日期 - 右上角 */}
                  {(() => {
                    let timestamp = report?.created_at || report?.generated_at;
                    if (!timestamp && report?.letter_content && typeof report.letter_content === 'object') {
                      timestamp = report.letter_content.generated_at;
                    }
                    
                    if (timestamp && typeof timestamp === 'string') {
                      try {
                        const date = new Date(timestamp);
                        return (
                          <div className="absolute right-16 text-right" style={{ top: '72px' }}>
                            <p className="text-amber-700 text-sm font-serif"
                               style={{ lineHeight: '36px', marginBottom: '0' }}>
                              {date.getFullYear()}年{date.getMonth() + 1}月{date.getDate()}日
                            </p>
                            <p className="text-amber-600 text-xs font-serif"
                               style={{ lineHeight: '36px', marginTop: '0' }}>
                              {date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                        );
                      } catch (error) {
                        return null;
                      }
                    }
                    return null;
                  })()}
                </div>
              </div>

              {/* 信件正文 */}
              <div className="max-w-3xl mx-auto">
                <div className="text-gray-800 font-serif text-lg" 
                     style={{ 
                       fontFamily: '"Noto Serif SC", "Source Han Serif SC", serif',
                       lineHeight: '36px',
                       fontSize: '16px', // 稍微调小字体，更好对齐
                       textIndent: '2em',
                       paddingTop: '0' // 移除之前的paddingTop
                     }}>
                  {(() => {
                    if (!report) {
                      return (
                        <div className="text-center py-12 text-amber-600">
                          <div className="animate-pulse">信件正在书写中...</div>
                        </div>
                      );
                    }
                    
                    let content = '';
                    if (typeof report === 'string') {
                      content = report;
                    } else if (typeof report === 'object' && report.letter_content) {
                      if (typeof report.letter_content === 'object' && report.letter_content.letter_content) {
                        content = report.letter_content.letter_content;
                      } else if (typeof report.letter_content === 'string') {
                        content = report.letter_content;
                      }
                    }
                    
                    if (!content) {
                      return '暂无信件内容';
                    }
                    
                    // 处理段落，让每段都有首行缩进，并与横线对齐
                    return content.split('\n').map((paragraph, index) => {
                      if (paragraph.trim() === '') {
                        return <div key={index} style={{ height: '36px' }} />; // 空行也要占据一行的高度
                      }
                      return (
                        <div key={index} 
                             style={{ 
                               lineHeight: '36px',
                               minHeight: '36px',
                               marginBottom: '0',
                               textIndent: '2em',
                               display: 'block',
                               verticalAlign: 'baseline'
                             }}>
                          {paragraph}
                        </div>
                      );
                    });
                  })()}
                </div>
              </div>

              {/* 信件落款 */}
              <div className="text-right max-w-3xl mx-auto" style={{ marginTop: '72px' }}>
                <div className="inline-block text-amber-800 font-serif">
                  <p className="text-lg" style={{ lineHeight: '36px', marginBottom: '0' }}>此致</p>
                  <p className="text-lg" style={{ lineHeight: '36px', marginBottom: '36px' }}>敬礼</p>
                  <div className="text-right">
                    <p className="text-xl font-semibold" style={{ lineHeight: '36px', marginBottom: '8px' }}>答案之书</p>
                    <div className="w-24 h-px bg-amber-600 ml-auto mb-2"></div>
                    <p className="text-sm text-amber-600"
                       style={{ lineHeight: '36px', marginBottom: '0' }}>
                      {(() => {
                        let timestamp = report?.created_at || report?.generated_at;
                        if (!timestamp && report?.letter_content && typeof report.letter_content === 'object') {
                          timestamp = report.letter_content.generated_at;
                        }
                        
                        if (timestamp && typeof timestamp === 'string') {
                          try {
                            const date = new Date(timestamp);
                            return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
                          } catch (error) {
                            return '';
                          }
                        }
                        return '';
                      })()}
                    </p>
                  </div>
                </div>
              </div>

              {/* 信件底部装饰 */}
              <div className="text-center" style={{ marginTop: '72px' }}>
                <div className="inline-flex items-center space-x-2 text-amber-600 opacity-60"
                     style={{ height: '36px', alignItems: 'center' }}>
                  <div className="w-8 h-px bg-amber-400"></div>
                  <span className="text-2xl">✨</span>
                  <div className="w-8 h-px bg-amber-400"></div>
                </div>
                <p className="text-amber-600 text-sm font-serif italic"
                   style={{ lineHeight: '36px', marginTop: '36px', marginBottom: '0' }}>
                  "智慧如灯，照亮前路"
                </p>
              </div>
            </div>

            {/* 信纸边缘效果 */}
            <div className="absolute inset-0 pointer-events-none">
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-amber-200 to-transparent"></div>
              <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-amber-200 to-transparent"></div>
              <div className="absolute top-0 bottom-0 left-0 w-px bg-gradient-to-b from-transparent via-amber-200 to-transparent"></div>
              <div className="absolute top-0 bottom-0 right-0 w-px bg-gradient-to-b from-transparent via-amber-200 to-transparent"></div>
            </div>

            {/* 纸张阴影效果 */}
            <div className="absolute -bottom-2 -right-2 w-full h-full bg-amber-100 opacity-30 -z-10 rounded-sm"></div>
            <div className="absolute -bottom-4 -right-4 w-full h-full bg-amber-200 opacity-20 -z-20 rounded-sm"></div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}