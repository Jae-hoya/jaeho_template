import asyncio
import sys
from decimal import Decimal, InvalidOperation, getcontext

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

SERVER_NAME = "calculate-mcp-server"
getcontext().prec = 50


def log_debug(message: str) -> None:
    print(f"[debug] {message}", file=sys.stderr, flush=True)


def to_decimal(value: object) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"Invalid number: {value}") from exc


def format_decimal(value: Decimal) -> str:
    return format(value, "f")


server = Server(SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="subtract",
            description="Subtract two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Minuend"},
                    "b": {"type": "number", "description": "Subtrahend"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="multiply",
            description="Multiply two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First factor"},
                    "b": {"type": "number", "description": "Second factor"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="divide",
            description="Divide two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Dividend"},
                    "b": {"type": "number", "description": "Divisor"},
                },
                "required": ["a", "b"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name not in {"add", "subtract", "multiply", "divide"}:
        raise ValueError(f"Unknown tool: {name}")

    a = to_decimal(arguments.get("a"))
    b = to_decimal(arguments.get("b"))
    log_debug(f"{name} input: a={a}, b={b}")

    if name == "add":
        result = a + b
    elif name == "subtract":
        result = a - b
    elif name == "multiply":
        result = a * b
    else:
        if b == 0:
            log_debug("divide error: division by zero")
            raise ValueError("Division by zero")
        result = a / b

    formatted = format_decimal(result)
    log_debug(f"{name} result: {formatted}")
    return [TextContent(type="text", text=formatted)]


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
