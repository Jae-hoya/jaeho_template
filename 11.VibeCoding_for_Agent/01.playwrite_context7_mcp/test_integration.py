"""Integration test script for Playwright + Context7 MCP"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mcp_client import MCPClient, Context7Client
from claude_agent import ClaudeAgent


class UnifiedToolExecutor:
    """Routes tool calls to the appropriate MCP client"""

    def __init__(self):
        self.playwright_tools = set()
        self.context7_tools = set()
        self.playwright_client = None
        self.context7_client = None

    def register_playwright_client(self, client):
        self.playwright_client = client
        self.playwright_tools = {tool["name"] for tool in client.available_tools}

    def register_context7_client(self, client):
        self.context7_client = client
        self.context7_tools = {tool["name"] for tool in client.available_tools}

    async def execute(self, tool_name, arguments):
        if tool_name in self.playwright_tools:
            return await self.playwright_client.call_tool(tool_name, arguments)
        elif tool_name in self.context7_tools:
            return await self.context7_client.call_tool(tool_name, arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")


async def test_context7():
    """Test Context7 MCP - Find React documentation"""
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found")
        return

    print("=" * 60)
    print("Context7 Integration Test")
    print("=" * 60)

    # Initialize clients
    playwright_client = MCPClient("npx", ["-y", "@playwright/mcp"])
    context7_client = Context7Client()
    tool_executor = UnifiedToolExecutor()

    try:
        print("\n[1] Connecting to Playwright MCP...")
        await playwright_client.connect()
        tool_executor.register_playwright_client(playwright_client)
        print(f"    Found {len(playwright_client.available_tools)} tools")

        print("\n[2] Connecting to Context7 MCP...")
        await context7_client.connect()
        tool_executor.register_context7_client(context7_client)
        print(f"    Found {len(context7_client.available_tools)} tools")

        # Print Context7 tool names
        print("\n    Context7 tools:")
        for tool in context7_client.available_tools:
            print(f"      - {tool['name']}")

        # Merge tools
        all_tools = playwright_client.get_tools_for_claude() + context7_client.get_tools_for_claude()
        print(f"\n[3] Total tools: {len(all_tools)}")

        # Initialize agent
        agent = ClaudeAgent(api_key)

        # Test Context7 - Find React documentation
        print("\n[4] Testing Context7: 'Find React hooks documentation'")
        print("-" * 60)

        response = await agent.process_message(
            "Find the React library ID using resolve-library-id tool, then get documentation about React hooks using get-library-docs",
            all_tools,
            tool_executor.execute
        )

        # Truncate for readability and handle encoding
        truncated = response[:1000] if len(response) > 1000 else response
        print(f"\nAssistant Response:\n{truncated.encode('utf-8', errors='replace').decode('utf-8')}...")

        print("\n" + "=" * 60)
        print("Test completed successfully!")
        print("=" * 60)

    finally:
        await playwright_client.close()
        await context7_client.close()


if __name__ == "__main__":
    asyncio.run(test_context7())
