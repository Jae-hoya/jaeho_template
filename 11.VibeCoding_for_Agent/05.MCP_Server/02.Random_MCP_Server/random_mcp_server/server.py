import asyncio
import random
import sys

from mcp import Tool, stdio_server
from mcp.server import Server
from mcp.types import TextContent

SERVER_NAME = "random-mcp-server"

server = Server(SERVER_NAME, version="0.1.0")


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_random_number",
            description="Generate a random number between 1 and 100.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )
    ]


@server.call_tool()
async def call_tool(name, _arguments):
    if name != "get_random_number":
        raise ValueError(f"Unknown tool: {name}")

    value = random.randint(1, 100)
    print(f"[debug] generated random number: {value}", file=sys.stderr)

    return [TextContent(type="text", text=str(value))]


async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
