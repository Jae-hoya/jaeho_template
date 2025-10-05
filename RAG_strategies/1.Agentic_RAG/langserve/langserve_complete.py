"""
완전한 Agentic RAG LangServe 서버
실제 RAG 모듈들을 사용하여 LangServe로 API를 노출합니다.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from langserve import add_routes
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from datetime import datetime
import json
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path
from langchain_core.runnables import Runnable
from langchain_core.runnables.utils import Input, Output

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

# RAG 모듈들 import
try:
    from rag import rag, chat_history_rag
    from retriever import FAISSRetrieverFactory
    from chain import create_agentic_rag_graph, create_agentic_rag_graph_no_memory
    from langchain_openai import ChatOpenAI
except ImportError as e:
    print(f"RAG 모듈 import 오류: {e}")
    print("기본 모드로 실행합니다.")

# get_retriever 함수 정의
def get_retriever():
    """FAISS retriever를 생성합니다."""
    try:
        faiss_factory = FAISSRetrieverFactory()
        retriever = faiss_factory.retriever(
            index_path="../LANGCHAIN_FAISS_DB_INDEX",
            fetch_k=3
        )
        return retriever
    except Exception as e:
        print(f"Retriever 생성 오류: {e}")
        return None

# FastAPI 앱 생성
app = FastAPI(
    title="Agentic RAG LangServe API", 
    version="1.0.0",
    description="LangServe를 사용한 Agentic RAG 시스템"
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
    used_tools: Optional[List[str]] = None
    timestamp: Optional[str] = None

class BatchConversationData(BaseModel):
    conversations: List[ConversationData]
    batch_timestamp: Optional[str] = None

class SessionSummaryData(BaseModel):
    thread_id: str
    total_questions: int
    session_duration: int
    conversation_count: int
    remaining_conversations: Optional[List[ConversationData]] = None
    timestamp: Optional[str] = None

# LangServe용 입력/출력 모델들
class SimpleRAGInput(BaseModel):
    question: str

class SimpleRAGOutput(BaseModel):
    answer: str

class ChatHistoryRAGInput(BaseModel):
    question: str
    chat_history: List[List[str]] = []

class ChatHistoryRAGOutput(BaseModel):
    answer: str
    chat_history: List[List[str]]

class AgenticRAGInput(BaseModel):
    question: str
    thread_id: str = "default_thread"  # Optional 대신 기본값 사용

class AgenticRAGOutput(BaseModel):
    answer: str
    thread_id: str
    used_agents: List[str]
    timestamp: str

# 데이터 저장소
feedback_storage = []
conversation_storage = []
executor = ThreadPoolExecutor(max_workers=10)

# RAG 체인들을 저장할 전역 변수
rag_chains = {}

def initialize_rag_chains():
    """RAG 체인들을 초기화합니다."""
    global rag_chains
    
    try:
        # Retriever 초기화
        retriever = get_retriever()
        
        # LLM 초기화
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # 1. 기본 RAG 체인
        rag_chains["simple_rag"] = rag(retriever, model=llm)
        
        # 2. 채팅 히스토리가 있는 RAG 체인
        rag_chains["chat_rag"] = chat_history_rag(retriever, model=llm)
        
        # 3. Agentic RAG 그래프 (메모리 있음)
        rag_chains["agentic_rag"] = create_agentic_rag_graph(retriever, llm, use_memory=True)
        
        # 4. Agentic RAG 그래프 (메모리 없음)
        rag_chains["agentic_rag_no_memory"] = create_agentic_rag_graph_no_memory(retriever, llm)
        
        print("RAG 체인들이 성공적으로 초기화되었습니다.")
        
    except Exception as e:
        print(f"RAG 체인 초기화 오류: {e}")
        # 기본 체인으로 대체
        rag_chains["simple_rag"] = create_fallback_chain()

def create_fallback_chain():
    """기본 체인을 생성합니다."""
    class FallbackChain(Runnable[Input, Output]):
        def invoke(self, input_data: Input, config=None) -> Output:
            return {"answer": "RAG 시스템을 초기화할 수 없습니다. 기본 응답입니다."}
        
        async def ainvoke(self, input_data: Input, config=None) -> Output:
            return self.invoke(input_data, config)
    
    return FallbackChain()

# RAG 체인 래퍼 클래스들
class SimpleRAGWrapper(Runnable[Input, Output]):
    def __init__(self, chain):
        self.chain = chain
    
    def invoke(self, input_data: Input, config=None) -> Output:
        # LangServe에서는 input_data가 Pydantic 모델이므로 .question 속성 사용
        if hasattr(input_data, 'question'):
            question = input_data.question
        else:
            question = input_data.get("question", "") if isinstance(input_data, dict) else ""
        
        result = self.chain.invoke({"question": question})
        return {"answer": result}
    
    async def ainvoke(self, input_data: Input, config=None) -> Output:
        # LangServe에서는 input_data가 Pydantic 모델이므로 .question 속성 사용
        if hasattr(input_data, 'question'):
            question = input_data.question
        else:
            question = input_data.get("question", "") if isinstance(input_data, dict) else ""
        
        result = await self.chain.ainvoke({"question": question})
        return {"answer": result}

class ChatHistoryRAGWrapper(Runnable[Input, Output]):
    def __init__(self, chain):
        self.chain = chain
    
    def invoke(self, input_data: Input, config=None) -> Output:
        question = input_data.get("question", "")
        chat_history = input_data.get("chat_history", [])
        
        result = self.chain.invoke({
            "question": question,
            "chat_history": chat_history
        })
        
        return {
            "answer": result,
            "chat_history": chat_history + [[question, result]]
        }
    
    async def ainvoke(self, input_data: Input, config=None) -> Output:
        question = input_data.get("question", "")
        chat_history = input_data.get("chat_history", [])
        
        result = await self.chain.ainvoke({
            "question": question,
            "chat_history": chat_history
        })
        
        return {
            "answer": result,
            "chat_history": chat_history + [[question, result]]
        }

class AgenticRAGWrapper(Runnable[Input, Output]):
    def __init__(self, graph, use_memory=True):
        self.graph = graph
        self.use_memory = use_memory
    
    def invoke(self, input_data: Input, config=None) -> Output:
        # Pydantic 모델에서 속성 접근
        if hasattr(input_data, 'question'):
            question = input_data.question
        else:
            question = input_data.get("question", "")
        
        if hasattr(input_data, 'thread_id'):
            thread_id = input_data.thread_id
        else:
            thread_id = input_data.get("thread_id", "default_thread")
        
        # 기본값이 "default_thread"인 경우 새로운 thread_id 생성
        if thread_id == "default_thread":
            thread_id = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.use_memory:
            config = {"configurable": {"thread_id": thread_id}}
            result = self.graph.invoke(
                {"messages": [("user", question)]},
                config=config
            )
        else:
            result = self.graph.invoke({"messages": [("user", question)]})
        
        # 결과에서 답변 추출
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, tuple):
                answer = last_message[1]
            else:
                answer = last_message.content if hasattr(last_message, 'content') else str(last_message)
        else:
            answer = "답변을 생성할 수 없습니다."
        
        return {
            "answer": answer,
            "thread_id": thread_id,
            "used_agents": ["Supervisor", "Retriever", "Researcher", "Coder", "General LLM"],
            "timestamp": datetime.now().isoformat()
        }
    
    async def ainvoke(self, input_data: Input, config=None) -> Output:
        return self.invoke(input_data, config)

# RAG 체인 초기화
initialize_rag_chains()

# LangServe 라우트 추가
if "simple_rag" in rag_chains:
    add_routes(
        app,
        SimpleRAGWrapper(rag_chains["simple_rag"]),
        path="/simple-rag",
        input_type=SimpleRAGInput,
        output_type=SimpleRAGOutput,
        enable_feedback_endpoint=True,
        enable_public_trace_link_endpoint=True,
        playground_type="chat",
    )

if "chat_rag" in rag_chains:
    add_routes(
        app,
        ChatHistoryRAGWrapper(rag_chains["chat_rag"]),
        path="/chat-rag",
        input_type=ChatHistoryRAGInput,
        output_type=ChatHistoryRAGOutput
    )

if "agentic_rag" in rag_chains:
    add_routes(
        app,
        AgenticRAGWrapper(rag_chains["agentic_rag"], use_memory=True),
        path="/agentic-rag",
        input_type=AgenticRAGInput,
        output_type=AgenticRAGOutput
    )

if "agentic_rag_no_memory" in rag_chains:
    add_routes(
        app,
        AgenticRAGWrapper(rag_chains["agentic_rag_no_memory"], use_memory=False),
        path="/agentic-rag-no-memory",
        input_type=AgenticRAGInput,
        output_type=AgenticRAGOutput
    )

# 기존 FastAPI 엔드포인트들
@app.get("/")
async def root():
    return {
        "message": "Agentic RAG LangServe API is running",
        "available_endpoints": [
            "/simple-rag",
            "/chat-rag", 
            "/agentic-rag",
            "/agentic-rag-no-memory",
            "/feedback",
            "/conversation"
        ],
        "playground_urls": {
            "simple_rag": "http://localhost:8002/simple-rag/playground/",
            "chat_rag": "http://localhost:8002/chat-rag/playground/",
            "agentic_rag": "http://localhost:8002/agentic-rag/playground/",
            "agentic_rag_no_memory": "http://localhost:8002/agentic-rag-no-memory/playground/"
        },
        "docs_url": "http://localhost:8002/docs"
    }

# favicon 에러 해결을 위한 엔드포인트
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon"}

@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    return {
        "status": "healthy",
        "rag_chains_initialized": list(rag_chains.keys()),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackData, background_tasks: BackgroundTasks):
    try:
        if not feedback.timestamp:
            feedback.timestamp = datetime.now().isoformat()
        
        feedback_storage.append(feedback.dict())
        background_tasks.add_task(save_feedback_to_file, feedback.dict())
        
        return {
            "status": "success",
            "message": "피드백이 성공적으로 제출되었습니다.",
            "data": feedback.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 제출 중 오류가 발생했습니다: {str(e)}")

@app.post("/conversation")
async def submit_conversation(conversation: ConversationData, background_tasks: BackgroundTasks):
    """단일 대화 내용을 저장하는 엔드포인트"""
    try:
        if not conversation.timestamp:
            conversation.timestamp = datetime.now().isoformat()
        
        conversation_storage.append(conversation.dict())
        background_tasks.add_task(save_conversation_to_file, conversation.dict())
        
        return {
            "status": "success",
            "message": "대화가 성공적으로 저장되었습니다.",
            "data": conversation.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"대화 저장 중 오류가 발생했습니다: {str(e)}")

@app.post("/conversation/thread")
async def submit_conversation_by_thread(conversation: ConversationData, background_tasks: BackgroundTasks):
    """thread_id별로 같은 파일에 대화를 저장하는 엔드포인트"""
    try:
        if not conversation.timestamp:
            conversation.timestamp = datetime.now().isoformat()
        
        conversation_storage.append(conversation.dict())
        background_tasks.add_task(save_conversation_by_thread_to_file, conversation.dict())
        
        return {
            "status": "success",
            "message": "대화가 thread_id별로 성공적으로 저장되었습니다.",
            "data": conversation.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"thread_id별 대화 저장 중 오류가 발생했습니다: {str(e)}")

@app.post("/conversation/batch")
async def submit_conversation_batch(batch_data: BatchConversationData, background_tasks: BackgroundTasks):
    """배치 대화 내용을 저장하는 엔드포인트"""
    try:
        if not batch_data.batch_timestamp:
            batch_data.batch_timestamp = datetime.now().isoformat()
        
        for conversation in batch_data.conversations:
            if not conversation.timestamp:
                conversation.timestamp = datetime.now().isoformat()
        
        background_tasks.add_task(save_conversation_batch_to_file, batch_data.dict())
        
        return {
            "status": "success",
            "message": f"{len(batch_data.conversations)}개의 대화가 성공적으로 저장되었습니다.",
            "batch_size": len(batch_data.conversations),
            "batch_timestamp": batch_data.batch_timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 대화 저장 중 오류가 발생했습니다: {str(e)}")

@app.post("/session/summary")
async def submit_session_summary(summary: SessionSummaryData, background_tasks: BackgroundTasks):
    """세션 요약을 저장하는 엔드포인트"""
    try:
        if not summary.timestamp:
            summary.timestamp = datetime.now().isoformat()
        
        background_tasks.add_task(save_session_summary_to_file, summary.dict())
        
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
        raise HTTPException(status_code=500, detail=f"세션 요약 저장 중 오류가 발생했습니다: {str(e)}")

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
    uvicorn.run(app, host="0.0.0.0", port=8002)

# 실행 명령어:
# uvicorn langserve_complete:app --reload --port 8002
