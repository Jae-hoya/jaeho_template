"""
간단한 MCP stdio transport 예제

실행 방법:
    python mcp_stdio_simple.py
"""

import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import os

load_dotenv(override=True)


async def test_stdio():
    """간단한 stdio 연결 테스트"""
    
    # Windows용 설정
    client = MultiServerMCPClient(
        {
            "sequential-thinking": {
                "command": "cmd",
                "args": [
                    "/c",
                    "npx", "-y", "@smithery/cli@latest", "run",
                    "@smithery-ai/server-sequential-thinking",
                    "--key", "92f8aa68-b8c4-4053-94ee-63d4d0d90992",
                    "--profile", "allied-bird-lzqFcM",
                ],
                "transport": "stdio",
            },
        }
    )
    
    print("🔄 서버 연결 중...\n")
    
    try:
        # 도구 목록 가져오기
        tools = await client.get_tools()
        
        print("✅ 연결 성공!")
        print(f"\n📦 사용 가능한 도구 개수: {len(tools)}")
        print("\n도구 목록:")
        for i, tool in enumerate(tools[:10], 1):  # 처음 10개만
            print(f"  {i}. {tool.name}")
        
        if len(tools) > 10:
            print(f"  ... 외 {len(tools) - 10}개")
            
    except Exception as e:
        print(f"❌ 오류: {type(e).__name__}")
        print(f"   {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_stdio())

