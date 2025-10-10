from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv(override=True)

import asyncio
import sys
import os
import logging
import builtins

# -------------------------------------------------
# (0) 모든 print를 stderr로 강제하여 STDIO 프로토콜 오염 방지
# -------------------------------------------------
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
_real_print = builtins.print
def print(*a, **k):
    k.setdefault("file", sys.stderr)
    return _real_print(*a, **k)
builtins.print = print

# -------------------------------------------------
# (1) retriever 로컬 모듈 경로 보강(필요할 때만 유지)
# -------------------------------------------------
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retriever import FAISSRetrieverFactory, QdrantRetrieverFactory  # noqa: E402

# -------------------------------------------------
# (2) 설정
# -------------------------------------------------
SERVICE_NAME = "Retriever"
INSTRUCTIONS = "A Retriever that can retrieve information from the database. Database is for SPRI AI Brief"
COLLECTION = "RAG_Example(RAG_strategies)"
FETCH_K = 3
MAX_CHARS = 50_000
RETRIEVE_TIMEOUT = 15.0  # seconds

mcp = FastMCP(SERVICE_NAME, instructions=INSTRUCTIONS)

def log_debug(msg: str) -> None:
    logging.info(msg)  # stderr로만

# 헬스체크용 간단 툴(선택)
@mcp.tool()
async def ping(msg: str = "ok") -> str:
    return f"pong:{msg}"

@mcp.tool()
async def retrieve(query: str) -> str:
    """
    Args:
        query: 검색 질의
    Returns:
        str: 결과 텍스트(최대 MAX_CHARS)
    """
    log_debug(f"retrieve() 호출 - query: {query!r}")

    def _retrieve_sync(q: str) -> str:
        # 동기 I/O는 여기에 모읍니다(워커 스레드에서 실행됨).
        log_debug("QdrantRetrieverFactory 생성")
        qs = QdrantRetrieverFactory()

        log_debug(f"Retriever 생성 (collection={COLLECTION}, k={FETCH_K})")
        retr = qs.retriever(collection_name=COLLECTION, fetch_k=FETCH_K)

        log_debug("문서 검색 실행(retr.invoke)")
        docs = retr.invoke(q)  # 동기 호출

        log_debug(f"문서 {len(docs)}개")
        text = "\n".join((getattr(d, "page_content", "") or "") for d in docs).strip()
        return text or "(no results)"

    try:
        # (3) 블로킹 호출을 워커 스레드로, (4) 타임아웃 적용
        result = await asyncio.wait_for(asyncio.to_thread(_retrieve_sync, query), timeout=RETRIEVE_TIMEOUT)

        # (5) STDIO 전송 과대 방지
        if len(result) > MAX_CHARS:
            result = result[:MAX_CHARS] + "\n...[truncated]"

        log_debug(f"retrieve() 완료 - 길이={len(result)}")
        return result

    except asyncio.TimeoutError:
        log_debug("retrieve() 타임아웃")
        return "[retrieve error] Timeout: backend took too long"

    except Exception as e:
        # 예외는 항상 '짧은 문자열'로 반환(표준출력은 MCP payload!)
        log_debug(f"retrieve() 예외: {type(e).__name__}: {e}")
        return f"[retrieve error] {type(e).__name__}: {e}"

if __name__ == "__main__":
    # STDIO 모드: 클라이언트는 반드시 stdio_client/ClientSession으로 붙어야 합니다.
    mcp.run(transport="stdio")


# from retriever import FAISSRetrieverFactory, QdrantRetrieverFactory

# from mcp.server.fastmcp import FastMCP

# from dotenv import load_dotenv
# load_dotenv(override=True)

# mcp = FastMCP(
#     "Retriever",
#     instructions="A Retriever that can retrieve information from the database. Database is for SPRI AI Brief",
# )

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
    

#     qs = QdrantRetrieverFactory()

#     qs_retriever = qs.retriever(collection_name="RAG_Example(RAG_strategies)", fetch_k=3)
#     # Use the invoke() method to get relevant documents based on the query
#     retrieved_docs = qs_retriever.invoke(query)

#     # Join all document contents with newlines and return as a single string
#     return "\n".join([doc.page_content for doc in retrieved_docs])

# if __name__ == "__main__":
#     # Run the MCP server with stdio transport for integration with MCP clients
#     mcp.run(transport="stdio")

####################

# _real_print = builtins.print
# def print(*a, **k):
#     k.setdefault("file", sys.stderr)  # 모든 print를 강제로 stderr로
#     return _real_print(*a, **k)
# builtins.print = print
# stdio 통신 구조:
# ┌─────────────┐  stdout (MCP JSON) ─┐
# │ MCP Server  │                      │
# │ (stdio)     │  stderr (로그만)     │
# └─────────────┘                      ▼
#                               ┌──────────────┐
#                               │ MCP Client   │
#                               │ (stdio_client)│
#                               └──────────────┘

# ❌ 문제: stdout에 로그나 print가 섞이면 JSON이 깨짐!
# ✅ 해결: 모든 출력을 stderr로 강제