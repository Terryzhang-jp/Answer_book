#!/usr/bin/env python3
"""
Cloud Run 启动脚本
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

if __name__ == "__main__":
    # 从环境变量获取端口，默认为8080（Cloud Run标准）
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    print(f"Python version: {sys.version}")
    print(f"Starting server on {host}:{port}")
    print(f"Environment variables:")
    print(f"  PORT: {os.environ.get('PORT', 'not set')}")
    print(f"  HOST: {os.environ.get('HOST', 'not set')}")
    print(f"  DEBUG: {os.environ.get('DEBUG', 'not set')}")

    # 设置一些环境变量以确保应用正常启动
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))

    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            workers=1,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
