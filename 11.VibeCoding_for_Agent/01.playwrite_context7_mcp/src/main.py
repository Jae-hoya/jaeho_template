import asyncio
import os
import sys
from typing import Any, Dict, Set
from dotenv import load_dotenv

from mcp_client import MCPClient, Context7Client
from claude_agent import ClaudeAgent


class UnifiedToolExecutor:
    """Routes tool calls to the appropriate MCP client"""

    def __init__(self):
        self.playwright_tools: Set[str] = set()
        self.context7_tools: Set[str] = set()
        self.playwright_client: MCPClient = None
        self.context7_client: Context7Client = None

    def register_playwright_client(self, client: MCPClient):
        self.playwright_client = client
        self.playwright_tools = {tool["name"] for tool in client.available_tools}

    def register_context7_client(self, client: Context7Client):
        self.context7_client = client
        self.context7_tools = {tool["name"] for tool in client.available_tools}

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute tool by routing to the appropriate client"""
        if tool_name in self.playwright_tools:
            return await self.playwright_client.call_tool(tool_name, arguments)
        elif tool_name in self.context7_tools:
            return await self.context7_client.call_tool(tool_name, arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")


async def main():
    """Main CLI function"""
    # Load environment variables
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment")
        sys.exit(1)

    # Playwright MCP settings
    server_command = os.getenv("MCP_SERVER_COMMAND", "npx")
    server_args_str = os.getenv("MCP_SERVER_ARGS", "-y,@modelcontextprotocol/server-playwright")
    server_args = server_args_str.split(",")

    # Context7 MCP settings
    context7_url = os.getenv("CONTEXT7_MCP_URL", Context7Client.DEFAULT_URL)

    print("Playwright + Context7 MCP Client")
    print("=" * 50)

    # Initialize clients
    playwright_client = MCPClient(server_command, server_args)
    context7_client = Context7Client(context7_url)
    tool_executor = UnifiedToolExecutor()

    try:
        # Connect to Playwright MCP
        print(f"\nConnecting to Playwright MCP: {server_command} {' '.join(server_args)}")
        await playwright_client.connect()
        tool_executor.register_playwright_client(playwright_client)
        print(f"  -> Found {len(playwright_client.available_tools)} Playwright tools")

        # Connect to Context7 MCP
        print(f"\nConnecting to Context7 MCP: {context7_url}")
        await context7_client.connect()
        tool_executor.register_context7_client(context7_client)
        print(f"  -> Found {len(context7_client.available_tools)} Context7 tools")

        # Merge all tools
        all_tools = playwright_client.get_tools_for_claude() + context7_client.get_tools_for_claude()
        total_tools = len(all_tools)
        print(f"\nTotal available tools: {total_tools}")

        # Initialize Claude agent
        agent = ClaudeAgent(api_key)

        # CLI loop
        print("\n" + "=" * 50)
        print("Ready! Type your requests below (or 'quit' to exit)")
        print("=" * 50 + "\n")

        while True:
            try:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nGoodbye!")
                    break

                if user_input.lower() == "reset":
                    agent.reset_conversation()
                    print("\nConversation reset!")
                    continue

                # Process message with Claude using merged tools
                response = await agent.process_message(
                    user_input,
                    all_tools,
                    tool_executor.execute
                )

                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                print("\nNo input available. Exiting...")
                break
            except Exception as e:
                print(f"\nError: {str(e)}\n")

    finally:
        await playwright_client.close()
        await context7_client.close()


if __name__ == "__main__":
    asyncio.run(main())
