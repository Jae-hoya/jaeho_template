# Troubleshooting and Setup Notes

This project uses FastMCP with STDIO transport. Claude Desktop runs servers in an isolated process, so the `command`, `args`, and `env` fields must be explicit and correct.

## 1) Final Claude Desktop Config
Location (Windows): `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "seoul-culture-events": {
      "command": "C:\\Users\\skyop\\jaeho_template\\dotenv_windows\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\skyop\\jaeho_template\\11.VibeCoding_for_Agent\\05.MCP_Server\\04.OPENAPI_MCP_Server\\src\\server.py"
      ],
      "env": {
        "SEOUL_API_KEY": "4e4666566e73656c38314a4e4d6345",
        "SEOUL_API_BASE_URL": "http://openapi.seoul.go.kr:8088",
        "SEOUL_API_SERVICE": "culturalEventInfo",
        "SEOUL_API_TYPE": "json",
        "SEOUL_API_TIMEOUT_SECONDS": "10"
      }
    }
  }
}
```

Notes:
- This exact config is also stored in `.mcp_example.json`.
- If you prefer a single entrypoint that ensures `src` is on `sys.path`, use `.mcp_example_run_server.json` instead.
- After editing the config, fully quit Claude Desktop and start it again.

## 2) run_server.py (clear entrypoint)
`run_server.py` is a thin wrapper that adds `src` to `sys.path` and starts the FastMCP server. Use this if you want a single clear entrypoint during local testing.

Run it directly with the venv Python:
```bash
C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\04.OPENAPI_MCP_Server\run_server.py
```

## 3) Common Errors and Fixes

### Claude Desktop does not show tools
- Make sure the config JSON is valid.
- Verify the `command` and `args` paths are absolute and use double backslashes.
- Restart Claude Desktop completely.

### ModuleNotFoundError: fastmcp
- You are not using the venv Python. Ensure the `command` in config points to:
  `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe`

### SEOUL_API_KEY is required
- The server does not read your shell env in Claude Desktop.
- Ensure the `env` block in the config includes `SEOUL_API_KEY`.

### HTTP 401/403 or empty results
- Confirm the API key is valid and active.
- Confirm `SEOUL_API_SERVICE` is `culturalEventInfo` and `SEOUL_API_TYPE` is `json`.

### Server starts but returns empty data
- `start_index` and `end_index` might be out of range.
- Try `start_index=1`, `end_index=5` to verify data.

## 4) OpenCode MCP Registration
OpenCode reads MCP servers from `opencode.json`.

Add a server entry like this (use your real API key):
```json
{
  "mcp": {
    "seoul-culture-events": {
      "type": "local",
      "command": [
        "C:\\Users\\skyop\\jaeho_template\\dotenv_windows\\Scripts\\python.exe",
        "C:\\Users\\skyop\\jaeho_template\\11.VibeCoding_for_Agent\\05.MCP_Server\\04.OPENAPI_MCP_Server\\src\\server.py"
      ],
      "enabled": true
    }
  }
}
```

Notes:
- If you use `.mcp_example_run_server.json`, swap the `args` path to `run_server.py`.
- OpenCode will inherit your shell env, so you can set `SEOUL_API_KEY` in your environment or hardcode it in `command` by switching to a wrapper script.

## 5) Claude Code MCP Registration
Claude Code uses `claude mcp add` to register a local STDIO server.

Example (explicit env):
```bash
claude mcp add seoul-culture-events \
  -e SEOUL_API_KEY=YOUR_SEOUL_API_KEY \
  -e SEOUL_API_BASE_URL=http://openapi.seoul.go.kr:8088 \
  -e SEOUL_API_SERVICE=culturalEventInfo \
  -e SEOUL_API_TYPE=json \
  -e SEOUL_API_TIMEOUT_SECONDS=10 \
  -- C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe \
  C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\04.OPENAPI_MCP_Server\src\server.py
```

Notes:
- You can swap the script path to `run_server.py` if you prefer a single entrypoint.
- If you see "Claude Code CLI not found", ensure `claude --version` works.
