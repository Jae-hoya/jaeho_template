# LangGraph RAG CLI

Routing 기반 LangGraph RAG 시스템 - Hybrid Search를 활용한 대출 상품 검색

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)
[![LangGraph](https://img.shields.io/badge/langgraph-1.0+-green.svg)](https://github.com/langchain-ai/langgraph)

**빠른 시작**: [QUICKSTART.md](QUICKSTART.md) 📖

## 개요

이 프로젝트는 LangGraph를 사용한 라우팅 기반 RAG (Retrieval-Augmented Generation) 시스템입니다.
질문을 분석하여 검색이 필요한지 판단하고, 필요한 경우 Hybrid Search(BM25 + Vector)로 관련 문서를 검색한 후 답변을 생성합니다.

**✓ 독립 실행**: 이 프로젝트는 `search_app` 모듈을 포함하고 있어 외부 의존성 없이 독립적으로 실행됩니다.

## 워크플로우

```
START → route → [조건부 분기]
                ├─ search → retrieve → generate → END
                └─ direct → generate → END
```

1. **Route**: 질문 분석 → search/direct 판단 (GPT-5-mini)
2. **Retrieve**: Hybrid Search로 top-3 검색 (조건부 실행)
3. **Generate**: 답변 생성 (GPT-5-mini)

## 핵심 구현

- **StateGraph**: LangGraph의 상태 기반 워크플로우
- **Conditional Edges**: 라우팅 로직으로 동적 경로 결정
- **Hybrid Search**: BM25(전문 검색) + Vector(의미 검색) + RRF 융합

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

또는 uv 사용:

```bash
uv pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 생성 또는 `C:\Users\skyop\jaeho_template\dotenv_windows`에 다음 변수 설정:

```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/postgres
```

### 3. 데이터베이스 초기화

데이터베이스를 초기화하고 대출 상품 데이터를 로드합니다:

```bash
# 데이터 파일 복사 (../hybrid_search에서)
cp ../hybrid_search/loan_products.json ./

# 데이터베이스 초기화
python -m search_app.setup
```

**최적화**: 임베딩 생성은 배치 처리로 수행되어 OpenAI API 호출을 최소화합니다 (67개 상품 → 1번 API 호출).

또는 이미 초기화된 데이터베이스가 있다면 이 단계를 건너뛸 수 있습니다.

## 사용법

### 🌐 Streamlit 웹 UI (권장)

웹 브라우저에서 사용하기 쉬운 인터페이스:

```bash
streamlit run streamlit_app.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다.

**기능:**
- 💬 채팅 인터페이스
- 🔍 검색 결과 시각화 (접을 수 있는 검색 결과)
- 📊 실시간 통계 (검색/직접 답변 카운트)
- ⚙️ 디버그 모드 토글
- 💡 예제 질문 버튼 (클릭 시 즉시 처리, 중복 방지)
- 🏠 홈 버튼 (대화 초기화 및 처음으로 돌아가기)

### 📟 CLI 사용

터미널에서 직접 실행:

```bash
python langgraph_rag.py "의사 전용 대출 상품 추천해줘"
```

또는 uv 사용:

```bash
uv run python langgraph_rag.py "의사 전용 대출 상품 추천해줘"
```

### 디버그 모드

워크플로우 각 단계를 확인하려면 `--debug` 옵션 사용:

```bash
python langgraph_rag.py "저금리 대출 찾고 있어요" --debug
```

### Jupyter 노트북으로 테스트

대화형 환경에서 테스트하려면 Jupyter 노트북을 사용하세요:

```bash
jupyter notebook test_langgraph_rag.ipynb
```

노트북 포함 내용:
- 환경 설정 및 패키지 확인
- 데이터베이스 연결 테스트
- Direct/Search 질문 테스트
- 디버그 모드 / 클린 모드 비교
- 배치 테스트 및 결과 분석
- State 추적 및 시각화

### Python 스크립트로 테스트

자동화된 테스트를 실행하려면:

```bash
python test_langgraph_rag.py
```

## 예제

### 검색이 필요한 질문

```bash
$ python langgraph_rag.py "의사 전용 대출 상품 추천해줘"

답변:
의사 전용 대출 상품으로는 다음을 추천드립니다:

1. KB국민은행 KB직장인든든대출
   - 금리: 3.45% ~ 4.67%
   - 의사, 약사 등 전문직 종사자 대상
   ...
```

### 직접 답변 가능한 질문

```bash
$ python langgraph_rag.py "안녕하세요"

답변:
안녕하세요! 대출 상품에 대해 궁금하신 점이 있으시면 언제든 질문해주세요.
```

## 아키텍처

### State 정의

```python
class RAGState(TypedDict):
    question: str
    route_decision: str  # "search" or "direct"
    search_results: List[Dict[str, Any]]
    answer: str
    debug: bool
```

### 노드 구성

1. **route_node**: LLM으로 질문 분석 및 경로 결정
2. **retrieve_node**: HybridSearch로 top-3 검색 (search 경로만)
3. **generate_node**: 컨텍스트 기반 답변 생성

### Conditional Edges

```python
workflow.add_conditional_edges(
    "route",
    decide_next_step,
    {
        "search": "retrieve",
        "direct": "generate"
    }
)
```

## 기술 스택

- **LangGraph 1.0+**: 상태 기반 워크플로우 오케스트레이션
- **LangChain**: LLM 통합
- **GPT-5-mini**: 라우팅 및 답변 생성
- **Hybrid Search**: ParadeDB (BM25) + pgvector (Vector Search)
- **PostgreSQL**: 데이터 저장소

## 성능 최적화

### 배치 임베딩 생성
- **개선 전**: 67개 상품 × 개별 API 호출 = 67번 호출
- **개선 후**: 배치 처리로 1번 API 호출
- **효과**: API 호출 횟수 98.5% 감소, 초기화 속도 대폭 향상

### UI/UX 개선
- **즉시 응답**: 스트리밍 효과 제거로 답변 즉시 표시
- **예제 질문**: 클릭 시 바로 처리, 중복 표시 방지
- **홈 버튼**: 왼쪽 상단에 홈 버튼으로 언제든지 초기 화면으로 복귀
- **에러 처리**: 상세한 에러 메시지와 traceback으로 디버깅 용이

## 디렉토리 구조

```
LangGraph_RAG/
├── streamlit_app.py           # Streamlit 웹 UI ⭐
├── langgraph_rag.py           # 메인 CLI 스크립트
├── test_langgraph_rag.py      # Python 테스트 스크립트
├── test_langgraph_rag.ipynb   # Jupyter 노트북 테스트
├── requirements.txt           # Python 의존성
├── .env.example               # 환경 변수 예제
├── README.md                  # 사용 가이드
├── SETUP.md                   # 설치 및 설정 가이드
├── DEPLOYMENT.md              # 배포 가이드 ⭐
├── DEPENDENCY.md              # 의존성 가이드
├── PRD.md                     # 프로젝트 요구사항 문서
├── search_app/                # 하이브리드 검색 모듈 (포함됨)
│   ├── __init__.py
│   ├── hybrid_search.py       # 검색 로직
│   ├── database.py            # DB 연결
│   ├── config.py              # 설정
│   ├── data_loader.py         # 데이터 로더 (배치 임베딩 생성)
│   ├── main.py                # 검색 CLI
│   └── setup.py               # DB 초기화
└── loan_products.json         # 대출 상품 데이터
```

## 참고

- **설치 가이드**: [SETUP.md](SETUP.md)
- **배포 가이드**: [DEPLOYMENT.md](DEPLOYMENT.md) 🌐
- **의존성 가이드**: [DEPENDENCY.md](DEPENDENCY.md)
- LangGraph 공식 문서: https://github.com/langchain-ai/langgraph
- PRD: `PRD.md`
