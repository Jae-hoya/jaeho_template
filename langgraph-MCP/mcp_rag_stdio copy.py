from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from mcp.server.fastmcp import FastMCP

import sys
import builtins

from dotenv import load_dotenv
load_dotenv(override=True)

# # stdout 보호 (STDIO 통신을 위해 필수!)
# _real_print = builtins.print
# def print(*a, **k):
#     k.setdefault("file", sys.stderr)
#     return _real_print(*a, **k)
# builtins.print = print

mcp = FastMCP(
    "Retriever",
    instructions="A Retriever that can retrieve information from the database. Database is for Langchain, Langgraph.",
)

# 서버 시작 전에 FAISS 로드 (메인 스레드에서!)
async def _faiss_db():
    _embeddings = OllamaEmbeddings(model="bge-m3")
    _faiss_db = FAISS.load_local(
        "LANGCHAIN_DB_INDEX",
        embeddings=_embeddings,
        allow_dangerous_deserialization=True
    )
    return _faiss_db

@mcp.tool()
async def retrieve(query: str) -> str:
    """
    Retrieves information from the document database based on the query.

    Args:
        query (str): The search query to find relevant information

    Returns:
        str: Concatenated text content from all retrieved documents
    """    

    
    # 직접 검색 (간단하게!)
    docs = _faiss_db.invoke(query, k=3)
    result = "\n\n".join([doc.page_content for doc in docs])
    
    return result

if __name__ == "__main__":
    print("MCP RAG server (STDIO) running...")
    mcp.run(transport="stdio")
