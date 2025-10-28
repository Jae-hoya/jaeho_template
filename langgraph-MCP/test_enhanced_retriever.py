"""
Enhanced Retriever MCP Tool 테스트 스크립트

이 스크립트는 확장된 retriever의 다양한 기능을 테스트합니다.
"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_basic_search():
    """기본 검색 테스트"""
    print("\n=== 테스트 1: 기본 검색 ===")
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_rag_sse.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "retrieve",
                arguments={
                    "query": "인공지능 기술 동향",
                    "use_expansion": False,
                    "retriever_mode": "basic",
                    "fetch_k": 3
                }
            )
            
            print("검색 결과:")
            print(result.content[0].text[:500] + "...")  # 처음 500자만 출력


async def test_query_expansion():
    """쿼리 확장 테스트"""
    print("\n=== 테스트 2: 쿼리 확장 검색 ===")
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_rag_sse.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "retrieve",
                arguments={
                    "query": "AI 윤리",
                    "use_expansion": True,
                    "temperature": 0.7,
                    "retriever_mode": "basic",
                    "fetch_k": 5
                }
            )
            
            print("검색 결과 (쿼리 확장 사용):")
            print(result.content[0].text[:500] + "...")


async def test_compression_mode():
    """압축 모드 (Reranking) 테스트"""
    print("\n=== 테스트 3: 압축 모드 + 쿼리 확장 ===")
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_rag_sse.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "retrieve",
                arguments={
                    "query": "머신러닝 활용 사례",
                    "use_expansion": True,
                    "temperature": 0.5,
                    "retriever_mode": "compression",
                    "fetch_k": 20,
                    "top_n": 5
                }
            )
            
            print("검색 결과 (압축 모드 + 쿼리 확장):")
            print(result.content[0].text[:500] + "...")


async def test_creative_expansion():
    """창의적 쿼리 확장 테스트"""
    print("\n=== 테스트 4: 창의적 쿼리 확장 (높은 temperature) ===")
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_rag_sse.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "retrieve",
                arguments={
                    "query": "생성형 AI",
                    "use_expansion": True,
                    "temperature": 0.9,  # 높은 창의성
                    "retriever_mode": "basic",
                    "fetch_k": 5
                }
            )
            
            print("검색 결과 (창의적 확장):")
            print(result.content[0].text[:500] + "...")


async def main():
    """모든 테스트 실행"""
    print("=" * 60)
    print("Enhanced Retriever MCP Tool 테스트")
    print("=" * 60)
    
    try:
        await test_basic_search()
        await asyncio.sleep(2)
        
        await test_query_expansion()
        await asyncio.sleep(2)
        
        await test_compression_mode()
        await asyncio.sleep(2)
        
        await test_creative_expansion()
        
        print("\n" + "=" * 60)
        print("모든 테스트 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Windows에서 ProactorEventLoop 사용 문제 해결
    if asyncio.get_event_loop_policy().__class__.__name__ == 'WindowsProactorEventLoopPolicy':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())


