#!/usr/bin/env python3
"""
Agentic RAG FastAPI 서버 실행 스크립트
"""

import uvicorn
from fastapi_server import app

if __name__ == "__main__":
    print("🚀 Agentic RAG FastAPI 서버를 시작합니다...")
    print("📡 서버 주소: http://localhost:8000")
    print("📚 API 문서: http://localhost:8000/docs")
    print("🔄 서버를 중지하려면 Ctrl+C를 누르세요")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,  # 개발 모드에서 자동 재시작
        log_level="info"
    )

