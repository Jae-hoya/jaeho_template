import asyncio
import sys
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from dotenv import load_dotenv
load_dotenv(override=True)

async def main():
    """메인 함수 - MCP 클라이언트와 LangGraph 에이전트를 설정하고 실행"""
    
    # LLM 모델 초기화 (올바른 모델명 사용)
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    print("✅ LLM 모델 초기화 완료")

    # MCP 클라이언트 설정
    mcp_servers = {}
    
    # 1. Document Retriever MCP 서버 (로컬)
    if os.path.exists("mcp_rag_stdio.py"):
        mcp_servers["document-retriever"] = {
            "command": sys.executable,
            "args": ["mcp_rag_stdio.py"],
            "transport": "stdio",
            "cwd": "."
        }
        print("✅ Document Retriever MCP 서버 설정 완료")
    else:
        print("⚠️ mcp_rag_stdio.py 파일을 찾을 수 없습니다.")
    
    # 2. LangChain Dev Docs MCP 서버 (SSE)
    mcp_servers["langchain-dev-docs"] = {
        "url": "https://teddynote.io/mcp/langchain/sse",
        "transport": "sse",
    }
    print("✅ LangChain Dev Docs MCP 서버 설정 완료")

    # MCP 클라이언트 생성
    tools = []
    try:
        if mcp_servers:
            client = MultiServerMCPClient(mcp_servers)
            print("✅ MCP 클라이언트 생성 완료")
            
            # MCP 도구 가져오기
            mcp_tools = await client.get_tools()
            tools.extend(mcp_tools)
            print(f"✅ MCP에서 {len(mcp_tools)}개의 도구를 가져왔습니다.")
        else:
            print("⚠️ 사용 가능한 MCP 서버가 없습니다.")
    except Exception as e:
        print(f"❌ MCP 클라이언트 오류: {e}")
        print("기본 도구만 사용합니다.")

    # Tavily 검색 도구 추가
    try:
        tavily = TavilySearch(max_result=3, topic="news", days=7)
        tools.append(tavily)
        print("✅ Tavily 검색 도구 추가 완료")
    except Exception as e:
        print(f"❌ Tavily 도구 오류: {e}")

    # 도구 목록 출력
    print(f"\n📋 사용 가능한 도구: {len(tools)}개")
    for i, tool in enumerate(tools, 1):
        print(f"  {i}. {tool.name}: {tool.description}")

    # LangGraph 에이전트 생성 (한국어 응답 설정)
    prompt = """당신은 도움이 되는 AI 어시스턴트입니다. 
    모든 응답은 한국어로 해주세요. 
    사용자의 질문에 정확하고 유용한 정보를 제공하되, 
    한국어로 자연스럽고 친근하게 답변해주세요."""
    
    try:
        agent = create_react_agent(model, tools, prompt=prompt)
        print("✅ LangGraph 에이전트 생성 완료")
    except Exception as e:
        print(f"❌ 에이전트 생성 오류: {e}")
        return

    # 사용자 질문 받기 및 처리
    print("\n" + "="*50)
    print("🤖 AI 어시스턴트가 준비되었습니다!")
    print("="*50)
    
    while True:
        try:
            question = input("\n💬 질문을 입력하세요 (종료하려면 'quit' 입력): ")
            
            if question.lower() in ['quit', 'exit', '종료']:
                print("👋 안녕히 가세요!")
                break
                
            if not question.strip():
                print("⚠️ 질문을 입력해주세요.")
                continue

            print(f"\n🔍 질문 처리 중: {question}")
            
            # 에이전트 실행
            response = await agent.ainvoke({
                "messages": [{"role": "user", "content": question}]
            })
            
            # 응답 처리 및 출력
            if 'messages' in response and response['messages']:
                last_message = response['messages'][-1]
                
                if hasattr(last_message, 'content'):
                    print(f"\n🤖 답변: {last_message.content}")
                else:
                    print(f"\n🤖 답변: {last_message}")
            else:
                print(f"\n🤖 답변: {response}")
                
        except KeyboardInterrupt:
            print("\n👋 사용자가 중단했습니다. 안녕히 가세요!")
            break
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            print("다시 시도해주세요.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 프로그램이 종료되었습니다.")
    except Exception as e:
        print(f"❌ 프로그램 오류: {e}")
