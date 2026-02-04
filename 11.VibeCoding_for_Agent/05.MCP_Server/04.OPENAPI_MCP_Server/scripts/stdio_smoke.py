import asyncio
import os
import sys

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


async def main() -> None:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    src_path = os.path.join(repo_root, "src")
    env = os.environ.copy()
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{existing}" if existing else src_path
    )

    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "seoul_culture_mcp.server"],
        env=env,
        cwd=repo_root,
    )

    async with Client(transport) as client:
        result = await client.call_tool(
            "get_cultural_events", {"start_index": 1, "end_index": 1}
        )
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
