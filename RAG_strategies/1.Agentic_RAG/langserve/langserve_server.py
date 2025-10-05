from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from datetime import datetime
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from langchain_core.runnables import Runnable
from langchain_core.runnables.utils import Input, Output

# FastAPI 앱 생성
app = FastAPI(title="Agentic RAG LangServe API", version="1.0.0")

# CORS 미들웨어 설정
# 외부 도메인에서의 API 접근을 위한 보안 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 데이터 모델들
class FeedbackData(BaseModel):
    thread_id: str
    question_count: int
    feedback_scores: Dict[str, int]
    comment: Optional[str] = None
    timestamp: Optional[str] = None

class ConversationData(BaseModel):
    thread_id: str
    question_count: int
    user_message: str
    ai_response: str
    used_tools: List[str] = []
    timestamp: str = ""

class BatchConversationData(BaseModel):
    conversations: List[ConversationData]
    batch_timestamp: str = ""

class SessionSummaryData(BaseModel):
    thread_id: str
    total_questions: int
    session_duration: int
    conversation_count: int
    remaining_conversations: List[ConversationData] = []
    timestamp: str = ""

# 입력/출력 모델 (LangServe용) - 기본 형식
class RAGInput(BaseModel):
    query: str

class RAGOutput(BaseModel):
    response: str

# 데이터 저장소
feedback_storage = []
conversation_storage = []
executor = ThreadPoolExecutor(max_workers=10)

# 간단한 RAG 체인 예시 (실제 구현에서는 기존 RAG 모듈을 import)
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.base import Runnable

class SimpleRAGChain(Runnable):
    """기본 RAG 체인"""
    
    def invoke(self, input_data, config=None):
        """기본 메시지 처리"""
        if isinstance(input_data, dict) and "query" in input_data:
            query = input_data["query"]
        else:
            query = str(input_data)
        
        response = f"질문: {query}\n\n답변: 이것은 RAG 시스템의 예시 응답입니다. 실제로는 벡터 검색과 LLM을 통한 답변 생성이 이루어집니다."
        
        return {"response": response}
    
    async def ainvoke(self, input_data, config=None):
        """비동기 버전"""
        return self.invoke(input_data, config)

# 체인 생성
rag_chain = SimpleRAGChain()

# with_types 메서드로 명시적 타입 지정
typed_chain = rag_chain.with_types(
    input_type=RAGInput,
    output_type=RAGOutput
)

# LangServe 라우트 추가
add_routes(
    app,
    typed_chain,
    path="/rag",
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True,
    playground_type="chat",
)

# 기존 FastAPI 엔드포인트들
@app.get("/")
async def root():
    return {
        "message": "Agentic RAG LangServe API is running",
        "playground_url": "http://localhost:8001/rag/playground/",
        "docs_url": "http://localhost:8001/docs",
        "endpoints": {
            "rag_invoke": "http://localhost:8001/rag/invoke",
            "rag_stream": "http://localhost:8001/rag/stream",
            "rag_batch": "http://localhost:8001/rag/batch"
        }
    }

# 플레이그라운드로 리다이렉션
@app.get("/playground")
async def redirect_to_playground():
    return RedirectResponse("/rag/playground/")

# favicon 에러 해결을 위한 엔드포인트
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon"}

# 플레이그라운드 테스트용 엔드포인트
@app.get("/rag/info")
async def rag_info():
    return {
        "status": "RAG endpoint is working",
        "input_type": "RAGInput",
        "output_type": "RAGOutput",
        "playground_url": "/rag/playground/"
    }

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackData):
    try:
        if not feedback.timestamp:
            feedback.timestamp = datetime.now().isoformat()
        
        feedback_storage.append(feedback.dict())
        await save_feedback_to_file(feedback.dict())
        
        return {
            "status": "success",
            "message": "피드백이 성공적으로 제출되었습니다.",
            "data": feedback.dict()
        }
    except Exception as e:
        return {"status": "error", "detail": f"피드백 제출 중 오류가 발생했습니다: {str(e)}"}

@app.post("/conversation")
async def submit_conversation(conversation: ConversationData):
    """단일 대화 내용을 저장하는 엔드포인트"""
    try:
        if not conversation.timestamp:
            conversation.timestamp = datetime.now().isoformat()
        
        conversation_storage.append(conversation.dict())
        await save_conversation_to_file(conversation.dict())
        
        return {
            "status": "success",
            "message": "대화가 성공적으로 저장되었습니다.",
            "data": conversation.dict()
        }
    except Exception as e:
        return {"status": "error", "detail": f"대화 저장 중 오류가 발생했습니다: {str(e)}"}

@app.post("/conversation/thread")
async def submit_conversation_by_thread(conversation: ConversationData):
    """thread_id별로 같은 파일에 대화를 저장하는 엔드포인트"""
    try:
        if not conversation.timestamp:
            conversation.timestamp = datetime.now().isoformat()
        
        conversation_storage.append(conversation.dict())
        await save_conversation_by_thread_to_file(conversation.dict())
        
        return {
            "status": "success",
            "message": "대화가 thread_id별로 성공적으로 저장되었습니다.",
            "data": conversation.dict()
        }
    except Exception as e:
        return {"status": "error", "detail": f"thread_id별 대화 저장 중 오류가 발생했습니다: {str(e)}"}

