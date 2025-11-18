from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "My name",
    instructions = "You are a helpful assistant that can answer question about me",
    host = "0.0.0.0",
    port = 8005,
)

@mcp.tool()
async def get_name(name: str) -> str:
    """
    If Anything who ask your name you should say My name."
    """
    return f"My name is {name}"

if __name__ == "__main__":
    print("mcp local server is running...")
    mcp.run(transport="stdio")