from retriever import FAISSRetrieverFactory, QdrantRetrieverFactory
from mcp.server.fastmcp import FastMCP

import asyncio
import sys
import builtins
from dotenv import load_dotenv
load_dotenv(override=True)

# stdout 보호(그대로 유지)
_real_print = builtins.print
def print(*a, **k):
    k.setdefault("file", sys.stderr)
    return _real_print(*a, **k)
builtins.print = print

mcp = FastMCP(
    "Retriever",
    instructions="A Retriever that can retrieve information from the database. Database is for SPRI AI Brief",
)

RETRIEVE_TIMEOUT = 15.0  # 사용 중인 값 유지/조정

@mcp.tool()
async def retrieve(query: str) -> str:
    def _retrieve_sync(q: str) -> str:
        qs = QdrantRetrieverFactory()
        qs_retriever = qs.retriever(collection_name="RAG_Example(RAG_strategies)", fetch_k=3)
        retrieved_docs = qs_retriever.invoke(q)
        return "\n".join([doc.page_content for doc in retrieved_docs])

    try:
        # 빈 입력 보호(간혹 에이전트가 ""로 호출)
        safe_query = query or ""
        result = await asyncio.wait_for(
            asyncio.to_thread(_retrieve_sync, safe_query), # 워커스레드 실행 + 타임아웃 적용
            timeout=RETRIEVE_TIMEOUT, 
        )
        return result
    except Exception as e:
        # 원본 예외를 stderr로만 출력(프로토콜 안전) → 무엇이 터졌는지 확인 가능
        print(f"[retrieve internal error] {type(e).__name__}: {e}", file=sys.stderr, flush=True)
        raise


if __name__ == "__main__":
    mcp.run(transport="stdio")



# from retriever import FAISSRetrieverFactory, QdrantRetrieverFactory
# from mcp.server.fastmcp import FastMCP

# import asyncio
# import sys
# import builtins

# from dotenv import load_dotenv
# load_dotenv(override=True)

# # 핵심: stdout 보호 (반드시 필요!)
# _real_print = builtins.print
# def print(*a, **k):
#     k.setdefault("file", sys.stderr)  # 모든 print를 강제로 stderr로
#     return _real_print(*a, **k)
# builtins.print = print

# mcp = FastMCP(
#     "Retriever",
#     instructions="A Retriever that can retrieve information from the database. Database is for SPRI AI Brief",
# )

# # ✅ 수정 코드 (됨)
# @mcp.tool()
# async def retrieve(query: str) -> str:
#     """
#     Retrieves information from the document database based on the query.

#     This function creates a retriever, queries it with the provided input,
#     and returns the concatenated content of all retrieved documents.

#     Args:
#         query (str): The search query to find relevant information

#     Returns:
#         str: Concatenated text content from all retrieved documents
#     """    
#     def _retrieve_sync(q: str) -> str:
#         qs = QdrantRetrieverFactory()
#         qs_retriever = qs.retriever(collection_name="RAG_Example(RAG_strategies)", fetch_k=3)
#         retrieved_docs = qs_retriever.invoke(q)
#         return "\n".join([doc.page_content for doc in retrieved_docs])
    
#     result = await asyncio.to_thread(_retrieve_sync, query)  # 워커 스레드에서 실행!
#     return result

# if __name__ == "__main__":
#     # Run the MCP server with stdio transport for integration with MCP clients
#     mcp.run(transport="stdio")

# # 요약: stdio에서 가장 중요한 건 stdout 보호입니다. retriever나 langchain 내부에서 print()를 하면 MCP 프로토콜(JSON)이 깨져서 agent가 응답을 받지 못합니다!