from fastmcp import FastMCP
from typing import Optional
import pytz
from datetime import datetime

mcp = FastMCP(
    "Current Time",  # Name of the MCP server
    instructions="Information about the current time in a given timezone",  # Instructions for the LLM on how to use this tool
)


@mcp.tool()
async def who_am_i(name:str) -> str:
    """
    Get information about the user.

    Args: 
        name (str): The name of the user

    Returns:
        str: A string containing the information about the user
    """
    return f"My name is {name}"
    


if __name__ == "__main__":
    # Print a message indicating the server is starting
    print("mcp remote server is running...")

    # start the server
    mcp.run(transport="streamable-http", port=8003)
