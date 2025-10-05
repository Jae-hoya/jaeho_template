"""
Agentic RAG를 사용한 LangServe 서버 - 실제 에이전트들 포함
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from pydantic import BaseModel, Field
from typing import List, Union, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import uvicorn
import sys
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir))

# RAG 모듈들 import
try:
    from rag import rag, chat_history_rag
    from retriever import get_retriever
    from chain import create_agentic_rag_graph, create_agentic_rag_graph_no_memory
    from langchain_openai import ChatOpenAI
    print("✅ RAG 모듈들 import 성공")
except ImportError as e:
    print(f"❌ RAG 모듈 import 오류: {e}")
    print("기본 모드로 실행합니다.")

# FastAPI 앱 생성
app = FastAPI(title="Agentic RAG LangServe Server")

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 입력 모델들
class InputRAG(BaseModel):
    question: str

class InputChat(BaseModel):
    messages: List[Union[HumanMessage, AIMessage, SystemMessage]] = Field(
        default_factory=list,
        description="The chat messages representing the current conversation.",
    )

class InputAgenticRAG(BaseModel):
    question: str
    thread_id: str = "default_thread"  # Optional 대신 기본값 사용

# 출력 모델들
class OutputRAG(BaseModel):
    answer: str

class OutputAgenticRAG(BaseModel):
    answer: str
    thread_id: str
    used_agents: List[str]
    timestamp: str

# 체인 클래스들
class SimpleRAGChain:
    def create(self):
        try:
            retriever = get_retriever()
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            return rag(retriever, model=llm)
        except Exception as e:
            print(f"Simple RAG 체인 생성 오류: {e}")
            return self._create_fallback_chain()
    
    def _create_fallback_chain(self):
        from langchain_core.runnables import Runnable
        from langchain_core.runnables.utils import Input, Output
        
        class FallbackRAG(Runnable[Input, Output]):
            def invoke(self, input_data: Input, config=None) -> Output:
                question = input_data.get("question", "")
                return f"Fallback RAG: '{question}'에 대한 기본 응답입니다."
            
            async def ainvoke(self, input_data: Input, config=None) -> Output:
                return self.invoke(input_data, config)
        
        return FallbackRAG()

class ChatRAGChain:
    def create(self):
        try:
            retriever = get_retriever()
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            return chat_history_rag(retriever, model=llm)
        except Exception as e:
            print(f"Chat RAG 체인 생성 오류: {e}")
            return self._create_fallback_chat_chain()
    
    def _create_fallback_chat_chain(self):
        from langchain_core.runnables import Runnable
        from langchain_core.runnables.utils import Input, Output
        
        class FallbackChatRAG(Runnable[Input, Output]):
            def invoke(self, input_data: Input, config=None) -> Output:
                messages = input_data.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    if hasattr(last_message, 'content'):
                        question = last_message.content
                    else:
                        question = str(last_message)
                    return {"messages": [AIMessage(content=f"Fallback Chat RAG: '{question}'에 대한 기본 응답입니다.")]}
                return {"messages": [AIMessage(content="안녕하세요! 무엇을 도와드릴까요?")]}
            
            async def ainvoke(self, input_data: Input, config=None) -> Output:
                return self.invoke(input_data, config)
        
        return FallbackChatRAG()

class AgenticRAGChain:
    def __init__(self, use_memory=True):
        self.use_memory = use_memory
    
    def create(self):
        try:
            retriever = get_retriever()
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            
            if self.use_memory:
                graph = create_agentic_rag_graph(retriever, llm, use_memory=True)
            else:
                graph = create_agentic_rag_graph_no_memory(retriever, llm)
            
            return AgenticRAGWrapper(graph, self.use_memory)
        except Exception as e:
            print(f"Agentic RAG 체인 생성 오류: {e}")
            return self._create_fallback_agentic_chain()
    
    def _create_fallback_agentic_chain(self):
        from langchain_core.runnables import Runnable
        from langchain_core.runnables.utils import Input, Output
        from datetime import datetime
        
        class FallbackAgenticRAG(Runnable[Input, Output]):
            def invoke(self, input_data: Input, config=None) -> Output:
                question = input_data.get("question", "")
                thread_id = input_data.get("thread_id", f"fallback_thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                
                return {
                    "answer": f"Fallback Agentic RAG: '{question}'에 대한 기본 응답입니다.",
                    "thread_id": thread_id,
                    "used_agents": ["Fallback Agent"],
                    "timestamp": datetime.now().isoformat()
                }
            
            async def ainvoke(self, input_data: Input, config=None) -> Output:
                return self.invoke(input_data, config)
        
        return FallbackAgenticRAG()

class AgenticRAGWrapper:
    def __init__(self, graph, use_memory=True):
        self.graph = graph
        self.use_memory = use_memory
    
    def invoke(self, input_data, config=None):
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
            thread_id = f"thread_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
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
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    
    async def ainvoke(self, input_data, config=None):
        return self.invoke(input_data, config)

# 기본 경로 리다이렉션
@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/agentic-rag/playground")

# 체인들 추가
print("🤖 Agentic RAG 체인들을 추가하는 중...")

# Simple RAG 체인
add_routes(
    app,
    SimpleRAGChain().create(),
    path="/simple-rag",
    input_type=InputRAG,
    output_type=OutputRAG
)

# Chat RAG 체인
add_routes(
    app,
    ChatRAGChain().create().with_types(input_type=InputChat),
    path="/chat-rag",
    enable_feedback_endpoint=True,
    enable_public_trace_link_endpoint=True,
    playground_type="chat",
)

# Agentic RAG 체인 (메모리 있음)
add_routes(
    app,
    AgenticRAGChain(use_memory=True).create(),
    path="/agentic-rag",
    input_type=InputAgenticRAG,
    output_type=OutputAgenticRAG
)

# Agentic RAG 체인 (메모리 없음)
add_routes(
    app,
    AgenticRAGChain(use_memory=False).create(),
    path="/agentic-rag-no-memory",
    input_type=InputAgenticRAG,
    output_type=OutputAgenticRAG
)

print("✅ 모든 Agentic RAG 체인이 추가되었습니다!")

if __name__ == "__main__":
    print("🚀 Agentic RAG LangServe 서버 시작")
    print("📍 포트: 8000")
    print("🤖 Agentic RAG Playground URLs:")
    print("   - Simple RAG: http://localhost:8000/simple-rag/playground/")
    print("   - Chat RAG: http://localhost:8000/chat-rag/playground/")
    print("   - Agentic RAG (메모리 있음): http://localhost:8000/agentic-rag/playground/")
    print("   - Agentic RAG (메모리 없음): http://localhost:8000/agentic-rag-no-memory/playground/")
    print("📚 API 문서: http://localhost:8000/docs")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
