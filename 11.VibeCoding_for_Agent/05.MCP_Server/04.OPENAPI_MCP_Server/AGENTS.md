# AGENTS.md

Purpose
- This file orients agentic coding tools to this repo: how to run, test, and follow the local coding style.

Project summary
- FastMCP (STDIO) server that exposes Seoul cultural events via MCP tools.
- Python package name: `seoul_culture_mcp` (underscore).
- Entry points: `src/seoul_culture_mcp/server.py` and `run_server.py`.

External rules
- Cursor rules: none found (`.cursor/rules/`, `.cursorrules`).
- Copilot rules: none found (`.github/copilot-instructions.md`).

Key paths
- Server: `src/seoul_culture_mcp/server.py`
- HTTP client: `src/seoul_culture_mcp/clients/seoul_api.py`
- Validation helpers: `src/seoul_culture_mcp/utils/validation.py`
- Settings: `src/seoul_culture_mcp/settings.py`
- Tests: `tests/`
- CLI helper: `run_server.py`
- Windows scripts: `scripts/run_server.cmd`, `scripts/run_tests.cmd`, `scripts/run_smoke.cmd`, `scripts/claude_code_install.cmd`
- Client configs: `.mcp_example.json`, `.mcp_example_run_server.json`, `opencode.json`
- Troubleshooting: `TROUBLESHOOTING.md`, `TROUBLESHOOTING_KO.md`

Environment
- Windows venv path: `C:\Users\skyop\jaeho_template\dotenv_windows`
- Always use that Python when running commands.
- Claude Desktop runs servers in an isolated env, so config must include explicit `env` values.

Build / run / test commands

Run server (STDIO)
- Recommended (venv Python):
  - `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\04.OPENAPI_MCP_Server\run_server.py`
- Direct module (needs PYTHONPATH):
  - `set PYTHONPATH=src && C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m seoul_culture_mcp.server`

Run tests (all)
- Script wrapper:
  - `scripts\run_tests.cmd`
- Direct:
  - `set PYTHONPATH=src && C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m unittest discover -s tests`

Run a single test
- `set PYTHONPATH=src && C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m unittest tests.test_validation.ValidationTests.test_validate_date_str`

Smoke test (STDIO client)
- `scripts\run_smoke.cmd`
- Direct:
  - `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe scripts\stdio_smoke.py`

Dependency sync
- `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\uv.exe sync`
- Note: scripts use `uv run --active --no-sync` to avoid auto-sync.

Lint / format
- No linter or formatter configured in `pyproject.toml`.
- Follow existing style and keep formatting consistent with current files.

Coding style guidelines

Imports
- Order: standard library, third-party, local modules.
- Use a blank line between import groups.
- Prefer `from __future__ import annotations` at top of modules.

Formatting
- 4-space indentation.
- Keep line lengths reasonable; follow existing wrapping patterns.
- Avoid adding comments unless needed to clarify non-obvious logic.

Typing
- Use Python 3.11 type syntax (`str | None`, `list[dict]`, etc.).
- Keep public tool signatures typed and explicit.
- Pydantic models allow extra fields (`ConfigDict(extra="allow")`).

Naming
- Use `snake_case` for functions and variables.
- MCP tools are lowercase, descriptive verbs (e.g., `get_cultural_events`).
- Constants in ALL_CAPS (see settings defaults).

Error handling
- Input validation: raise `ValueError` in validation helpers or tool functions.
- API errors: raise `SeoulAPIError` in the client, wrap to `RuntimeError` at tool layer.
- Do not log or print secrets (API key).

Settings and config
- Load env via `settings.get_settings()` only.
- Supported env vars:
  - `SEOUL_API_KEY` (required)
  - `SEOUL_API_BASE_URL` (optional)
  - `SEOUL_API_SERVICE` (optional)
  - `SEOUL_API_TYPE` (optional)
  - `SEOUL_API_TIMEOUT_SECONDS` (optional)

Data handling rules
- Preserve API field names and types:
  - `is_free` is a string (`"무료"` / `"유료"`).
  - `lat`/`lot` are strings (do not coerce unless required).
  - `strtdate`/`end_date` are epoch ms integers.
- Return data as `description`, `data`, `meta` for list/get tools.
- For search tools return `items` and `meta`.

Networking
- Use `httpx.AsyncClient` with `settings.timeout_seconds`.
- Build URLs via `build_request_url()`.
- Propagate HTTP error status with a clean error message.

Testing guidelines
- Use `unittest` (not pytest).
- Integration tests (`tests/test_integration.py`) require `SEOUL_API_KEY`.
- When adding tests, keep them deterministic and avoid network unless explicitly an integration test.

MCP tool catalog
- `get_cultural_events`: page-based fetch with optional filters.
- `list_cultural_events`: alias of `get_cultural_events`.
- `search_cultural_events`: multi-page search with optional filters.
- `search_events_by_title`: keyword search by title.
- `search_events_by_date_range`: overlap search within a date range.
- `search_events_by_category`: category (codename) filter, optional free flag.
- `get_free_events`: free events only, optional district filter.
- `get_event_by_location`: district (guname) filter.
- `get_event_field_map`: returns the `DESCRIPTION` field map.

Client configs
- Claude Desktop:
  - `.mcp_example.json` (runs `src/server.py`)
  - `.mcp_example_run_server.json` (runs `run_server.py`)
  - After edits, fully quit and restart Claude Desktop.
- OpenCode: register in `opencode.json`.
- Claude Code: use `claude mcp add` or `scripts/claude_code_install.cmd`.

Workspace hygiene
- Do not commit secrets (`.env` is ignored).
- Avoid deleting or changing sample data files unless required.

Notes for agents
- Prefer `run_server.py` for a clean entrypoint.
- Use the existing helper scripts in `scripts/` when possible.
- Keep behavior backward-compatible with existing MCP tool names.
