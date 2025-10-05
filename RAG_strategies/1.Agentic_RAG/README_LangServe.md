# LangServe를 사용한 Agentic RAG 시스템

이 문서는 LangServe를 사용하여 Agentic RAG 시스템을 REST API로 노출하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements_langserve.txt
```

### 2. 환경 변수 설정

`.env` 파일에 필요한 환경 변수를 설정합니다:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Agentic RAG System
```

### 3. 서버 실행

```bash
python run_langserve_server.py
```

또는

```bash
python langserve_server.py
```

## 📡 API 엔드포인트

### 기본 엔드포인트

- **GET** `/` - 서버 상태 확인
- **GET** `/docs` - API 문서 (Swagger UI)

### Agentic RAG 엔드포인트

- **POST** `/agentic-rag` - Agentic RAG 질의응답
- **POST** `/agentic-rag/stream` - 스트리밍 응답
- **POST** `/agentic-rag/feedback` - 피드백 제출

### 데이터 관리 엔드포인트

- **POST** `/feedback` - 피드백 데이터 제출
- **GET** `/feedback` - 모든 피드백 조회
- **GET** `/feedback/{thread_id}` - 특정 스레드 피드백 조회

- **POST** `/conversation` - 대화 데이터 제출
- **POST** `/conversation/thread` - 스레드별 대화 저장
- **POST** `/conversation/batch` - 배치 대화 저장
- **GET** `/conversation` - 모든 대화 조회
- **GET** `/conversation/{thread_id}` - 특정 스레드 대화 조회

- **POST** `/session/summary` - 세션 요약 저장

## 🔧 사용법

### 1. 기본 질의응답

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

### 2. 스트리밍 응답

```python
import requests

# 스트리밍 요청
response = requests.post(
    "http://localhost:8000/agentic-rag/stream",
    json={
        "query": "최신 AI 동향을 알려주세요",
        "thread_id": "user_123"
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

### 3. 피드백 제출

```python
import requests

# 피드백 제출
feedback_response = requests.post(
    "http://localhost:8000/feedback",
    json={
        "thread_id": "user_123",
        "question_count": 1,
        "feedback_scores": {
            "relevance": 5,
            "accuracy": 4,
            "helpfulness": 5
        },
        "comment": "매우 유용한 정보였습니다."
    }
)
```

### 4. 대화 데이터 저장

```python
import requests

# 대화 데이터 저장
conversation_response = requests.post(
    "http://localhost:8000/conversation",
    json={
        "thread_id": "user_123",
        "question_count": 1,
        "user_message": "SPRI AI Brief에서 인공지능 동향에 대해 알려주세요",
        "ai_response": "SPRI AI Brief에 따르면...",
        "used_tools": ["Retriever", "General LLM"],
        "timestamp": "2024-01-01T12:00:00"
    }
)
```

## 🏗️ 아키텍처

### LangServe 통합 구조

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client App    │───▶│  LangServe API   │───▶│  Agentic RAG    │
│                 │    │                  │    │     Chain       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   FastAPI App    │
                       │  (Data Storage)  │
                       └──────────────────┘
```

### 주요 컴포넌트

1. **LangServe Chain** (`langserve_chain.py`)
   - AgenticRAGInput/Output 모델 정의
   - AgenticRAGChain 클래스 구현
   - invoke() 및 stream() 메서드 제공

2. **LangServe Server** (`langserve_server.py`)
   - FastAPI 앱과 LangServe 통합
   - 데이터 저장 및 관리 엔드포인트
   - CORS 미들웨어 설정

3. **실행 스크립트** (`run_langserve_server.py`)
   - 서버 실행 및 설정

## 🔍 LangServe의 장점

### 1. 자동 API 생성
- LangChain 체인을 자동으로 REST API로 변환
- Swagger UI 자동 생성
- 타입 안전성 보장

### 2. 스트리밍 지원
- 실시간 스트리밍 응답
- 청크 단위 데이터 전송
- 사용자 경험 향상

### 3. 피드백 시스템
- 자동 피드백 엔드포인트 생성
- LangSmith 통합
- 모델 성능 모니터링

### 4. 확장성
- 마이크로서비스 아키텍처 지원
- 컨테이너화 가능
- 로드 밸런싱 지원

## 🚀 배포 옵션

### 1. 로컬 실행
```bash
python run_langserve_server.py
```

### 2. Docker 배포
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_langserve.txt .
RUN pip install -r requirements_langserve.txt

COPY . .
EXPOSE 8000

CMD ["python", "run_langserve_server.py"]
```

### 3. 클라우드 배포
- AWS Lambda
- Google Cloud Run
- Azure Container Instances
- Kubernetes

## 🔧 설정 옵션

### 환경 변수
```env
# LangServe 설정
LANGCHAIN_API_KEY=your_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=Agentic RAG System

# OpenAI 설정
OPENAI_API_KEY=your_openai_key

# Tavily 설정
TAVILY_API_KEY=your_tavily_key

# 서버 설정
HOST=0.0.0.0
PORT=8000
```

### 서버 설정
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8000,
    reload=True,
    log_level="info"
)
```

## 📊 모니터링

### LangSmith 통합
- 자동 추적 및 로깅
- 성능 메트릭 수집
- 디버깅 지원

### 로그 레벨
- INFO: 일반 정보
- DEBUG: 디버깅 정보
- ERROR: 오류 정보

## 🛠️ 개발 가이드

### 새로운 엔드포인트 추가
```python
@app.post("/custom-endpoint")
async def custom_endpoint(data: CustomModel):
    # 커스텀 로직
    return {"result": "success"}
```

### 체인 수정
```python
# langserve_chain.py에서 체인 로직 수정
def invoke(self, input_data: AgenticRAGInput) -> AgenticRAGOutput:
    # 수정된 로직
    pass
```

## 🐛 문제 해결

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 다른 포트 사용
   uvicorn.run(app, port=8001)
   ```

2. **의존성 오류**
   ```bash
   # 의존성 재설치
   pip install -r requirements_langserve.txt --force-reinstall
   ```

3. **환경 변수 오류**
   ```bash
   # .env 파일 확인
   cat .env
   ```

## 📚 추가 자료

- [LangServe 공식 문서](https://python.langchain.com/docs/langserve)
- [LangChain 공식 문서](https://python.langchain.com/docs)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)

## 🤝 기여

버그 리포트나 기능 요청은 GitHub Issues를 통해 제출해주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
