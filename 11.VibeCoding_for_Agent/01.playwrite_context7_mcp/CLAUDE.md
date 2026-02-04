# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python CLI client that connects to two MCP (Model Context Protocol) servers:
- **Playwright MCP**: Web browser automation via stdio
- **Context7 MCP**: Library documentation retrieval via HTTP/SSE

Uses OpenAI GPT-4o (despite file naming referencing "Claude") to process natural language requests and route tool calls to the appropriate MCP server.

## Commands

```bash
# Install dependencies
uv pip install -e .

# Install with dev dependencies
uv pip install -e ".[dev]"

# Run the CLI
python src/main.py

# Run tests
pytest
pytest -v                          # verbose
pytest tests/test_mcp_client.py    # single file
```

## Architecture

```
src/
├── main.py           # CLI entry point, UnifiedToolExecutor for routing
├── mcp_client.py     # MCPClient (stdio) and Context7Client (HTTP/SSE)
└── claude_agent.py   # OpenAI integration with tool execution loop
```

**Key flow**: User input → `ClaudeAgent.process_message()` → OpenAI API → Tool calls → `UnifiedToolExecutor.execute()` → Routes to `MCPClient` or `Context7Client` → Returns result

**UnifiedToolExecutor** (`main.py`): Routes tool calls by maintaining separate tool name sets for each MCP client.

**MCPClient** (`mcp_client.py`): Connects via `stdio_client` to local Playwright MCP server process.

**Context7Client** (`mcp_client.py`): Connects via `streamablehttp_client` to remote Context7 MCP server.

**ClaudeAgent** (`claude_agent.py`): Manages conversation history, converts MCP tools to OpenAI format, executes tool loop until final text response.

## Environment Variables

Required in `.env`:
- `OPENAI_API_KEY`: OpenAI API key

Optional:
- `MCP_SERVER_COMMAND`: Default `npx`
- `MCP_SERVER_ARGS`: Default `-y,@playwright/mcp` (comma-separated)
- `CONTEXT7_MCP_URL`: Default `https://mcp.context7.com/mcp`

## Requirements

- Python 3.10+
- Node.js (for Playwright MCP server via npx)
