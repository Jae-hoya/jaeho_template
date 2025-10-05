"""
LangGraph를 사용한 PDF 문서 기반 RAG 시스템
- PDF 문서 로딩 및 처리
- Ensemble Retriever (BM25 + FAISS)
- Tavily 검색 도구
- LangGraph 워크플로우
"""

import os
from typing import List, Dict, Any, Optional, TypedDict
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def check_api_keys():
    """API 키 확인"""
    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not openai_key or openai_key == "your-openai-api-key-here":
        print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY=your-actual-key 를 추가하세요.")
        return False
    
    if not tavily_key or tavily_key == "your-tavily-api-key-here":
        print("❌ TAVILY_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 TAVILY_API_KEY=your-actual-key 를 추가하세요.")
        return False
    
    print("✅ API 키가 올바르게 설정되었습니다.")
    return True
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
import warnings

# 경고 메시지 무시
warnings.filterwarnings("ignore")

# 환경 변수 설정
# os.environ.setdefault("OPENAI_API_KEY", "your-openai-api-key")
# os.environ.setdefault("TAVILY_API_KEY", "your-tavily-api-key")

class GraphState(TypedDict):
    """그래프 상태 정의"""
    messages: List[Dict[str, Any]]
    documents: List[Dict[str, Any]]
    query: str
    answer: str
    search_needed: bool

class PDFRAGSystem:
    """PDF 기반 RAG 시스템"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.ensemble_retriever = None
        self.tavily_tool = None
        self._setup_components()
    
    def _setup_components(self):
        """컴포넌트 설정"""
        # PDF 문서 로딩 및 처리
        self._load_and_process_pdf()
        
        # Tavily 검색 도구 설정
        self.tavily_tool = TavilySearchResults(
            max_results=5,
            include_answer=True,
            include_raw_content=True
        )
    
    def _load_and_process_pdf(self):
        """PDF 문서 로딩 및 처리"""
        print("PDF 문서를 로딩하고 처리 중...")
        
        # PDF 로더
        loader = PyMuPDFLoader(self.pdf_path)
        documents = loader.load()
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)
        
        # FAISS 벡터 스토어 생성
        faiss_vectorstore = FAISS.from_documents(
            documents=split_docs,
            embedding=self.embeddings
        )
        faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 5})
        
        # BM25 리트리버 생성
        bm25_retriever = BM25Retriever.from_documents(split_docs)
        bm25_retriever.k = 5
        
        # Ensemble Retriever 생성
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever],
            weights=[0.4, 0.6]  # BM25 40%, FAISS 60%
        )
        
        print(f"PDF 문서 처리 완료: {len(split_docs)}개 청크 생성")
    
    def retrieve_documents(self, query: str) -> List[Dict[str, Any]]:
        """문서 검색"""
        try:
            docs = self.ensemble_retriever.invoke(query)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "source": "pdf"
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"문서 검색 오류: {e}")
            return []
    
    def search_web(self, query: str) -> List[Dict[str, Any]]:
        """웹 검색"""
        try:
            results = self.tavily_tool.invoke({"query": query})
            return [
                {
                    "content": result.get("content", ""),
                    "url": result.get("url", ""),
                    "source": "web"
                }
                for result in results
            ]
        except Exception as e:
            print(f"웹 검색 오류: {e}")
            return []

def should_search_web(state: GraphState) -> str:
    """웹 검색 필요성 판단"""
    query = state["query"].lower()
    
    # 최신 정보가 필요한 키워드들
    recent_keywords = [
        "최신", "현재", "오늘", "이번", "recent", "current", "latest", "today"
    ]
    
    # 외부 정보가 필요한 키워드들
    external_keywords = [
        "뉴스", "시장", "가격", "날씨", "news", "market", "price", "weather"
    ]
    
    if any(keyword in query for keyword in recent_keywords + external_keywords):
        return "web_search"
    else:
        return "pdf_search"

def pdf_search_node(state: GraphState) -> GraphState:
    """PDF 검색 노드"""
    print("PDF 문서에서 검색 중...")
    
    # RAG 시스템 인스턴스 생성 (실제로는 전역으로 관리해야 함)
    rag_system = PDFRAGSystem("data/SPRi AI Brief_8월호_산업동향_F.pdf")  # 실제 PDF 경로로 변경
    
    # 문서 검색
    documents = rag_system.retrieve_documents(state["query"])
    
    # 프롬프트 생성
    context = "\n\n".join([doc["content"] for doc in documents])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 주어진 문서를 바탕으로 질문에 답변하는 AI 어시스턴트입니다.
        
문서 내용:
{context}

질문에 정확하고 도움이 되는 답변을 제공하세요. 문서에 없는 정보는 "문서에서 해당 정보를 찾을 수 없습니다"라고 답변하세요."""),
        ("user", "{query}")
    ])
    
    chain = prompt | rag_system.llm | StrOutputParser()
    
    try:
        answer = chain.invoke({"context": context, "query": state["query"]})
    except Exception as e:
        answer = f"답변 생성 중 오류가 발생했습니다: {e}"
    
    return {
        **state,
        "documents": documents,
        "answer": answer,
        "search_needed": False
    }

