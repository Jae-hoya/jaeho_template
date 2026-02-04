# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""{{ cookiecutter.project_domain }} MCP Server implementation."""

from loguru import logger
from mcp.server.fastmcp import FastMCP

# Create the FastMCP server instance
mcp = FastMCP(
    name="{{ cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') }}",
    instructions="{{ cookiecutter.instructions }}",
)


@mcp.tool()
def example_tool(query: str) -> str:
    """Example tool that returns a greeting.

    Args:
        query: The input query string

    Returns:
        A greeting message with the query
    """
    logger.info(f"Example tool called with query: {query}")
    return f"Hello! You asked: {query}"


@mcp.tool()
def math_tool(operation: str, a: int | float, b: int | float) -> int | float:
    """Perform basic mathematical operations.

    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First number
        b: Second number

    Returns:
        The result of the operation

    Raises:
        ValueError: If the operation is invalid or division by zero
    """
    logger.info(f"Math tool called: {operation}({a}, {b})")

    match operation:
        case "add":
            return a + b
        case "subtract":
            return a - b
        case "multiply":
            return a * b
        case "divide":
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
        case _:
            raise ValueError(f"Invalid operation: {operation}")


def main() -> None:
    """Main entry point for the MCP server."""
    # Demonstrate logging levels
    logger.trace("This is a trace message")
    logger.debug("This is a debug message")
    logger.info("Starting {{ cookiecutter.project_domain }} MCP server")
    logger.success("Server initialized successfully")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()
