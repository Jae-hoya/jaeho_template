#!/usr/bin/env python3
"""
MCP Server for document retrieval using stdio transport
"""

import asyncio
import json
import sys
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from retriever import FAISSRetrieverFactory, QdrantRetrieverFactory

# MCP 서버 생성
server = Server("document-retriever")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """사용 가능한 도구 목록을 반환합니다."""
    return [
        Tool(
            name="retrieve",
            description="문서 데이터베이스에서 정보를 검색합니다. SPRI AI Brief 데이터베이스를 사용합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색할 쿼리"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """도구를 호출합니다."""
    if name == "retrieve":
        query = arguments.get("query", "")
        if not query:
            return [TextContent(type="text", text="쿼리가 제공되지 않았습니다.")]
        
        try:
            # QdrantRetrieverFactory 사용
            qs = QdrantRetrieverFactory()
            qs_retriever = qs.retriever(collection_name="RAG_Example(RAG_strategies)", fetch_k=3)
            
            # 검색 실행
            retrieved_docs = qs_retriever.invoke(query)
            
            # 결과 결합
            result = "\n".join([doc.page_content for doc in retrieved_docs])
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"검색 중 오류가 발생했습니다: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"알 수 없는 도구: {name}")]

async def main():
    """MCP 서버를 stdio 방식으로 실행합니다."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())










