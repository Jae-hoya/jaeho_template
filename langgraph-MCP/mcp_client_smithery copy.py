import asyncio
import sys

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

from dotenv import load_dotenv
load_dotenv(override=True)

async def main():
    # LLM 모델 초기화
    model = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    # 1. 클라이언트 생성 (Smithery MCP 서버들) - 단계별로 테스트
    client_config = {}
    
    # Node.js가 설치되어 있는지 확인
    import subprocess
    try:
        subprocess.run(["node", "--version"], check=True, capture_output=True)
        print("✓ Node.js가 설치되어 있습니다")
        
        # Sequential Thinking 서버 추가
        client_config["server-sequential-thinking"] = {
            "command": "cmd",
            "args": [
                "/c",
                "npx",
                "-y",
                "@smithery/cli@latest",
                "run",
                "@smithery-ai/server-sequential-thinking",
                "--key",
                "92f8aa68-b8c4-4053-94ee-63d4d0d90992",
                "--profile",
                "allied-bird-lzqFcM"
            ],
            "transport": "stdio"
        }
        print("✓ Sequential Thinking 서버 설정됨")
        
        # Desktop Commander 서버 추가
        client_config["desktop-commander"] = {
            "command": "cmd",
            "args": [
                "/c",
                "npx",
                "-y",
                "@smithery/cli@latest",
                "run",
                "@wonderwhy-er/desktop-commander",
                "--key",
                "92f8aa68-b8c4-4053-94ee-63d4d0d90992"
            ],
            "transport": "stdio"
        }
        print("✓ Desktop Commander 서버 설정됨")
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Node.js가 설치되지 않았거나 npx를 찾을 수 없습니다")
        print("Node.js를 설치하거나 다른 MCP 서버만 사용하세요")
    
    # 로컬 Python 서버 추가 (파일 존재 확인)
    import os
    rag_server_path = "./mcp_rag_stdio.py"
    if os.path.exists(rag_server_path):
        client_config["document-retriever"] = {
            "command": sys.executable,  # Windows에서는 python 명령어 사용
            "args": [rag_server_path],
            "transport": "stdio",
        }
        print("✓ Document Retriever 서버 설정됨")
    else:
        print(f"⚠ {rag_server_path} 파일을 찾을 수 없습니다")
    
    if not client_config:
        print("❌ 사용 가능한 MCP 서버가 없습니다. 기본 도구만 사용합니다.")
        client = None
    else:
        client = MultiServerMCPClient(client_config)

    try:
        # 2. MCP 도구 목록 받아오기
        tools = []
        if client:
            try:
                tools = await client.get_tools()
                print(f"✓ MCP 도구 {len(tools)}개 로드됨")
            except Exception as e:
                print(f"⚠ MCP 도구 로드 실패: {e}")
                tools = []
        else:
            print("⚠ MCP 클라이언트가 없어 기본 도구만 사용합니다")
        
        # 3. Tavily 검색 도구 추가
        try:
            tavily = TavilySearch(max_result=3, topic="news", days=7)
            tools_with_tavily = tools + [tavily]
            print("✓ Tavily 검색 도구 추가됨")
        except Exception as e:
            print(f"⚠ Tavily 도구 추가 실패: {e}")
            tools_with_tavily = tools
        
        print(f"\n총 사용 가능한 도구: {len(tools_with_tavily)}개")
        for i, tool in enumerate(tools_with_tavily, 1):
            print(f"{i}. {tool.name}: {tool.description}")

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
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
