# MCP stdio Transport 사용 가이드

## 문제 상황

Jupyter 노트북에서 stdio transport를 사용하려고 할 때 다음과 같은 오류가 발생합니다:

```
UnsupportedOperation: fileno
```

## 원인

- **Jupyter 노트북의 제한**: Jupyter의 `sys.stderr`/`sys.stdout`은 실제 파일 객체가 아닙니다
- **stdio의 요구사항**: subprocess stdio 통신은 실제 파일 디스크립터(`fileno()`)가 필요합니다
- **근본적 충돌**: Jupyter 환경에서는 이를 제공할 수 없습니다

## 해결 방법

### 방법 1: Python 스크립트로 실행 (권장)

stdio transport는 **일반 Python 스크립트**에서만 작동합니다.

#### 1-1. 간단한 연결 테스트
```bash
python mcp_stdio_simple.py
```

#### 1-2. 전체 기능 테스트 (LangGraph 에이전트 포함)
```bash
python mcp_stdio_working.py
```

### 방법 2: SSE Transport 사용 (Jupyter에서 가능)

Jupyter 노트북에서 MCP를 사용하려면 **SSE transport**를 사용하세요.

#### 2-1. MCP 서버를 먼저 실행 (별도 터미널)
```bash
python mcp_server_remote.py
```

#### 2-2. Jupyter 노트북에서 SSE 클라이언트 사용
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# SSE transport 사용 (Jupyter에서 작동!)
client = MultiServerMCPClient(
    {
        "document-retriever": {
            "url": "http://localhost:8102/sse",
            "transport": "sse",
        }
    }
)

# 이후는 동일하게 사용
tools = await client.get_tools()
agent = create_react_agent(model, tools)
```

## 비교표

| 항목 | stdio | SSE |
|-----|-------|-----|
| **Jupyter 지원** | ❌ 불가능 | ✅ 가능 |
| **별도 서버 필요** | ❌ 불필요 | ✅ 필요 |
| **설정 복잡도** | 낮음 | 중간 |
| **권장 환경** | Python 스크립트 | Jupyter/Colab |

## 빠른 시작

### stdio를 사용하고 싶다면:
```bash
# 터미널에서 실행
cd c:\Users\skyop\jaeho_template\langgraph-MCP
python mcp_stdio_simple.py
```

### Jupyter에서 사용하고 싶다면:
```bash
# 터미널 1: 서버 실행
python mcp_server_remote.py

# 터미널 2 또는 Jupyter: 클라이언트 실행 (SSE 사용)
```

## 주의사항

1. **stdio는 Jupyter에서 절대 작동하지 않습니다**
   - `run_coro_in_thread`를 사용해도 근본적으로 해결되지 않습니다
   - 반드시 일반 Python 스크립트로 실행해야 합니다

2. **Windows 환경**
   - `command: "cmd"`, `args: ["/c", ...]` 사용
   - PowerShell을 사용하려면 `command: "powershell.exe"` 설정

3. **환경변수 확인**
   - `.env` 파일에 OpenAI API 키가 설정되어 있는지 확인
   - `load_dotenv()`가 호출되는지 확인

## 문제 해결

### 오류: "The operation completed successfully"
- Windows에서 정상 작동 중임을 나타내는 메시지입니다 (무시 가능)

### 오류: "npx not found"
- Node.js가 설치되어 있지 않거나 PATH에 없습니다
- Node.js를 설치하고 재시작하세요

### 오류: "Connection refused"
- SSE 서버가 실행되지 않았습니다
- `python mcp_server_remote.py`를 먼저 실행하세요

