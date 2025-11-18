from retriever import QdrantRetrieverFactory
from mcp.server.fastmcp import FastMCP

import sys
import builtins

from dotenv import load_dotenv
load_dotenv(override=True)


mcp = FastMCP(
    "Retriever",
    instructions="A Retriever that can retrieve information from the database. Database is for SPRI AI Brief",
)

# Qdrant vectorstore 전역 초기화
_qs_factory = QdrantRetrieverFactory()
_qs_vectorstore = _qs_factory._get_vectorstore(collection_name="RAG_Example(RAG_strategies)")

@mcp.tool()
async def retrieve(query: str) -> str:
    """
    Retrieves information from the document database based on the query.

    This function creates a retriever, queries it with the provided input,
    and returns the concatenated content of all retrieved documents.

    Args:
        query (str): The search query to find relevant information

    Returns:
        str: Concatenated text content from all retrieved documents
    """
    # ✅ VectorStore 직접 사용 (래퍼 없이!)
    retrieved_docs = await _qs_vectorstore.asimilarity_search(query, k=3)
    result = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    return result

if __name__ == "__main__":
    # Run the MCP server with stdio transport for integration with MCP clients
    mcp.run(transport="stdio")

# 이 mcp tool을 확장하고 싶어.
# 에를들면,
# 1. expansion query를 만든다
# 2. MCP가 알아서 모델의 temperature를 수정하면서, 최적의 temperature에서 검색한다..
# 3. retriever 방식을 수정한다



# from retriever import QdrantRetrieverFactory
# from mcp.server.fastmcp import FastMCP

# import sys
# import builtins

# from dotenv import load_dotenv
# load_dotenv(override=True)


# mcp = FastMCP(
#     "Retriever",
#     instructions="A Retriever that can retrieve information from the database. Database is for SPRI AI Brief",
# )

# # Qdrant vectorstore 전역 초기화

# _qs_factory = QdrantRetrieverFactory()
# _qdrant_vs = _qs_factory._get_vectorstore(collection_name="RAG_Example(RAG_strategies)")


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
    
#     # # vectorstore 직접 사용 (retriever 거치지 않음)
#     # retrieved_docs = _qdrant_vs.ainvoke(query, k=3)    
#     # vectorstore 직접 사용 (asimilarity_search 사용!)
#     retrieved_docs = await _qdrant_vs.asimilarity_search(query, k=3)
    
#     print(f"[DEBUG] Found {len(retrieved_docs)} docs")
#     result = "\n\n".join([doc.page_content for doc in retrieved_docs])
#     print(f"[DEBUG] Returning {len(result)} chars")
    
#     return result

# if __name__ == "__main__":
#     # Run the MCP server with stdio transport for integration with MCP clients
#     mcp.run(transport="stdio")

# # 이 mcp tool을 확장하고 싶어.
# # 에를들면,
# # 1. expansion query를 만든다
# # 2. MCP가 알아서 모델의 temperature를 수정하면서, 최적의 temperature에서 검색한다..
# # 3. retriever 방식을 수정한다