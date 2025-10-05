from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from utils import astream_graph
# command 위치가 맞는지 확인하려면, 실제 파이썬 인터프리터 경로가 "../.dotenv/bin/python"이 맞는지 확인해야 합니다.
# 예를 들어, 윈도우 환경에서는 보통 "python" 또는 "python.exe" 경로가 다를 수 있습니다.
# 아래처럼 sys.executable을 사용하면 현재 실행 중인 파이썬 경로를 쓸 수 있습니다.
from dotenv import load_dotenv
load_dotenv(override=True)


model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)


import sys

server_params = StdioServerParameters(
    command=sys.executable,  # 현재 파이썬 인터프리터 경로 사용
    args=["mcp_server_local(stdio).py"],
)

# StdIO 클라이언트를 사용하여 서버와 통신
async def main():
    # # Windows 권장: Proactor 이벤트 루프
    # if sys.platform == "win32":
    #     try:
    #         asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    #     except Exception:
    #         pass
    
    async with stdio_client(server_params) as (read, write):
        # 클라이언트 세션 생성
        async with ClientSession(read, write) as session:
            # 연결 초기화
            await session.initialize()

            # MCP 도구 로드
            tools = await load_mcp_tools(session)
            print(tools)

            # 에이전트 생성
            agent = create_react_agent(model, tools)

            # 에이전트 응답 스트리밍
            await astream_graph(agent, {"messages": "jaeho"})

# 비동기 함수 실행
import asyncio
asyncio.run(main())