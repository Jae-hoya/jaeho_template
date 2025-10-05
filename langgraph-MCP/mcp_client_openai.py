import sys
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from dotenv import load_dotenv
load_dotenv(override=True)

async def main():
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 1. 다중 서버 MCP 클라이언트 생성 (document-retriever는 stdio, langchain-dev-docs는 sse)
    client = MultiServerMCPClient(
        {
            "document-retriever": {
                "command": sys.executable,  # 현재 파이썬 실행 파일 경로
                "args": ["mcp_server_local(stdio).py"],  # mcp_server_rag.py의 경로를 실제 위치로 수정
                "transport": "stdio",
            },
            "langchain-dev-docs": {
                "url": "https://teddynote.io/mcp/langchain/sse",
                "transport": "sse",
            },
            "manse-tool":{
                "url": "http://localhost:8102/sse",
                "transport": "sse"
            }
        }
    )

    # 2. MCP 도구 목록 받아오기
    tools = await client.get_tools()
    
    # 3. Tavily 검색 도구 추가
    tavily = TavilySearch(max_result=3, topic="news", days=7)
    tools_with_tavily = tools + [tavily]
    
    print(f"사용 가능한 도구: {len(tools_with_tavily)}개")
    for tool in tools_with_tavily:
        print(f"- {tool.name}: {tool.description}")

    # 4. LangGraph 에이전트 생성 (한국어 응답 설정)
    prompt = """당신은 도움이 되는 AI 어시스턴트입니다. 
    모든 응답은 한국어로 해주세요. 
    사용자의 질문에 정확하고 유용한 정보를 제공하되, 
    한국어로 자연스럽고 친근하게 답변해주세요."""
    
    agent = create_react_agent(model, tools_with_tavily, prompt=prompt)

    # 5. 에이전트에게 질문하기
    question = input("질문을 입력하세요: ")
    if question:
        response = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
        
        # 응답 구조 확인 및 출력
        print(f"\n응답 타입: {type(response)}")
        print(f"응답 내용: {response}")
        
        # messages가 있는 경우
        if 'messages' in response:
            last_message = response['messages'][-1]
            print(f"\n마지막 메시지 타입: {type(last_message)}")
            print(f"마지막 메시지: {last_message}")
            
            # AIMessage 객체인 경우 content 속성 사용
            if hasattr(last_message, 'content'):
                print(f"\n답변: {last_message.content}")
            else:
                print(f"\n답변: {last_message}")
        else:
            print(f"\n답변: {response}")

if __name__ == "__main__":
    asyncio.run(main())