def web_search_node(state: GraphState) -> GraphState:
    """웹 검색 노드"""
    print("웹에서 검색 중...")
    
    # RAG 시스템 인스턴스 생성
    rag_system = PDFRAGSystem("data/SPRi AI Brief_8월호_산업동향_F.pdf")
    
    # 웹 검색
    web_docs = rag_system.search_web(state["query"])
    
    # PDF 검색도 병행
    pdf_docs = rag_system.retrieve_documents(state["query"])
    
    # 모든 문서 결합
    all_documents = pdf_docs + web_docs
    
    # 프롬프트 생성
    context = "\n\n".join([doc["content"] for doc in all_documents])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """당신은 주어진 문서와 웹 검색 결과를 바탕으로 질문에 답변하는 AI 어시스턴트입니다.
        
문서 및 웹 검색 결과:
{context}

질문에 정확하고 최신 정보를 포함한 답변을 제공하세요. 정보의 출처를 명시하세요."""),
        ("user", "{query}")
    ])
    
    chain = prompt | rag_system.llm | StrOutputParser()
    
    try:
        answer = chain.invoke({"context": context, "query": state["query"]})
    except Exception as e:
        answer = f"답변 생성 중 오류가 발생했습니다: {e}"
    
    return {
        **state,
        "documents": all_documents,
        "answer": answer,
        "search_needed": False
    }

def create_rag_graph():
    """RAG 그래프 생성"""
    
    # 상태 그래프 생성
    workflow = StateGraph(GraphState)
    
    # 노드 추가
    workflow.add_node("pdf_search", pdf_search_node)
    workflow.add_node("web_search", web_search_node)
    
    # 엔트리 포인트 설정
    workflow.set_entry_point("pdf_search")
    
    # 조건부 라우팅
    workflow.add_conditional_edges(
        "pdf_search",
        should_search_web,
        {
            "pdf_search": END,
            "web_search": "web_search"
        }
    )
    
    workflow.add_edge("web_search", END)
    
    # 메모리 설정
    memory = MemorySaver()
    
    # 그래프 컴파일
    app = workflow.compile(checkpointer=memory)
    
    return app

def main():
    """메인 실행 함수"""
    print("LangGraph PDF RAG 시스템 시작")
    
    # API 키 확인
    if not check_api_keys():
        print("\n❌ API 키를 설정한 후 다시 실행하세요.")
        return
    
    # PDF 파일 존재 확인
    pdf_path = "data/SPRi AI Brief_8월호_산업동향_F.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        print("   data 폴더에 PDF 파일이 있는지 확인하세요.")
        return
    
    print(f"✅ PDF 파일 확인: {pdf_path}")
    
    # 그래프 생성
    app = create_rag_graph()
    
    # 대화 루프
    while True:
        try:
            query = input("\n질문을 입력하세요 (종료: 'quit'): ")
            
            if query.lower() in ['quit', 'exit', '종료']:
                print("시스템을 종료합니다.")
                break
            
            if not query.strip():
                continue
            
            # 초기 상태 설정
            initial_state = {
                "messages": [],
                "documents": [],
                "query": query,
                "answer": "",
                "search_needed": True
            }
            
            # 그래프 실행 (config 추가)
            config = {"configurable": {"thread_id": "user_session"}}
            result = app.invoke(initial_state, config=config)
            
            print(f"\n답변: {result['answer']}")
            
            # 검색된 문서 정보 출력
            if result['documents']:
                print(f"\n참조된 문서 수: {len(result['documents'])}")
                for i, doc in enumerate(result['documents'][:3], 1):
                    source = doc.get('source', 'unknown')
                    content_preview = doc['content'][:100] + "..." if len(doc['content']) > 100 else doc['content']
                    print(f"  {i}. [{source}] {content_preview}")
            
        except KeyboardInterrupt:
            print("\n시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()