"""
STDIO MCP Qdrant 서버 테스트 스크립트
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(override=True)
# nest_asyncio 적용
try:
    import nest_asyncio
    nest_asyncio.apply()
except:
    pass

os.environ.setdefault("PYTHONUNBUFFERED", "1")

from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

async def test_mcp_qdrant():
    """STDIO MCP Qdrant 서버 테스트"""
    
    # 서버 파일 경로
    server_path = Path("mcp_rag_stdio_qdrant.py").resolve()
    if not server_path.exists():
        print(f"[ERROR] Server file not found: {server_path}")
        return
    
    print(f"[START] MCP server: {server_path}")
    
    # 서버 파라미터 설정
    params = StdioServerParameters(
        command=sys.executable,
        args=["-u", str(server_path)],
        cwd=str(server_path.parent),
        env=os.environ.copy(),
    )
    
    try:
        # stderr 로그 파일 열기
        with open("mcp_stderr.log", "wb") as err_fp:
            print("[CONNECT] MCP client connecting...")
            
            async with stdio_client(params, errlog=err_fp) as (read, write):
                async with ClientSession(read, write) as session:
                    # 세션 초기화
                    await session.initialize()
                    print("[OK] MCP session initialized")
                    
                    # 도구 로드
                    tools = await load_mcp_tools(session)
                    print(f"[OK] Tools loaded: {[t.name for t in tools]}")
                    
                    # Agent 생성
                    model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
                    agent = create_react_agent(model, tools)
                    print("[OK] Agent created")
                    
                    # 쿼리 실행
                    query = "DNA 서열 예측"
                    print(f"\n[QUERY] '{query}'")
                    
                    inputs = {"messages": [HumanMessage(content=query, name="user")]}
                    
                    # 결과 스트리밍
                    print("\n[RESULT]")
                    print("-" * 80)
                    
                    event_count = 0
                    async for event in agent.astream(inputs):
                        event_count += 1
                        print(f"\n[Event {event_count}]")
                        print(event)
                    
                    print("-" * 80)
                    print(f"\n[OK] Test complete! ({event_count} events)")
                    
    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        
        # stderr 로그 출력
        try:
            if Path("mcp_stderr.log").exists():
                with open("mcp_stderr.log", "rb") as f:
                    stderr_data = f.read()
                    tail = stderr_data[-2000:] if len(stderr_data) > 2000 else stderr_data
                    print(f"\n=== Server stderr (last 2000 bytes) ===")
                    print(tail.decode("utf-8", "ignore"))
        except:
            pass
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("STDIO MCP Qdrant 서버 테스트")
    print("=" * 80)
    
    asyncio.run(test_mcp_qdrant())

