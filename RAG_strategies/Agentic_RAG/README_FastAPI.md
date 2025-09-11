# Agentic RAG System with FastAPI

이 프로젝트는 Streamlit과 FastAPI를 결합한 Agentic RAG 시스템입니다.

## 🚀 시작하기

### 1. 의존성 설치

```bash
pip install -r requirements_fastapi.txt
```

### 2. FastAPI 서버 실행

```bash
python run_fastapi_server.py
```

또는

```bash
python fastapi_server.py
```

```bash
uvicorn fastapi_server:app --reload
```

서버가 실행되면:
- **서버 주소**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

### 3. Streamlit 앱 실행

새 터미널에서:

```bash
streamlit run fast_main.py
```

## 📡 API 엔드포인트

### 피드백 관련
- `POST /feedback` - 피드백 제출
- `GET /feedback` - 모든 피드백 조회
- `GET /feedback/{thread_id}` - 특정 스레드 피드백 조회

### 대화 관련
- `POST /conversation` - 단일 대화 저장
- `POST /conversation/thread` - thread_id별 대화 저장
- `POST /conversation/batch` - 배치 대화 저장
- `GET /conversation` - 모든 대화 조회
- `GET /conversation/{thread_id}` - 특정 스레드 대화 조회

### 세션 관련
- `POST /session/summary` - 세션 요약 저장

## 📁 데이터 저장

### 피드백 데이터
- **위치**: `feedback_data/` 폴더
- **형식**: `feedback_YYYYMMDD_HHMMSS.json`

### 대화 데이터
- **위치**: `conversation_data/` 폴더
- **형식**: 
  - 개별: `conversation_YYYYMMDD_HHMMSS.json`
  - 스레드별: `thread_{thread_id_8자리}_YYYYMMDD_HHMMSS.json`
  - 배치: `batch_conversation_YYYYMMDD_HHMMSS.json`
  - 세션 요약: `session_summary_YYYYMMDD_HHMMSS.json`

## 🔧 주요 기능

### 1. 비동기 처리
- FastAPI의 BackgroundTasks를 사용한 비동기 데이터 저장
- ThreadPoolExecutor를 사용한 비동기 HTTP 요청

### 2. 스레드별 대화 관리
- 각 대화 세션마다 고유한 thread_id 생성
- 같은 thread_id의 대화는 하나의 파일에 누적 저장

### 3. 피드백 시스템
- 5번째 질문마다 자동으로 피드백 요청
- LangSmith와 FastAPI 서버에 동시 전송

### 4. 세션 요약
- 대화 세션 종료 시 자동으로 요약 정보 저장

### 5. 에이전트 도구 추적
- 사용된 도구 정보를 대화 데이터에 포함
- Retriever, Researcher, Coder, General LLM 등

## 🛠️ 개발 모드

개발 중에는 `run_fastapi_server.py`를 사용하면 자동 재시작 기능이 활성화됩니다.

```bash
python run_fastapi_server.py
```

## 📊 모니터링

FastAPI 서버의 로그를 통해 다음을 확인할 수 있습니다:
- 피드백 전송 상태
- 대화 저장 상태
- 에러 발생 상황

## 🔍 문제 해결

### FastAPI 서버 연결 오류
1. 서버가 실행 중인지 확인: http://localhost:8000
2. 포트 8000이 사용 중인지 확인
3. 방화벽 설정 확인

### 데이터 저장 오류
1. `feedback_data/`, `conversation_data/` 폴더 권한 확인
2. 디스크 공간 확인
3. JSON 파일 형식 오류 확인

## 📝 참고사항

- 모든 API 요청은 비동기로 처리되어 사용자 경험을 향상시킵니다
- 데이터는 JSON 형식으로 저장되며 UTF-8 인코딩을 사용합니다
- 타임스탬프는 ISO 8601 형식으로 저장됩니다
- `stream_main.py`는 기존 버전으로 그대로 유지됩니다
- `fast_main.py`는 FastAPI 기능이 추가된 새로운 버전입니다
