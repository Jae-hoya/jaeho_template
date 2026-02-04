import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.mcp_client import MCPClient, Context7Client


@pytest.fixture
def mcp_client():
    return MCPClient("npx", ["-y", "@modelcontextprotocol/server-playwright"])


@pytest.fixture
def context7_client():
    return Context7Client()


# MCPClient Tests
@pytest.mark.asyncio
async def test_mcp_client_initialization(mcp_client):
    """Test MCP client initialization"""
    assert mcp_client.server_command == "npx"
    assert mcp_client.server_args == ["-y", "@modelcontextprotocol/server-playwright"]
    assert mcp_client.session is None
    assert mcp_client.available_tools == []


@pytest.mark.asyncio
async def test_get_tools_for_claude(mcp_client):
    """Test getting tools in Claude format"""
    mcp_client.available_tools = [
        {
            "name": "test_tool",
            "description": "Test tool description",
            "input_schema": {"type": "object"}
        }
    ]

    tools = mcp_client.get_tools_for_claude()
    assert len(tools) == 1
    assert tools[0]["name"] == "test_tool"
    assert tools[0]["description"] == "Test tool description"


@pytest.mark.asyncio
async def test_call_tool_without_connection(mcp_client):
    """Test calling tool without connection raises error"""
    with pytest.raises(RuntimeError, match="Not connected to MCP server"):
        await mcp_client.call_tool("test_tool", {})


# Context7Client Tests
@pytest.mark.asyncio
async def test_context7_client_initialization(context7_client):
    """Test Context7 client initialization with default URL"""
    assert context7_client.server_url == "https://mcp.context7.com/mcp"
    assert context7_client.session is None
    assert context7_client.available_tools == []


@pytest.mark.asyncio
async def test_context7_client_custom_url():
    """Test Context7 client initialization with custom URL"""
    custom_url = "https://custom.context7.com/mcp"
    client = Context7Client(custom_url)
    assert client.server_url == custom_url


@pytest.mark.asyncio
async def test_context7_get_tools_for_claude(context7_client):
    """Test getting Context7 tools in Claude format"""
    context7_client.available_tools = [
        {
            "name": "resolve-library-id",
            "description": "Resolve library ID",
            "input_schema": {"type": "object"}
        },
        {
            "name": "get-library-docs",
            "description": "Get library docs",
            "input_schema": {"type": "object"}
        }
    ]

    tools = context7_client.get_tools_for_claude()
    assert len(tools) == 2
    assert tools[0]["name"] == "resolve-library-id"
    assert tools[1]["name"] == "get-library-docs"


@pytest.mark.asyncio
async def test_context7_call_tool_without_connection(context7_client):
    """Test calling Context7 tool without connection raises error"""
    with pytest.raises(RuntimeError, match="Not connected to Context7 MCP server"):
        await context7_client.call_tool("resolve-library-id", {})
