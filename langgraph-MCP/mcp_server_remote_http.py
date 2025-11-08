from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "My name",
    instructions = "You are a helpful assistant that can answer question about me",
    port=8101
)

@mcp.tool()
async def get_name(name: str) -> str:
    """
    If Anything who ask your name you should say My name."
    """
    return f"My name is {name}"

if __name__ == "__main__":
    # Print a message indicating the server is starting
    print("mcp remote server is running...")

    # start the server
    mcp.run(transport="streamable-http")
    
    
    