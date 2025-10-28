from retriever import FAISSRetrieverFactory, QdrantRetrieverFactory

from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv
load_dotenv(override=True)

mcp = FastMCP(
    "Retriever",
    instructions="A Retriever that can retrieve information from the database. Database is for SPRI AI Brief",
    host="0.0.0.0",
    port=8102,
)

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
    

    qs = QdrantRetrieverFactory()

    qs_retriever = qs.retriever(collection_name="RAG_Example(RAG_strategies)", fetch_k=3)
    # Use the invoke() method to get relevant documents based on the query
    retrieved_docs = qs_retriever.invoke(query)

    # Join all document contents with newlines and return as a single string
    return "\n".join([doc.page_content for doc in retrieved_docs])

if __name__ == "__main__":
    # Run the MCP server with stdio transport for integration with MCP clients
    mcp.run(transport="sse")

# 이 mcp tool을 확장하고 싶어.
# 에를들면,
# 1. expansion query를 만든다
# 2. MCP가 알아서 모델의 temperature를 수정하면서, 최적의 temperature에서 검색한다..
# 3. retriever 방식을 수정한다