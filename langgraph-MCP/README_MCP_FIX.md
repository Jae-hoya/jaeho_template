# MCP 클라이언트 수정 버전

이 디렉토리에는 MCP (Model Context Protocol) 클라이언트의 수정된 버전들이 포함되어 있습니다.

## 문제점 및 해결책

### 원본 코드의 문제점:
1. **모델명 오타**: `gpt-4.1-mini` → `gpt-4o-mini`로 수정
2. **경로 문제**: 상대경로 `./mcp_rag_stdio.py` → 절대경로로 수정
3. **오류 처리 부족**: MCP 서버 연결 실패 시 예외 처리 추가
4. **복잡한 설정**: 너무 많은 MCP 서버 설정으로 인한 불안정성

### 해결책:
1. **올바른 모델명 사용**
2. **강화된 오류 처리**
3. **단계별 설정 검증**
4. **사용자 친화적인 인터페이스**

## 파일 설명

### 1. `mcp_client_smithery_fixed.py` (권장)
- **개선된 MCP 클라이언트**
- 강화된 오류 처리
- 단계별 설정 검증
- 사용자 친화적인 메시지
- MCP 서버와 기본 도구 모두 지원

### 2. `mcp_client_simple.py`
- **간단한 버전**
- MCP 없이 기본 도구만 사용
- Tavily 검색 도구 포함
- 초보자에게 적합

### 3. `mcp_client_smithery.py` (수정됨)
- **원본 코드의 수정 버전**
- 기본적인 오류 처리 추가
- 모델명 수정

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements_mcp.txt
```

### 2. 환경 변수 설정
`.env` 파일을 생성하고 다음을 추가:
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### 3. 실행 방법

#### 개선된 버전 (권장):
```bash
python mcp_client_smithery_fixed.py
```

#### 간단한 버전:
```bash
python mcp_client_simple.py
```

#### 수정된 원본 버전:
```bash
python mcp_client_smithery.py
```

## MCP 서버 설정

### Document Retriever MCP 서버
- 파일: `mcp_rag_stdio.py`
- 기능: 문서 검색 및 RAG
- 전송 방식: stdio

### LangChain Dev Docs MCP 서버
- URL: `https://teddynote.io/mcp/langchain/sse`
- 기능: LangChain 문서 검색
- 전송 방식: SSE (Server-Sent Events)

## 문제 해결

### 1. MCP 클라이언트 연결 오류
- MCP 서버가 실행 중인지 확인
- 네트워크 연결 상태 확인
- API 키가 올바르게 설정되었는지 확인

### 2. Tavily 검색 오류
- Tavily API 키 설정 확인
- 인터넷 연결 상태 확인

### 3. LLM 모델 오류
- OpenAI API 키 설정 확인
- 모델명이 올바른지 확인 (`gpt-4o-mini`)

## 사용 예시

```python
# 기본 질문
"안녕하세요! 오늘 날씨는 어떤가요?"

# 문서 검색 질문 (MCP 서버가 연결된 경우)
"LangChain에 대해 알려주세요."

# 뉴스 검색 질문
"최신 AI 뉴스를 찾아주세요."
```

## 추가 정보

- 모든 응답은 한국어로 제공됩니다
- 'quit', 'exit', '종료'를 입력하면 프로그램이 종료됩니다
- Ctrl+C로도 프로그램을 중단할 수 있습니다

## 지원

문제가 발생하면 다음을 확인하세요:
1. 환경 변수 설정
2. 인터넷 연결
3. API 키 유효성
4. 패키지 설치 상태
