# PRD2.md 구현 수정 사항 (fix.md)

## 개요
Playwright MCP + Context7 MCP를 동시에 지원하는 Python CLI 클라이언트 구현 및 OpenAI API 전환

---

## 1. MCP 클라이언트 수정 (`src/mcp_client.py`)

### 문제점
- 기존 `stdio_client`가 async context manager인데 `await`로 직접 호출하려고 함
- Context7Client 클래스가 없음

### 수정 내용

```python
# Before (잘못된 방식)
self.stdio_transport = await stdio_client(server_params)

# After (올바른 방식)
self._stdio_context = stdio_client(server_params)
read_stream, write_stream = await self._stdio_context.__aenter__()

self._session_context = ClientSession(read_stream, write_stream)
self.session = await self._session_context.__aenter__()
```

### 추가된 Context7Client 클래스
```python
class Context7Client:
    """MCP Client for connecting to Context7 MCP Server via SSE/HTTP"""
    DEFAULT_URL = "https://mcp.context7.com/mcp"

    async def connect(self):
        self._http_context = streamablehttp_client(self.server_url)
        read_stream, write_stream, _ = await self._http_context.__aenter__()
        # ...
```

### 정리 로직 개선
```python
async def close(self):
    try:
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
    except Exception:
        pass  # Ignore cleanup errors
```

---

## 2. OpenAI API 전환 (`src/claude_agent.py`)

### 변경 이유
- 사용자가 OpenAI API Key를 사용하려고 함
- Anthropic SDK → OpenAI SDK로 변경 필요

### 수정 내용

```python
# Before
from anthropic import Anthropic
self.client = Anthropic(api_key=api_key)
response = self.client.messages.create(...)

# After
from openai import OpenAI
self.client = OpenAI(api_key=api_key)
response = self.client.chat.completions.create(...)
```

### Tool 포맷 변환 함수 추가
```python
def convert_to_openai_tools(mcp_tools):
    """MCP tool 포맷을 OpenAI function calling 포맷으로 변환"""
    return [{
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool.get("input_schema", {})
        }
    } for tool in mcp_tools]
```

### 응답 처리 방식 변경
```python
# Anthropic 방식
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            # ...

# OpenAI 방식
if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
```

---

## 3. 메인 애플리케이션 수정 (`src/main.py`)

### 추가된 UnifiedToolExecutor 클래스
```python
class UnifiedToolExecutor:
    """Tool 호출을 적절한 MCP 클라이언트로 라우팅"""

    def register_playwright_client(self, client):
        self.playwright_tools = {tool["name"] for tool in client.available_tools}

    def register_context7_client(self, client):
        self.context7_tools = {tool["name"] for tool in client.available_tools}

    async def execute(self, tool_name, arguments):
        if tool_name in self.playwright_tools:
            return await self.playwright_client.call_tool(tool_name, arguments)
        elif tool_name in self.context7_tools:
            return await self.context7_client.call_tool(tool_name, arguments)
```

### 환경변수 변경
```python
# Before
api_key = os.getenv("ANTHROPIC_API_KEY")

# After
api_key = os.getenv("OPENAI_API_KEY")
```

### EOF 에러 처리 추가
```python
except EOFError:
    print("\nNo input available. Exiting...")
    break
```

---

## 4. 환경 설정 수정 (`.env`)

### 문제점
- Playwright MCP 패키지명이 잘못됨: `@modelcontextprotocol/server-playwright` (존재하지 않음)

### 수정
```bash
# Before (잘못된 패키지명)
MCP_SERVER_ARGS=-y,@modelcontextprotocol/server-playwright

# After (올바른 패키지명)
MCP_SERVER_ARGS=-y,@playwright/mcp
```

---

## 5. 시스템 프롬프트 업데이트 (`src/claude_agent.py`)

### 추가된 내용
```
### 2. Context7 Tools (Library Documentation)
- **resolve-library-id**: Find the correct library ID for a package/library name
- **get-library-docs**: Get documentation and code examples for a library

**Important**: When looking up library documentation:
1. First use `resolve-library-id` to find the correct library ID
2. Then use `get-library-docs` with the resolved ID to get documentation
```

---

## 6. 테스트 파일 추가

### `test_mcp_connection.py`
- MCP 연결 단독 테스트용

### `test_integration.py`
- Playwright + Context7 통합 테스트
- OpenAI API를 통한 도구 호출 테스트

---

## 검증 결과

```
============================================================
Context7 Integration Test
============================================================

[1] Connecting to Playwright MCP...
    Found 22 tools

[2] Connecting to Context7 MCP...
    Found 2 tools (resolve-library-id, query-docs)

[3] Total tools: 24

[4] Testing Context7: 'Find React hooks documentation'
    - resolve-library-id → Success
    - query-docs → Success

============================================================
Test completed successfully!
============================================================
```

---

## 수정된 파일 목록

| 파일 | 변경 내용 |
|------|----------|
| `src/mcp_client.py` | Context7Client 추가, async context manager 수정 |
| `src/claude_agent.py` | Anthropic → OpenAI 전환, tool 포맷 변환 |
| `src/main.py` | UnifiedToolExecutor 추가, 다중 클라이언트 통합 |
| `.env` | `@playwright/mcp` 패키지명 수정 |
| `.env.example` | OPENAI_API_KEY, CONTEXT7_MCP_URL 추가 |
| `tests/test_mcp_client.py` | Context7Client 테스트 추가 |
