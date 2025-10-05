# 🤖 Agentic RAG System

**다중 에이전트 기반 지능형 RAG(Retrieval-Augmented Generation) 시스템**

이 프로젝트는 LangGraph를 활용한 다중 에이전트 아키텍처로 구성된 지능형 RAG 시스템입니다. 각 에이전트가 특화된 역할을 수행하며, 감독자 에이전트가 전체 워크플로우를 조율합니다.

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│  Supervisor      │───▶│  Specialized    │
│                 │    │  Agent           │    │  Agents         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Response        │
                       │  Generation      │
                       └──────────────────┘
```

### 🎯 핵심 에이전트

1. **🔍 Retriever Agent**: SPRI AI Brief 문서 검색 및 정보 추출
2. **🌐 Researcher Agent**: 웹 기반 최신 정보 수집 (Tavily Search)
3. **📊 Coder Agent**: 데이터 시각화 및 차트 생성 (Python REPL)
4. **💬 General LLM Agent**: 일반적인 대화 및 질의응답
5. **👑 Supervisor Agent**: 에이전트 간 작업 조율 및 라우팅

## 📁 프로젝트 구조

```
Agentic_RAG/
├── 📓 Jupyter Notebooks
│   ├── 01.Agentic_RAG.ipynb          # 메인 구현 노트북
│   ├── 02.Modules.ipynb              # 모듈화된 컴포넌트
│   ├── 03.Agentic_RAG copy 2.ipynb   # 백업 노트북
│   └── Agentic_RAG.ipynb             # 통합 노트북
│
├── 🐍 Python Modules
│   ├── agents.py                     # 에이전트 생성 및 관리
│   ├── chain.py                      # LangGraph 체인 구성
│   ├── graph.py                      # 그래프 생성 및 관리
│   ├── nodes.py                      # 노드 함수 정의
│   ├── states.py                     # 상태 관리
│   ├── tools.py                      # 도구 정의
│   ├── rag.py                        # RAG 체인 구현
│   ├── retriever.py                  # 검색기 팩토리
│   └── base.py                       # 기본 유틸리티
│
├── 🖥️ Streamlit Applications
│   ├── stream_main.py                # 기본 스트림릿 앱
│   ├── fast_main.py                  # FastAPI 통합 앱
│   └── streamlit_wrapper.py         # 스트림릿 래퍼
│
├── 🚀 API Servers
│   ├── fastapi_server.py             # FastAPI 서버
│   └── run_fastapi_server.py         # 서버 실행 스크립트
│
├── 📝 Prompts
│   ├── rag-prompt.yaml               # 기본 RAG 프롬프트
│   └── rag-prompt-with-chat-history.yaml  # 대화 히스토리 포함 프롬프트
│
├── 📋 Requirements
│   ├── requirements.txt              # 기본 의존성
│   └── requirements_fastapi.txt      # FastAPI 의존성
│
└── 📚 Documentation
    └── README_FastAPI.md             # FastAPI 가이드
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd RAG_strategies/Agentic_RAG

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. Qdrant 벡터 데이터베이스 설정

#### 🐳 로컬 Docker 실행 (무료)

```bash
# Qdrant Docker 컨테이너 실행
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant:latest
```

또는 Docker Compose를 사용하는 경우:

```yaml
# docker-compose.yml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./qdrant_storage:/qdrant/storage
```

#### ☁️ 클라우드 사용 (유료)

**중요**: Qdrant 클라우드 서비스를 사용하려면 **유료 플랜**이 필요합니다.

