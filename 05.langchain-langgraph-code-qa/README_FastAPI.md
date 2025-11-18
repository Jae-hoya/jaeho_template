# LangGraph 코드 어시스턴트 - FastAPI 연동 (개선된 버전)

이 프로젝트는 LangGraph 코드 어시스턴트에 FastAPI 피드백 서버를 연동한 버전입니다. **모든 대화가 FastAPI로 전송되며, 비동기 처리를 통해 성능과 안정성을 향상시켰습니다.**

## 🚀 설치 및 실행

### 1. FastAPI 서버 실행

```bash
# FastAPI 서버 실행 (권장)
uvicorn fastapi_server:app --reload --host 0.0.0.0 --port 8000
```

또는 스크립트로 실행:
```bash
python run_fastapi_server.py
```

### 2. Streamlit 앱 실행

```bash
# Streamlit 앱 실행
cd modules
streamlit run main.py
```

## 📋 API 엔드포인트

### 대화 저장
- **POST** `/conversation` - 모든 대화 내용을 서버로 전송
- **GET** `/conversation` - 모든 대화 데이터 조회
- **GET** `/conversation/{thread_id}` - 특정 스레드의 대화 조회

### 피드백 제출
- **POST** `/feedback` - 피드백 데이터를 서버로 전송
- **GET** `/feedback` - 모든 피드백 조회
- **GET** `/feedback/{thread_id}` - 특정 스레드의 피드백 조회

## 🔧 설정

### FastAPI 서버 URL 변경
`modules/main.py` 파일에서 `FASTAPI_SERVER_URL` 변수를 수정하세요:

```python
FASTAPI_SERVER_URL = "http://localhost:8000"  # 기본값
```

## 📊 데이터 구조

### 대화 데이터
```json
{
  "thread_id": "사용자 세션 ID",
  "question_count": 5,
  "user_message": "사용자 질문",
  "ai_response": "AI 답변",
  "timestamp": "2024-01-01T12:00:00"
}
```

### 피드백 데이터
```json
{
  "thread_id": "사용자 세션 ID",
  "question_count": 5,
  "feedback_scores": {
    "올바른 답변": 5,
    "도움됨": 4,
    "구체성": 5
  },
  "comment": "사용자 의견 (선택사항)",
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🎯 주요 기능

### 1. **모든 대화 저장**
- 사용자의 모든 질문과 AI 답변이 FastAPI 서버로 전송됩니다
- 비동기 처리로 성능 저하 없이 백그라운드에서 저장

### 2. **5번째 질문마다 피드백 수집**
- 사용자가 5번째 질문을 할 때마다 자동으로 피드백 폼이 표시됩니다

### 3. **비동기 처리로 성능 향상**
- **BackgroundTasks**: FastAPI의 BackgroundTasks를 사용하여 비동기 처리
- **ThreadPoolExecutor**: Streamlit에서 비동기 HTTP 요청 처리
- **Non-blocking**: 사용자 경험을 방해하지 않는 백그라운드 처리

### 4. **이중 피드백 전송**
- LangSmith로 피드백 전송 (기존 기능)
- FastAPI 서버로 피드백 전송 (새로운 기능)

### 5. **데이터 저장**
- 메모리와 JSON 파일에 데이터 저장
- 대화 데이터: `conversation_data/` 폴더
- 피드백 데이터: `feedback_data/` 폴더

### 6. **API 문서**
- http://localhost:8000/docs 에서 자동 생성된 API 문서 확인

## 🛠️ 기술적 개선사항

### FastAPI 서버
- **BackgroundTasks**: 비동기 백그라운드 작업 처리
- **ThreadPoolExecutor**: 파일 I/O 작업을 별도 스레드에서 처리
- **에러 처리**: 각 단계별 예외 처리 및 로깅

### Streamlit 클라이언트
- **ThreadPoolExecutor**: 비동기 HTTP 요청 처리
- **Non-blocking 전송**: 사용자 인터페이스 블로킹 방지
- **타임아웃 설정**: 네트워크 요청 타임아웃으로 안정성 향상

## 📁 파일 구조

```
fastcampus-code-qa_copy/
├── fastapi_server.py          # FastAPI 서버 메인 파일 (개선됨)
├── run_fastapi_server.py      # 서버 실행 스크립트
├── requirements_fastapi.txt   # FastAPI 관련 패키지 (업데이트됨)
├── modules/
│   └── main.py               # Streamlit 앱 (비동기 처리 추가)
├── conversation_data/        # 대화 데이터 저장 폴더 (자동 생성)
└── feedback_data/           # 피드백 데이터 저장 폴더 (자동 생성)
```

## 🔍 문제 해결

### FastAPI 서버 연결 오류
1. FastAPI 서버가 실행 중인지 확인
2. 포트 8000이 사용 가능한지 확인
3. 방화벽 설정 확인

### 비동기 처리 문제
1. ThreadPoolExecutor가 정상적으로 초기화되었는지 확인
2. 네트워크 연결 상태 확인
3. 서버 로그에서 백그라운드 작업 오류 확인

### 성능 최적화
1. 스레드 풀 크기 조정 (현재 5개 워커)
2. 타임아웃 설정 조정 (현재 5초)
3. 배치 처리로 여러 요청을 묶어서 전송

## 🚀 성능 특징

- **비동기 처리**: 모든 HTTP 요청이 백그라운드에서 처리
- **Non-blocking**: 사용자 인터페이스가 블로킹되지 않음
- **확장성**: ThreadPoolExecutor로 동시 요청 처리 가능
- **안정성**: 타임아웃과 예외 처리로 안정적인 서비스 제공
