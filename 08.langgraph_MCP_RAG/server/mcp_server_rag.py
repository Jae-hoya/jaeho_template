
from mcp.server.fastmcp import FastMCP
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_tavily import TavilySearch
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from dotenv import load_dotenv
from typing import List, Literal
import os
import pickle

load_dotenv(override=True)

# FastMCP 서버 초기화
mcp = FastMCP(
    "RAG_Server",
    instructions="A RAG server that provides vector search, document addition, and web search capabilities."
)

# 전역 변수로 벡터스토어 관리
vector_store = None
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
bm25_retriever = None
ensemble_retriever = None
all_documents = []  # BM25를 위한 문서 리스트

# 이것은 TOOL로 안쓰기 때문에 함수로 만들어둔다.
def initialize_vector_store():
    """벡터 스토어를 초기화하고 PDF 문서를 로드합니다."""
    global vector_store, bm25_retriever, ensemble_retriever, all_documents

    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, "data", "SPRI_AI_Brief_2023년12월호_F.pdf")

    loader = PyMuPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(documents)

    vector_store = FAISS.from_documents(splits, embeddings)
    
    # BM25 Retriever 구축
    all_documents = splits
    bm25_retriever = BM25Retriever.from_documents(splits)
    bm25_retriever.k = 100  # 기본 검색 개수 설정
    
    # FAISS Retriever 생성
    faiss_retriever = vector_store.as_retriever(search_kwargs={"k": 100})
    
    # Ensemble Retriever 생성 (BM25 40%, FAISS 60%)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.4, 0.6]
    )
    
    return vector_store

# 이 TEXT를 우리의 VECTORSTORE에 원격으로 밀어넣는다. 문서를 외부에서 받아서 넣을 수 있다는 것이다.
@mcp.tool()
async def vector_search(
    query: str, 
    search_type: Literal["semantic", "keyword", "hybrid"] = "semantic",
    k: int = 5
) -> str:
    """벡터 스토어에서 문서를 검색합니다."""
    global vector_store

    if vector_store is None:
        initialize_vector_store()

    if search_type == "semantic":
        results = vector_store.similarity_search(query, k=k)
    elif search_type == "keyword":
        # LangChain BM25Retriever를 사용한 키워드 검색
        bm25_retriever.k = k
        results = bm25_retriever.invoke(query)
    elif search_type == "hybrid":

        # BM25와 FAISS retriever의 k 값 설정
        bm25_retriever.k = k * 2
        faiss_retriever = vector_store.as_retriever(search_kwargs={"k": k * 2})
        
        # Ensemble Retriever 재생성 (k 값 반영)
        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, faiss_retriever],
            weights=[0.3, 0.7]
        )
        
        results = ensemble_retriever.invoke(query)
        # 상위 k개만 반환
        results = results[:k]

    return "\n\n".join([doc.page_content for doc in results])

@mcp.tool()
async def add_document(text: str, metadata: dict = None) -> str:
    """사용자 텍스트를 벡터 스토어에 추가합니다."""
    global vector_store

    if vector_store is None:
        initialize_vector_store()

    if metadata is None:
        metadata = {"source": "user_input"}

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    documents = [Document(page_content=text, metadata=metadata)]
    splits = text_splitter.split_documents(documents)

    vector_store.add_documents(splits)
    
    # BM25 Retriever와 Ensemble Retriever에도 추가
    global bm25_retriever, ensemble_retriever, all_documents
    if bm25_retriever is None:
        # 초기화되지 않은 경우 초기화
        if vector_store is None:
            initialize_vector_store()
        else:
            # 기존 문서들로 BM25 Retriever 구축
            all_docs = []
            for doc_id in vector_store.docstore._dict.keys():
                all_docs.append(vector_store.docstore._dict[doc_id])
            all_documents = all_docs
            bm25_retriever = BM25Retriever.from_documents(all_docs)
            bm25_retriever.k = 100
            
            # Ensemble Retriever 재생성
            faiss_retriever = vector_store.as_retriever(search_kwargs={"k": 100})
            ensemble_retriever = EnsembleRetriever(
                retrievers=[bm25_retriever, faiss_retriever],
                weights=[0.4, 0.6]
            )
    
    # 새 문서 추가 - BM25 Retriever와 Ensemble Retriever 재구축
    all_documents.extend(splits)
    bm25_retriever = BM25Retriever.from_documents(all_documents)
    bm25_retriever.k = 100
    
    # Ensemble Retriever 재생성
    faiss_retriever = vector_store.as_retriever(search_kwargs={"k": 100})
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever],
        weights=[0.4, 0.6]
    )

    return f"문서가 성공적으로 추가되었습니다. 총 {len(text)} 문자, {len(splits)}개 청크로 분할됨"

@mcp.tool()
async def web_search(query: str, max_results: int = 3) -> str:
    """TavilySearch를 사용하여 웹 검색을 수행합니다."""
    tavily = TavilySearch(max_results=max_results)
    results = tavily.invoke(query)

    formatted_results = []
    for i, result in enumerate(results, 1):
        formatted_results.append(
            f"검색 결과 {i}:\n"
            f"제목: {result.get('title', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}\n"
            f"내용: {result.get('content', 'N/A')}\n"
        )

    return "\n".join(formatted_results)

if __name__ == "__main__":
    # 서버 초기화
    print("RAG MCP 서버를 초기화합니다...")
    initialize_vector_store()
    print("벡터 스토어 초기화 완료!")

    # MCP 서버 실행
    mcp.run(transport="stdio")