@app.post("/conversation/batch")
async def submit_conversation_batch(batch_data: BatchConversationData):
    """배치 대화 내용을 저장하는 엔드포인트"""
    try:
        if not batch_data.batch_timestamp:
            batch_data.batch_timestamp = datetime.now().isoformat()
        
        for conversation in batch_data.conversations:
            if not conversation.timestamp:
                conversation.timestamp = datetime.now().isoformat()
        
        await save_conversation_batch_to_file(batch_data.dict())
        
        return {
            "status": "success",
            "message": f"{len(batch_data.conversations)}개의 대화가 성공적으로 저장되었습니다.",
            "batch_size": len(batch_data.conversations),
            "batch_timestamp": batch_data.batch_timestamp
        }
    except Exception as e:
        return {"status": "error", "detail": f"배치 대화 저장 중 오류가 발생했습니다: {str(e)}"}

@app.post("/session/summary")
async def submit_session_summary(summary: SessionSummaryData):
    """세션 요약을 저장하는 엔드포인트"""
    try:
        if not summary.timestamp:
            summary.timestamp = datetime.now().isoformat()
        
        await save_session_summary_to_file(summary.dict())
        
        return {
            "status": "success",
            "message": "세션 요약이 성공적으로 저장되었습니다.",
            "data": {
                "thread_id": summary.thread_id,
                "total_questions": summary.total_questions,
                "session_duration": summary.session_duration,
                "conversation_count": summary.conversation_count
            }
        }
    except Exception as e:
        return {"status": "error", "detail": f"세션 요약 저장 중 오류가 발생했습니다: {str(e)}"}

@app.get("/feedback")
async def get_feedback():
    """모든 피드백 데이터 조회"""
    return {
        "status": "success",
        "count": len(feedback_storage),
        "data": feedback_storage
    }

@app.get("/conversation")
async def get_conversations():
    """모든 대화 데이터 조회"""
    return {
        "status": "success",
        "count": len(conversation_storage),
        "data": conversation_storage
    }

@app.get("/feedback/{thread_id}")
async def get_feedback_by_thread(thread_id: str):
    """특정 스레드의 피드백 데이터 조회"""
    thread_feedback = [f for f in feedback_storage if f["thread_id"] == thread_id]
    return {
        "status": "success",
        "thread_id": thread_id,
        "count": len(thread_feedback),
        "data": thread_feedback
    }

@app.get("/conversation/{thread_id}")
async def get_conversation_by_thread(thread_id: str):
    """특정 스레드의 대화 데이터 조회"""
    thread_conversations = [c for c in conversation_storage if c["thread_id"] == thread_id]
    return {
        "status": "success",
        "thread_id": thread_id,
        "count": len(thread_conversations),
        "data": thread_conversations
    }

# 비동기 파일 저장 함수들
async def save_feedback_to_file(feedback_data: Dict[str, Any]):
    """비동기로 피드백 데이터를 JSON 파일로 저장"""
    feedback_dir = "feedback_data"
    if not os.path.exists(feedback_dir):
        os.makedirs(feedback_dir)
    
    filename = f"{feedback_dir}/feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, save_json_file, filename, feedback_data)

async def save_conversation_to_file(conversation_data: Dict[str, Any]):
    """비동기로 대화 데이터를 JSON 파일로 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    filename = f"{conversation_dir}/conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, save_json_file, filename, conversation_data)

async def save_conversation_by_thread_to_file(conversation_data: Dict[str, Any]):
    """비동기로 thread_id별로 같은 파일에 대화 데이터를 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    thread_id = conversation_data["thread_id"]
    thread_short = thread_id[:8]
    
    existing_files = [f for f in os.listdir(conversation_dir) if f.startswith(f"thread_{thread_short}_")]
    
    if existing_files:
        filename = f"{conversation_dir}/{existing_files[0]}"
    else:
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{conversation_dir}/thread_{thread_short}_{current_time}.json"
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, save_conversation_by_thread_sync, filename, conversation_data)

async def save_conversation_batch_to_file(batch_data: Dict[str, Any]):
    """비동기로 배치 대화 데이터를 JSON 파일로 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    filename = f"{conversation_dir}/batch_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, save_json_file, filename, batch_data)

async def save_session_summary_to_file(summary_data: Dict[str, Any]):
    """비동기로 세션 요약 데이터를 JSON 파일로 저장"""
    conversation_dir = "conversation_data"
    if not os.path.exists(conversation_dir):
        os.makedirs(conversation_dir)
    
    filename = f"{conversation_dir}/session_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, save_json_file, filename, summary_data)

# 동기 파일 저장 헬퍼 함수들
def save_json_file(filename: str, data: Dict[str, Any]):
    """JSON 파일 저장 헬퍼 함수"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_conversation_by_thread_sync(filename: str, conversation_data: Dict[str, Any]):
    """thread_id별로 같은 파일에 대화 데이터를 동기적으로 저장"""
    existing_conversations = []
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if isinstance(existing_data, dict) and "conversations" in existing_data:
                    existing_conversations = existing_data["conversations"]
                elif isinstance(existing_data, list):
                    existing_conversations = existing_data
        except Exception as e:
            print(f"기존 파일 읽기 오류: {e}")
            existing_conversations = []
    
    existing_conversations.append(conversation_data)
    
    thread_data = {
        "thread_id": conversation_data["thread_id"],
        "conversations": existing_conversations,
        "last_updated": datetime.now().isoformat()
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(thread_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

# 실행 명령어:
# uvicorn langserve_server:app --reload --port 8001

# http://localhost:8001/rag/playground/