# Agentic RAG LangServe API

LangServe를 사용하여 Agentic RAG 시스템을 API로 노출한 서버입니다.

## 파일 구조

```
langserve/
├── langserve_server.py      # 기본 LangServe 서버 (간단한 예시)
├── langserve_complete.py    # 완전한 LangServe 서버 (실제 RAG 모듈 사용)
├── client_example.py        # 클라이언트 테스트 예시
├── fastapi_server.py        # 기존 FastAPI 서버
└── README_LangServe.md      # 이 파일
```

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install langserve fastapi uvicorn requests
```

### 2. 서버 실행

#### 기본 LangServe 서버 (포트 8001)
```bash
uvicorn langserve_server:app --reload --port 8001
```

#### 완전한 LangServe 서버 (포트 8002)
```bash
uvicorn langserve_complete:app --reload --port 8002
```

### 3. 클라이언트 테스트

```bash
python client_example.py
```

## API 엔드포인트

### LangServe 엔드포인트

#### 1. 간단한 RAG (`/simple-rag`)
- **입력**: `{"question": "질문 내용"}`
- **출력**: `{"answer": "답변 내용"}`

#### 2. 채팅 히스토리 RAG (`/chat-rag`)
- **입력**: `{"question": "질문 내용", "chat_history": [["이전 질문", "이전 답변"]]}`
- **출력**: `{"answer": "답변 내용", "chat_history": [["이전 질문", "이전 답변"], ["현재 질문", "현재 답변"]]}`

#### 3. Agentic RAG (`/agentic-rag`)
- **입력**: `{"question": "질문 내용", "thread_id": "선택적 스레드 ID"}`
- **출력**: `{"answer": "답변 내용", "thread_id": "스레드 ID", "used_agents": ["사용된 에이전트들"], "timestamp": "타임스탬프"}`

#### 4. Agentic RAG (메모리 없음) (`/agentic-rag-no-memory`)
- **입력**: `{"question": "질문 내용", "thread_id": "선택적 스레드 ID"}`
- **출력**: `{"answer": "답변 내용", "thread_id": "스레드 ID", "used_agents": ["사용된 에이전트들"], "timestamp": "타임스탬프"}`

### 일반 FastAPI 엔드포인트

- `GET /` - API 상태 확인
- `GET /health` - 시스템 상태 확인
- `POST /feedback` - 피드백 제출
- `POST /conversation` - 대화 저장
- `POST /conversation/thread` - 스레드별 대화 저장
- `POST /conversation/batch` - 배치 대화 저장
- `POST /session/summary` - 세션 요약 저장
- `GET /feedback` - 모든 피드백 조회
- `GET /conversation` - 모든 대화 조회
- `GET /feedback/{thread_id}` - 특정 스레드 피드백 조회
- `GET /conversation/{thread_id}` - 특정 스레드 대화 조회

## 사용 예시

### Python 클라이언트

```python
import requests

# 간단한 RAG 질문
response = requests.post("http://localhost:8002/simple-rag/invoke", 
                        json={"input": {"question": "AI의 미래에 대해 설명해주세요."}})
result = response.json()
print(result["output"]["answer"])

# Agentic RAG 질문
response = requests.post("http://localhost:8002/agentic-rag/invoke",
                        json={"input": {"question": "머신러닝이란?", "thread_id": "my_thread"}})
result = response.json()
print(result["output"]["answer"])
```

### curl 예시

```bash
# 간단한 RAG 테스트
curl -X POST "http://localhost:8002/simple-rag/invoke" \
     -H "Content-Type: application/json" \
     -d '{"input": {"question": "AI의 미래에 대해 설명해주세요."}}'

# Agentic RAG 테스트
curl -X POST "http://localhost:8002/agentic-rag/invoke" \
     -H "Content-Type: application/json" \
     -d '{"input": {"question": "머신러닝이란?", "thread_id": "test_thread"}}'
```

## LangServe의 장점

1. **자동 API 생성**: LangChain 체인을 자동으로 API로 노출
2. **스키마 자동 생성**: Pydantic 모델을 기반으로 자동 스키마 생성
3. **Playground 지원**: 웹 UI에서 직접 테스트 가능
4. **표준화된 인터페이스**: 일관된 API 인터페이스 제공
5. **타입 안전성**: 입력/출력 타입 검증

## 주의사항

1. **모듈 의존성**: `langserve_complete.py`는 기존 RAG 모듈들(`rag.py`, `retriever.py`, `chain.py` 등)에 의존합니다.
2. **환경 변수**: OpenAI API 키 등 필요한 환경 변수가 설정되어 있어야 합니다.
3. **포트 충돌**: 다른 서비스와 포트가 겹치지 않도록 주의하세요.

## 문제 해결

### 모듈 Import 오류
```
ImportError: No module named 'rag'
```
- RAG 모듈들이 올바른 위치에 있는지 확인
- `sys.path.append()` 부분이 올바른 경로를 가리키는지 확인

### API 키 오류
```
OpenAI API key not found
```
- 환경 변수에 `OPENAI_API_KEY` 설정 확인

### 포트 사용 중 오류
```
Address already in use
```
- 다른 포트 번호 사용: `--port 8003`
- 또는 기존 프로세스 종료

## 추가 정보

- LangServe 공식 문서: https://python.langchain.com/docs/langserve
- FastAPI 문서: https://fastapi.tiangolo.com
- LangChain 문서: https://python.langchain.com