- **Qdrant Cloud**: [https://cloud.qdrant.io/](https://cloud.qdrant.io/)
- **무료 플랜**: 제한된 용량과 기능
- **유료 플랜**: 확장된 용량, 고급 기능, 지원 서비스

클라우드 사용 시 환경 변수:
```env
# Qdrant Cloud 설정 (유료)
QDRANT_URL=https://your-cluster.qdrant.tech
QDRANT_API_KEY=your_api_key
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 변수들을 설정하세요:

```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Tavily Search API
TAVILY_API_KEY=your_tavily_api_key

# LangSmith (선택사항)
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Agentic RAG System

# Qdrant 설정 (로컬 Docker)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Qdrant Cloud 설정 (유료 - 선택사항)
# QDRANT_URL=https://your-cluster.qdrant.tech
# QDRANT_API_KEY=your_api_key
```

### 4. 실행 방법

#### 🖥️ Streamlit 앱 실행

```bash
# 기본 스트림릿 앱
streamlit run stream_main.py

# FastAPI 통합 앱 (권장)
streamlit run fast_main.py
```

#### 🚀 FastAPI 서버 실행

```bash
# Python으로 직접 실행 (권장)
python fastapi_server.py

# 개발 모드 (자동 재시작)
python run_fastapi_server.py

# uvicorn으로 실행
uvicorn fastapi_server:app --reload --host 0.0.0.0 --port 8000
```

#### 📓 Jupyter Notebook 실행

```bash
jupyter notebook 01.Agentic_RAG.ipynb
```

## 🔧 주요 기능

### 1. 다중 에이전트 시스템

- **지능형 라우팅**: 감독자 에이전트가 질문 유형에 따라 적절한 에이전트 선택
- **전문성 분화**: 각 에이전트가 특화된 도메인에서 최적의 성능 발휘
- **협업 워크플로우**: 에이전트 간 정보 공유 및 협업

### 2. 고급 검색 기능

- **하이브리드 검색**: Dense + Sparse 검색의 조합
- **다중 벡터스토어**: Qdrant, FAISS 지원
- **컨텍스트 압축**: 관련성 높은 정보만 선별

### 3. 실시간 웹 검색

- **Tavily Search 통합**: 최신 정보 수집
- **신뢰성 검증**: 다중 소스 정보 교차 검증

### 4. 데이터 시각화

- **Python REPL 도구**: 동적 차트 생성
- **한글 폰트 지원**: Windows/macOS/Linux 호환
- **인터랙티브 플롯**: matplotlib, seaborn 활용

### 5. 대화 관리

- **컨텍스트 유지**: 대화 히스토리 기반 응답
- **메모리 관리**: 세션별 상태 관리
- **피드백 시스템**: 사용자 평가 수집

## 📊 API 엔드포인트

### 기본 엔드포인트

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | 서버 상태 확인 |
| GET | `/docs` | API 문서 (Swagger UI) |

### 피드백 관리

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/feedback` | 피드백 제출 |
| GET | `/feedback` | 모든 피드백 조회 |
| GET | `/feedback/{thread_id}` | 특정 스레드 피드백 조회 |

### 대화 관리

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/conversation` | 단일 대화 저장 |
| POST | `/conversation/thread` | 스레드별 대화 저장 |
| POST | `/conversation/batch` | 배치 대화 저장 |
| GET | `/conversation` | 모든 대화 조회 |
| GET | `/conversation/{thread_id}` | 특정 스레드 대화 조회 |

### 세션 관리

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/session/summary` | 세션 요약 저장 |

## 🛠️ 사용 예시

### Python API 사용

```python
from retriever import QdrantRetrieverFactory
from chain import create_agentic_rag_graph

# 검색기 설정
qs = QdrantRetrieverFactory()
retriever = qs.retriever(collection_name="RAG_Example", fetch_k=3)

# 그래프 생성
graph = create_agentic_rag_graph(retriever)

# 질의응답 실행
result = graph.invoke({
    "messages": [HumanMessage(content="미드저니 신버전에 대해 알려주세요")]
})
```

### HTTP API 사용

```python
import requests

# 질의응답 요청
response = requests.post(
    "http://localhost:8000/agentic-rag",
    json={
        "query": "SPRI AI Brief에서 인공지능 동향에 대해 알려주세요",
        "thread_id": "user_123",
        "chat_history": [
            {"role": "user", "content": "안녕하세요"},
            {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
        ]
    }
)

result = response.json()
print(result["response"])
```

## 🔍 고급 설정

### 1. 검색기 설정

```python
# Qdrant 검색기 (로컬 Docker - 무료)
from retriever import QdrantRetrieverFactory

# Qdrant가 Docker로 실행 중이어야 함
qs = QdrantRetrieverFactory(
    host="localhost",  # Docker 컨테이너의 localhost
    port=6333,        # Docker 포트 매핑
    dense_model="bge-m3",
    sparse_model="Qdrant/bm25"
)

# Qdrant Cloud 검색기 (유료)
# qs_cloud = QdrantRetrieverFactory(
#     host="your-cluster.qdrant.tech",  # 클라우드 URL
#     port=443,                        # HTTPS 포트
#     api_key="your_api_key"           # API 키 필요
# )

# FAISS 검색기 (로컬 파일 기반 - 무료)
from retriever import FAISSRetrieverFactory

fa = FAISSRetrieverFactory(
    model="bge-m3",
    cache_dir="./cache/"
)
```

### 2. 에이전트 커스터마이징

```python
from agents import create_retriever_agent, create_research_agent

# 커스텀 시스템 프롬프트
custom_prompt = """
You are a specialized research agent focused on AI trends.
Your primary responsibilities:
1. Search through SPRI AI Brief documents
2. Find relevant information about AI technologies
3. Provide detailed, well-sourced answers
"""

retriever_agent = create_retriever_agent(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o-mini", temperature=0),
    system_prompt=custom_prompt
)
```

### 3. 그래프 구성

```python
from graph import create_agentic_rag_graph

# 메모리 사용 그래프
graph_with_memory = create_agentic_rag_graph(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o-mini"),
    use_memory=True
)

# 메모리 없는 그래프
graph_no_memory = create_agentic_rag_graph(
    retriever=retriever,
    llm=ChatOpenAI(model="gpt-4o-mini"),
    use_memory=False
)
```

## 📈 성능 최적화

### 1. 검색 성능

- **하이브리드 검색**: Dense + Sparse 검색으로 정확도 향상
- **컨텍스트 압축**: 관련성 높은 문서만 선별
- **캐싱**: 자주 사용되는 쿼리 결과 캐싱

### 2. 응답 속도

- **병렬 처리**: 에이전트 간 병렬 실행
- **스트리밍**: 실시간 응답 스트리밍
- **비동기 처리**: FastAPI 비동기 처리

### 3. 메모리 관리

- **세션 관리**: 스레드별 메모리 격리
- **가비지 컬렉션**: 자동 메모리 정리
- **체크포인팅**: 상태 저장 및 복원

## 🐛 문제 해결

### 일반적인 문제

1. **Qdrant 연결 오류**
   ```bash
   # Qdrant Docker 컨테이너 상태 확인
   docker ps | grep qdrant
   
   # Qdrant 재시작
   docker restart qdrant_container_name
   
   # 클라우드 사용 시 API 키 확인
   echo $QDRANT_API_KEY
   ```

2. **Qdrant 클라우드 연결 문제**
   ```bash
   # 클라우드 URL 및 API 키 확인
   curl -H "api-key: $QDRANT_API_KEY" https://your-cluster.qdrant.tech/collections
   ```

3. **포트 충돌**
   ```bash
   # 다른 포트 사용
   python fastapi_server.py --port 8001
   ```

4. **의존성 오류**
   ```bash
   # 의존성 재설치
   pip install -r requirements.txt --force-reinstall
   ```

5. **환경 변수 오류**
   ```bash
   # .env 파일 확인
   cat .env
   ```

6. **메모리 부족**
   ```bash
   # 메모리 사용량 확인
   python -c "import psutil; print(psutil.virtual_memory())"
   ```

### 디버깅 팁

1. **로그 레벨 설정**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **LangSmith 추적**
   ```python
   import os
   os.environ["LANGCHAIN_TRACING_V2"] = "true"
   os.environ["LANGCHAIN_PROJECT"] = "Agentic RAG Debug"
   ```

3. **에이전트 상태 확인**
   ```python
   # 그래프 실행 상태 확인
   for chunk in graph.stream(inputs):
       print(f"Node: {list(chunk.keys())}")
   ```

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📚 추가 자료

- [LangGraph 공식 문서](https://python.langchain.com/docs/langgraph)
- [LangChain 공식 문서](https://python.langchain.com/docs)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Streamlit 공식 문서](https://docs.streamlit.io/)
- [Qdrant 공식 문서](https://qdrant.tech/documentation/)
- [Docker 공식 문서](https://docs.docker.com/)




