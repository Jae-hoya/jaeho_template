# 다음과 같은 질문으로 code가 만들어졌습니다.
langchain-dev-docs 도구를 사용해서 langgraph 코드를 작성해 주세요
1. pdf 문서 기반 rag 해주세요
2. ensemble retriever 써주세요
3. tavily 검색 도구 써주세요


# LangGraph PDF RAG 시스템

LangGraph를 사용한 PDF 문서 기반 RAG(Retrieval-Augmented Generation) 시스템입니다. Ensemble Retriever와 Tavily 검색 도구를 활용하여 강력한 문서 검색 및 질의응답 기능을 제공합니다.

## 주요 기능

- **PDF 문서 처리**: PyMuPDF를 사용한 PDF 문서 로딩 및 텍스트 추출
- **Ensemble Retriever**: BM25와 FAISS를 결합한 하이브리드 검색
- **Tavily 웹 검색**: 실시간 웹 정보 검색 및 통합
- **LangGraph 워크플로우**: 조건부 라우팅을 통한 지능적 검색 전략
- **메모리 관리**: 대화 히스토리 유지

## 시스템 아키텍처

```
사용자 질문
    ↓
검색 전략 결정
    ↓
┌─────────────┬─────────────┐
│  PDF 검색   │  웹 검색    │
│ (Ensemble)  │ (Tavily)    │
└─────────────┴─────────────┘
    ↓
문서 통합 및 답변 생성
    ↓
최종 답변
```

## 설치 방법

1. **의존성 설치**
```bash
pip install -r requirements.txt
```

2. **환경 변수 설정**
```bash
# .env 파일 생성
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
```

3. **PDF 파일 준비**
```bash
mkdir data
# data 폴더에 PDF 파일을 저장
```

## 사용 방법

### 기본 실행
```python
python langgraph_pdf_rag_ensemble_tavily.py
```

### 코드 예시
```python
from langgraph_pdf_rag_ensemble_tavily import create_rag_graph

# 그래프 생성
app = create_rag_graph()

# 질문 처리
result = app.invoke({
    "messages": [],
    "documents": [],
    "query": "문서에서 AI에 대해 설명해주세요",
    "answer": "",
    "search_needed": True
})

print(result['answer'])
```

## 주요 컴포넌트

### 1. PDFRAGSystem 클래스
- PDF 문서 로딩 및 전처리
- Ensemble Retriever 설정
- Tavily 검색 도구 통합

### 2. Ensemble Retriever
- **BM25**: 키워드 기반 검색 (40% 가중치)
- **FAISS**: 의미적 유사도 검색 (60% 가중치)
- **Reciprocal Rank Fusion**: 결과 재순위화

### 3. 검색 전략
- **PDF 우선**: 일반적인 문서 질문
- **웹 검색**: 최신 정보가 필요한 질문
- **하이브리드**: PDF + 웹 검색 결과 통합

### 4. LangGraph 워크플로우
```python
# 조건부 라우팅
def should_search_web(state):
    query = state["query"].lower()
    recent_keywords = ["최신", "현재", "오늘", "recent", "current"]
    return "web_search" if any(kw in query for kw in recent_keywords) else "pdf_search"
```

## 설정 옵션

### PDF 처리 설정
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 청크 크기
    chunk_overlap=200     # 청크 겹침
)
```

### Ensemble Retriever 설정
```python
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, faiss_retriever],
    weights=[0.4, 0.6]  # BM25 40%, FAISS 60%
)
```

### Tavily 검색 설정
```python
tavily_tool = TavilySearchResults(
    max_results=5,
    include_answer=True,
    include_raw_content=True
)
```

## 고급 기능

### 1. 메모리 관리
```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

### 2. 커스텀 도구 추가
```python
@tool
def custom_search(query: str) -> str:
    """커스텀 검색 도구"""
    # 사용자 정의 검색 로직
    return search_result
```

### 3. 스트리밍 응답
```python
# 스트리밍 실행
for chunk in app.stream(initial_state):
    print(chunk)
```

## 성능 최적화

### 1. 청크 크기 조정
- 작은 청크: 정확한 검색, 많은 청크
- 큰 청크: 맥락 보존, 적은 청크

### 2. 검색 가중치 조정
```python
# 키워드 검색 강화
weights=[0.6, 0.4]  # BM25 60%, FAISS 40%

# 의미적 검색 강화  
weights=[0.3, 0.7]  # BM25 30%, FAISS 70%
```

### 3. 캐싱 활용
```python
from langchain.cache import InMemoryCache
import langchain

langchain.llm_cache = InMemoryCache()
```

## 문제 해결

### 1. PDF 로딩 오류
```python
# PDF 파일 경로 확인
pdf_path = "data/sample.pdf"
if not os.path.exists(pdf_path):
    print("PDF 파일을 찾을 수 없습니다.")
```

### 2. API 키 오류
```python
# 환경 변수 확인
import os
print("OpenAI API Key:", bool(os.getenv("OPENAI_API_KEY")))
print("Tavily API Key:", bool(os.getenv("TAVILY_API_KEY")))
```

### 3. 메모리 부족
```python
# 청크 크기 줄이기
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # 1000 → 500
    chunk_overlap=100  # 200 → 100
)
```

## 라이선스

MIT License

## 기여하기

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 지원

문제가 발생하면 GitHub Issues를 통해 문의해주세요.