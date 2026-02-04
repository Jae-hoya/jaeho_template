# Usage Guide

## 프로젝트 구조

```
playwrite_context7_mcp/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI 진입점
│   ├── mcp_client.py        # MCP 서버 연결 및 tool 관리
│   └── claude_agent.py      # Claude API 통합
├── tests/
│   ├── __init__.py
│   ├── test_mcp_client.py   # MCP 클라이언트 테스트
│   └── test_claude_agent.py # Claude 에이전트 테스트
├── pyproject.toml           # 프로젝트 설정 및 의존성
├── .env.example             # 환경 변수 예시
├── .gitignore
├── README.md
└── PRD.md

## 테스트

pytest를 사용한 테스트 실행:

```bash
pytest
```

상세한 출력과 함께 테스트:

```bash
pytest -v
```

특정 테스트 파일만 실행:

```bash
pytest tests/test_mcp_client.py
```

## 주요 컴포넌트

### MCPClient (src/mcp_client.py)

Playwright MCP 서버와의 stdio 통신을 담당합니다.

주요 메서드:
- `connect()`: MCP 서버에 연결
- `call_tool(tool_name, arguments)`: Tool 실행
- `get_tools_for_claude()`: Claude용 tool 목록 반환
- `close()`: 연결 종료

### ClaudeAgent (src/claude_agent.py)

Claude API와 통합하여 사용자 요청을 처리합니다.

주요 메서드:
- `process_message(user_message, available_tools, tool_executor)`: 메시지 처리
- `reset_conversation()`: 대화 기록 초기화

시스템 프롬프트:
- 웹 자동화 작업에 특화된 프롬프트
- MCP tool 사용 가이드
- 에러 처리 및 피드백 제공

### Main CLI (src/main.py)

대화형 CLI 인터페이스를 제공합니다.

기능:
- MCP 서버 연결
- Claude 에이전트 초기화
- 사용자 입력 처리 루프
- Tool 실행 결과 출력

## 환경 변수

`.env` 파일에서 다음 변수를 설정할 수 있습니다:

```
# 필수
ANTHROPIC_API_KEY=your_api_key_here

# 선택 (기본값 사용 가능)
MCP_SERVER_COMMAND=npx
MCP_SERVER_ARGS=-y,@modelcontextprotocol/server-playwright
```

## 문제 해결

### MCP 서버 연결 실패

1. Node.js가 설치되어 있는지 확인
2. npx 명령어가 작동하는지 확인: `npx --version`
3. Playwright MCP 서버가 정상적으로 실행되는지 확인

### API 키 오류

1. `.env` 파일이 존재하는지 확인
2. `ANTHROPIC_API_KEY`가 올바르게 설정되어 있는지 확인
3. API 키에 충분한 크레딧이 있는지 확인

### Tool 실행 오류

1. Tool 이름과 파라미터가 올바른지 확인
2. MCP 서버가 정상적으로 연결되어 있는지 확인
3. 콘솔 출력에서 에러 메시지 확인

## 개발 가이드

### 새로운 기능 추가

1. `src/` 디렉토리에 모듈 추가
2. 테스트 코드 작성 (`tests/` 디렉토리)
3. README 업데이트
4. 테스트 실행하여 검증

### 코드 스타일

- Python 3.10+ 기능 사용 가능
- Type hints 사용 권장
- 단순하고 읽기 쉬운 코드 작성
- 핵심 기능에 집중 (과도한 추상화 지양)

## 라이선스

이 프로젝트는 교육 및 학습 목적으로 제공됩니다.
