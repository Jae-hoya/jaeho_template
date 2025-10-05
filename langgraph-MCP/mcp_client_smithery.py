import asyncio
import os
import sys
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from dotenv import load_dotenv
load_dotenv(override=True)

async def main():
    # LLM 모델 초기화
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 1. 클라이언트 생성 (MCP 서버들)
    try:
        client = MultiServerMCPClient(
            {
                "document-retriever": {
                    "command": sys.executable,
                    # "args": ["mcp_rag_stdio.py"],
                    "args": [os.path.join(os.path.dirname(__file__), "mcp_rag_stdio.py")],
                    
                    "transport": "stdio",
                    
                },
                "langchain-dev-docs": {
                    # SSE 서버가 실행 중인지 확인하세요
                    "url": "https://teddynote.io/mcp/langchain/sse",
                    # SSE(Server-Sent Events) 방식으로 통신
                    "transport": "sse",
                },
            }
        )
    except Exception as e:
        print(f"MCP 클라이언트 생성 중 오류 발생: {e}")
        print("기본 도구만 사용합니다.")
        client = None

    # 2. MCP 도구 목록 받아오기
    if client:
        try:
            tools = await client.get_tools()
            print(f"MCP에서 {len(tools)}개의 도구를 가져왔습니다.")
        except Exception as e:
            print(f"MCP 도구 가져오기 중 오류 발생: {e}")
            tools = []
    else:
        tools = []
    
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


