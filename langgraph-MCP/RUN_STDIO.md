# stdio 실행하기 - 빠른 가이드

## 🚫 문제: Jupyter에서 stdio가 작동하지 않는 이유

**오류 메시지:**
```
io.UnsupportedOperation: fileno
```

**원인:**
- Jupyter 노트북의 `sys.stderr`는 진짜 파일이 아닙니다
- subprocess stdio 통신은 실제 파일 디스크립터가 필요합니다
- **해결 불가능**: Jupyter에서는 근본적으로 stdio를 사용할 수 없습니다

---

## ✅ 해결 방법

### 🎯 방법 1: Python 스크립트로 실행 (stdio 사용)

#### 단계 1: 터미널 열기
- VS Code: `Ctrl + `` (백틱)
- 또는 외부 PowerShell/CMD

#### 단계 2: 가상환경 활성화
```bash
# 가상환경이 있다면
# .venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux
```

#### 단계 3: 스크립트 실행
```bash
cd c:\Users\skyop\jaeho_template\langgraph-MCP

# 간단한 연결 테스트
python mcp_stdio_simple.py

# 또는 전체 기능 테스트 (LangGraph 포함)
python mcp_stdio_working.py
```

---

### 🌐 방법 2: Jupyter에서 SSE 사용

stdio 대신 SSE transport를 사용하면 Jupyter에서도 작동합니다!

#### 단계 1: 별도 터미널에서 MCP 서버 실행
```bash
python mcp_server_remote.py
```

#### 단계 2: Jupyter 노트북에서 SSE 클라이언트 사용
```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# SSE transport - Jupyter에서 작동! ✅
client = MultiServerMCPClient(
    {
        "document-retriever": {
            "url": "http://localhost:8102/sse",
            "transport": "sse",  # 이것이 핵심!
        }
    }
)

# 나머지는 동일
tools = await client.get_tools()
agent = create_react_agent(model, tools)

# 질문하기
async for chunk in agent.astream(
    {"messages": [{"role": "user", "content": "Hello!"}]},
    stream_mode="values"
):
    if "messages" in chunk and chunk["messages"]:
        print(chunk["messages"][-1].content)
```

---

## 📊 비교

| 항목 | stdio (Python 스크립트) | SSE (Jupyter 가능) |
|-----|------------------------|-------------------|
| Jupyter 지원 | ❌ 불가능 | ✅ 가능 |
| 별도 서버 필요 | ❌ | ✅ |
| 설정 | 간단 | 중간 |
| 추천 | CLI 도구, 배포 | 개발, 실험 |

---

## 🎬 지금 바로 시작하기

### stdio를 써보고 싶다면:
```bash
python mcp_stdio_simple.py
```

### Jupyter에서 계속 작업하고 싶다면:
1. 새 터미널: `python mcp_server_remote.py`
2. Jupyter: SSE 코드 사용 (위 참조)

---

## 💡 핵심 요약

**stdio는 Jupyter에서 절대 작동하지 않습니다!**
- ✅ 해결책 1: 일반 Python 스크립트 사용
- ✅ 해결책 2: SSE transport로 변경

두 방법 모두 정상적으로 작동하며, 기능은 동일합니다.

