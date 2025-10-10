from mcp import ClientSession
from mcp.client.sse import sse_client
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from utils import astream_graph
from dotenv import load_dotenv
import sys
import os
import asyncio

load_dotenv(override=True)

# 올바른 모델 이름 사용 (gpt-4o-mini 또는 gpt-4-turbo)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# SSE 클라이언트를 사용하여 서버와 통신
async def main():
    print("[INFO] MCP 서버 연결 중...")
    print("[INFO] 서버 URL: http://localhost:8101/sse")
    
    try:
        # SSE 서버에 연결
        async with sse_client("http://localhost:8101/sse") as (read, write):
            print("[SUCCESS] MCP 서버 연결 성공!")
            
            # 클라이언트 세션 생성
            async with ClientSession(read, write) as session:
                print("[INFO] 세션 초기화 중...")
                # 연결 초기화
                await session.initialize()
                print("[SUCCESS] 세션 초기화 완료!")

                # MCP 도구 로드
                print("[INFO] MCP 도구 로드 중...")
                tools = await load_mcp_tools(session)
                print(f"[SUCCESS] 로드된 도구 개수: {len(tools)}")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description[:50]}...")

                # 에이전트 생성
                print("[INFO] 에이전트 생성 중...")
                agent = create_react_agent(model, tools)
                print("[SUCCESS] 에이전트 생성 완료!")

                # 에이전트 응답 스트리밍
                print("\n" + "="*60)
                print("[AGENT] 에이전트 실행 시작...")
                print("="*60 + "\n")
                await astream_graph(agent, {"messages": "DNA 서열 예측에서 최고 성능 개수는?"})
                print("\n" + "="*60)
                print("[SUCCESS] 에이전트 실행 완료!")
                print("="*60)
                
    except Exception as e:
        print(f"[ERROR] 에러 발생: {type(e).__name__}")
        print(f"[ERROR] 에러 메시지: {str(e)}")
        import traceback
        traceback.print_exc()

# 비동기 함수 실행
if __name__ == "__main__":
    # Windows 환경에서 이벤트 루프 정책 설정
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    asyncio.run(main())

