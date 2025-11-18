"""
간단한 MCP 클라이언트 예제 (SSE + STDIO)
(1.MCP_Handon.ipynb 스타일)

사용법:
1. 터미널에서 SSE 서버 시작 (선택): python mcp_rag_sse.py
2. 이 스크립트 실행: python simple_sse_client.py
"""
import asyncio
import sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

async def main():
    print("=" * 80)
    print("Multi-Server MCP 클라이언트 (SSE + STDIO)")
    print("=" * 80)
    
    # 모델 초기화
    model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    print("[OK] Model initialized")
    
    # ✅ 여러 MCP 서버에 동시 연결 (SSE + STDIO)
    client = MultiServerMCPClient(
        {
            # SSE 방식 (HTTP 서버)
            "qdrant_sse": {
                "url": "http://localhost:8102/sse",
                "transport": "streamable_http",
            },
            # STDIO 방식 (로컬 프로세스)
            "qdrant_local": {
                "command": sys.executable,
                "args": ["-u", str(Path("mcp_rag_stdio_qdrant.py").resolve())],
                "transport": "stdio",
            }
        }
    )
    
    # MCP에서 도구를 받아옴
    tools = await client.get_tools()
    print(f"[OK] Tools loaded: {[t.name for t in tools]}")
    
    # 받아온 도구를 LangGraph 에이전트에 연결
    agent = create_react_agent(model, tools)
    print("[OK] Agent created")
    
    # 에이전트가 도구를 활용하여 질문에 답변
    query = "DNA 서열 예측"
    print(f"\n[QUERY] '{query}'")
    print("\n[RESULT]")
    print("-" * 80)
    
    inputs = {"messages": [{"role": "user", "content": query}]}
    
    event_count = 0
    async for event in agent.astream(inputs):
        event_count += 1
        print(f"\n[Event {event_count}]")
        print(event)
    
    print("-" * 80)
    print(f"\n[OK] Complete! ({event_count} events)")

if __name__ == "__main__":
    asyncio.run(main())

