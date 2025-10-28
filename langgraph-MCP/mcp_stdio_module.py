"""
Jupyter에서 import해서 사용할 수 있는 모듈 형태
하지만 주의: stdio는 여전히 작동하지 않습니다!
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(override=True)


def create_stdio_client():
    """stdio 클라이언트 생성"""
    return MultiServerMCPClient(
        {
            "server-sequential-thinking": {
                "command": "cmd" if os.name == "nt" else "bash",
                "args": [
                    "/c" if os.name == "nt" else "-c",
                    "npx -y @smithery/cli@latest run @smithery-ai/server-sequential-thinking "
                    "--key 92f8aa68-b8c4-4053-94ee-63d4d0d90992 "
                    "--profile allied-bird-lzqFcM",
                ],
                "transport": "stdio",
            },
            "desktop-commander": {
                "command": "cmd" if os.name == "nt" else "bash",
                "args": [
                    "/c" if os.name == "nt" else "-c",
                    "npx -y @smithery/cli@latest run @wonderwhy-er/desktop-commander "
                    "--key 92f8aa68-b8c4-4053-94ee-63d4d0d90992",
                ],
                "transport": "stdio",
            },
            "RAG-tool":{
            "url": "http://localhost:8102/sse",
            "transport": "sse"
        }
        }
    )


async def get_mcp_tools_stdio():
    """MCP stdio 도구 가져오기 - 하지만 Jupyter에서는 작동하지 않음!"""
    client = create_stdio_client()
    tools = await client.get_tools()
    return tools, client


def create_sse_client(url="http://localhost:8102/sse"):
    """SSE 클라이언트 생성 - Jupyter에서 작동! ✅"""
    return MultiServerMCPClient(
        {
            "document-retriever": {
                "url": url,
                "transport": "sse",
            }
        }
    )


async def get_mcp_tools_sse(url="http://localhost:8102/sse"):
    """MCP SSE 도구 가져오기 - Jupyter에서 작동! ✅"""
    client = create_sse_client(url)
    tools = await client.get_tools()
    return tools, client


async def create_mcp_agent(transport="sse", url="http://localhost:8102/sse", model_name="gpt-4o-mini"):
    """
    MCP 에이전트 생성
    
    Args:
        transport: "stdio" 또는 "sse"
        url: SSE 서버 URL (transport="sse"일 때만 사용)
        model_name: 사용할 LLM 모델
    
    Returns:
        agent, client, tools
    """
    model = ChatOpenAI(model=model_name, temperature=0)
    
    if transport == "sse":
        tools, client = await get_mcp_tools_sse(url)
        print(f"✅ SSE 연결 성공! 도구 {len(tools)}개 로드됨")
    else:
        tools, client = await get_mcp_tools_stdio()
        print(f"✅ stdio 연결 성공! 도구 {len(tools)}개 로드됨")
    
    agent = create_react_agent(model, tools)
    
    return agent, client, tools


async def demo_tool_calling(agent, query):
    """
    에이전트가 도구를 호출하는 과정을 시연
    
    Args:
        agent: create_mcp_agent로 생성된 에이전트
        query: 질문/작업 내용
    
    Returns:
        최종 답변과 호출된 도구 목록
    """
    print(f"\n{'='*70}")
    print(f"📝 질문: {query}")
    print("="*70)
    
    tool_calls_made = []
    final_answer = None
    
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": query}]},
        stream_mode="updates"
    ):
        for node_name, node_data in chunk.items():
            if node_name == "agent":
                messages = node_data.get("messages", [])
                for msg in messages:
                    # 도구 호출 감지
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_name = tc.get("name", "Unknown")
                            tool_args = tc.get("args", {})
                            tool_calls_made.append(tool_name)
                            
                            print(f"\n🔧 도구 호출: {tool_name}")
                            # 인자 표시
                            if tool_args:
                                args_str = str(tool_args)
                                if len(args_str) > 100:
                                    args_str = args_str[:100] + "..."
                                print(f"   📋 인자: {args_str}")
                    
                    # 최종 응답
                    if hasattr(msg, "content") and msg.content and not hasattr(msg, "tool_calls"):
                        final_answer = msg.content
            
            elif node_name == "tools":
                messages = node_data.get("messages", [])
                for msg in messages:
                    if hasattr(msg, "content") and msg.content:
                        result = msg.content
                        if len(result) > 150:
                            result = result[:150] + "..."
                        print(f"   ✅ 결과: {result}")
    
    # 요약
    print("\n" + "-"*70)
    print(f"📊 호출된 도구: {', '.join(tool_calls_made) if tool_calls_made else '없음'}")
    if final_answer:
        print(f"\n💡 최종 답변:\n{final_answer}")
    print("-"*70)
    
    return {
        "answer": final_answer,
        "tools_called": tool_calls_made
    }

