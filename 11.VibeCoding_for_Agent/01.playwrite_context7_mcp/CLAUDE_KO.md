# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소에서 작업할 때 참고하는 가이드입니다.

## 프로젝트 개요

두 개의 MCP (Model Context Protocol) 서버에 연결하는 Python CLI 클라이언트:
- **Playwright MCP**: stdio를 통한 웹 브라우저 자동화
- **Context7 MCP**: HTTP/SSE를 통한 라이브러리 문서 조회

OpenAI GPT-4o를 사용하여 (파일명에 "Claude"가 있지만 실제로는 OpenAI 사용) 자연어 요청을 처리하고 적절한 MCP 서버로 도구 호출을 라우팅합니다.

## 명령어

```bash
# 의존성 설치
uv pip install -e .

# 개발 의존성 포함 설치
uv pip install -e ".[dev]"

# CLI 실행
python src/main.py

# 테스트 실행
pytest
pytest -v                          # 상세 출력
pytest tests/test_mcp_client.py    # 단일 파일 테스트
```

## 아키텍처

```
src/
├── main.py           # CLI 진입점, 도구 라우팅을 위한 UnifiedToolExecutor
├── mcp_client.py     # MCPClient (stdio) 및 Context7Client (HTTP/SSE)
└── claude_agent.py   # OpenAI 통합 및 도구 실행 루프
```

**핵심 흐름**: 사용자 입력 → `ClaudeAgent.process_message()` → OpenAI API → 도구 호출 → `UnifiedToolExecutor.execute()` → `MCPClient` 또는 `Context7Client`로 라우팅 → 결과 반환

**UnifiedToolExecutor** (`main.py`): 각 MCP 클라이언트별 도구 이름 집합을 유지하여 도구 호출을 라우팅합니다.

**MCPClient** (`mcp_client.py`): `stdio_client`를 통해 로컬 Playwright MCP 서버 프로세스에 연결합니다.

**Context7Client** (`mcp_client.py`): `streamablehttp_client`를 통해 원격 Context7 MCP 서버에 연결합니다.

**ClaudeAgent** (`claude_agent.py`): 대화 기록 관리, MCP 도구를 OpenAI 형식으로 변환, 최종 텍스트 응답까지 도구 루프를 실행합니다.

## 환경 변수

`.env` 파일에 필수:
- `OPENAI_API_KEY`: OpenAI API 키

선택 사항:
- `MCP_SERVER_COMMAND`: 기본값 `npx`
- `MCP_SERVER_ARGS`: 기본값 `-y,@playwright/mcp` (쉼표로 구분)
- `CONTEXT7_MCP_URL`: 기본값 `https://mcp.context7.com/mcp`

## 요구 사항

- Python 3.10+
- Node.js (npx를 통한 Playwright MCP 서버 실행용)
