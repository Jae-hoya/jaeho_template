"""Simple test script to verify MCP connection"""
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_playwright_mcp():
    print("Testing Playwright MCP connection...")

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@playwright/mcp"],
        env=None
    )

    print("Starting stdio client...")
    async with stdio_client(server_params) as (read_stream, write_stream):
        print("Creating session...")
        async with ClientSession(read_stream, write_stream) as session:
            print("Initializing session...")
            await session.initialize()

            print("Getting tools...")
            response = await session.list_tools()
            print(f"Found {len(response.tools)} tools:")
            for tool in response.tools[:5]:
                print(f"  - {tool.name}")
            if len(response.tools) > 5:
                print(f"  ... and {len(response.tools) - 5} more")


if __name__ == "__main__":
    asyncio.run(test_playwright_mcp())
