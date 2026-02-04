import asyncio
import json
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client


class MCPClient:
    """MCP Client for connecting to Playwright MCP Server"""

    def __init__(self, server_command: str, server_args: List[str]):
        self.server_command = server_command
        self.server_args = server_args
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self._stdio_context = None
        self._session_context = None

    async def connect(self):
        """Connect to MCP server via stdio"""
        server_params = StdioServerParameters(
            command=self.server_command,
            args=self.server_args,
            env=None
        )

        # Enter stdio client context
        self._stdio_context = stdio_client(server_params)
        read_stream, write_stream = await self._stdio_context.__aenter__()

        # Enter session context
        self._session_context = ClientSession(read_stream, write_stream)
        self.session = await self._session_context.__aenter__()

        await self.session.initialize()

        # Get available tools
        response = await self.session.list_tools()
        self.available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in response.tools
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        result = await self.session.call_tool(tool_name, arguments)
        return result

    async def close(self):
        """Close the MCP session"""
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors
        try:
            if self._stdio_context:
                await self._stdio_context.__aexit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors

    def get_tools_for_claude(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to Claude function calling format"""
        return self.available_tools


class Context7Client:
    """MCP Client for connecting to Context7 MCP Server via SSE/HTTP"""

    DEFAULT_URL = "https://mcp.context7.com/mcp"

    def __init__(self, server_url: str = None):
        self.server_url = server_url or self.DEFAULT_URL
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Dict[str, Any]] = []
        self._http_context = None
        self._session_context = None

    async def connect(self):
        """Connect to Context7 MCP server via SSE/HTTP"""
        # Enter HTTP client context
        self._http_context = streamablehttp_client(self.server_url)
        read_stream, write_stream, _ = await self._http_context.__aenter__()

        # Enter session context
        self._session_context = ClientSession(read_stream, write_stream)
        self.session = await self._session_context.__aenter__()

        await self.session.initialize()

        # Get available tools
        response = await self.session.list_tools()
        self.available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in response.tools
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool with given arguments"""
        if not self.session:
            raise RuntimeError("Not connected to Context7 MCP server")

        result = await self.session.call_tool(tool_name, arguments)
        return result

    async def close(self):
        """Close the Context7 MCP session"""
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors
        try:
            if self._http_context:
                await self._http_context.__aexit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors

    def get_tools_for_claude(self) -> List[Dict[str, Any]]:
        """Convert MCP tools to Claude function calling format"""
        return self.available_tools
