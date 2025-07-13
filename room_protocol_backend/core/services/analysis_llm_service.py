"""
分析专用LLM服务 - 使用gemini-2.0-flash进行对话分析
"""

import os
from typing import Optional
from langchain.chat_models.base import init_chat_model
from loguru import logger

from config.settings import get_settings


class AnalysisLLMService:
    """分析专用LLM服务类"""
    
    _analysis_model = None
    
    @classmethod
    def get_analysis_model(cls):
        """获取分析专用模型实例（单例模式）"""
        if cls._analysis_model is None:
            settings = get_settings()

            try:
                # 检查API密钥
                api_key = settings.GEMINI_API_KEY
                if not api_key:
                    logger.warning("GEMINI_API_KEY未配置，分析功能将被禁用")
                    return None

                # 设置环境变量（关键！）
                os.environ["GOOGLE_API_KEY"] = api_key

                cls._analysis_model = init_chat_model(
                    "gemini-1.5-flash",
                    model_provider="google-genai",  # 关键！指定使用Google AI API
                    temperature=0.3,  # 分析需要稳定输出
                    max_tokens=3000   # 控制分析长度
                )
                logger.info("分析模型初始化成功: gemini-1.5-flash")
            except Exception as e:
                logger.error(f"分析模型初始化失败: {e}")
                return None

        return cls._analysis_model
    
    @classmethod
    async def analyze_conversation(cls, analysis_prompt: str) -> str:
        """执行对话分析"""
        model = cls.get_analysis_model()
        if model is None:
            logger.warning("分析模型未初始化，跳过分析")
            return "分析功能暂时不可用"

        try:
            logger.info("开始执行对话分析")
            response = await model.ainvoke([{"role": "user", "content": analysis_prompt}])
            logger.info(f"分析完成，响应长度: {len(response.content)}")
            return response.content
        except Exception as e:
            logger.error(f"对话分析失败: {e}")
            return "分析执行失败"
