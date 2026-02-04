# AGENTS.md

## Purpose
- Guidance for agentic contributors working in this repository.
- Focus on safe defaults, repeatable commands, and local conventions.
- Keep this file aligned with real tooling; update when tooling changes.
- Follow existing patterns unless the user requests a refactor.

## Repository Summary
- Python MCP server that returns a random number via stdio transport.
- Primary runtime logic lives in `random_mcp_server/server.py`.
- Entry points are exposed both as a module and as a console script.

## Key Paths
- `pyproject.toml`: project metadata and script entry point.
- `random_mcp_server/server.py`: MCP server, tools, and run loop.
- `random_mcp_server/__main__.py`: module entry for `python -m`.
- `random_mcp_server/__init__.py`: package version.
- `README_PLAY.md`: initial requirements snapshot.

## Setup
- Requires Python 3.11+.
- Install dependencies: `pip install -e .`.
- No system packages required beyond Python.

## Run / Build
- Run module: `python -m random_mcp_server`.
- Run console script: `random-mcp-server`.
- Run file directly: `python random_mcp_server/server.py`.
- Build step: not configured (no wheel/sdist tooling declared).
- If build tooling is added, document exact commands here.

## Lint / Format
- Lint: not configured.
- Format: not configured.
- Keep to PEP 8 with 4-space indentation.
- Aim for line length around 100 (no hard enforcement).
- Prefer f-strings over `%` formatting or `.format()`.
- Use explicit imports; avoid star imports.

## Tests
- Test runner: not configured.
- No tests currently present.
- Single-test command: N/A (no test framework configured).
- If you add pytest, prefer:
  `pytest path/to/test_file.py::test_name`.
- Keep tests deterministic; seed RNG when testing randomness.

## Manual Smoke Test
- Run server: `python -m random_mcp_server`.
- Use an MCP client to call `get_random_number`.
- Verify stdout is valid JSON-RPC and stderr logs the number.
- Ensure returned values are within 1..100.

## MCP Protocol Conventions
- Use `mcp.server.Server` for server definition.
- Use `mcp.stdio_server` for stdio transport.
- Register tools via `@server.list_tools()`.
- Handle invocations via `@server.call_tool()`.
- Return text with `mcp.types.TextContent`.
- Keep `inputSchema` strict and minimal; set `additionalProperties: False`.

## Tool Behavior Guidelines
- Tool names are stable and `snake_case`.
- Do not change tool semantics without updating clients/tests.
- Avoid side effects in tool handlers unless required.
- Keep tool output simple text unless structured output is needed.

## Logging / Debugging
- Debug output goes to stderr only.
- Use a short prefix, e.g. `[debug] message`.
- Never write logs to stdout (reserved for MCP JSON-RPC).
- Keep logs sparse; avoid spamming in repeated calls.

## Imports
- Order: standard library, third-party, local.
- Separate import groups with a blank line.
- Import types from `mcp.types` explicitly when used.
- Avoid circular imports across package modules.

## Formatting
- 4 spaces per indent.
- One blank line between top-level definitions.
- Keep functions small and focused.
- Prefer early returns to reduce nesting.
- Use module-level constants for shared strings.

## Types
- Type hints are optional but encouraged for public functions.
- Use built-in generics (`list[str]`, `dict[str, Any]`).
- Avoid overly complex typing for small modules.

## Naming
- Modules, functions, variables: `snake_case`.
- Constants: `UPPER_SNAKE_CASE`.
- Tool names should be descriptive and stable.
- Keep identifiers short but clear.

## Error Handling
- Validate tool names and raise `ValueError` for unknown tools.
- Keep errors user-readable; avoid stack traces in tool output.
- Catch exceptions only when you can add context.
- Let MCP framework handle JSON-RPC error formatting.

## Randomness Guidelines
- Use Python `random` module unless determinism is required.
- Seed RNG in tests or examples when reproducibility matters.
- Avoid global state changes that affect randomness.

## Entry Points
- Console entry: `random-mcp-server` -> `random_mcp_server.server:main`.
- Module entry: `python -m random_mcp_server`.
- Keep `main()` lightweight; delegate to async `run_server()`.
- Avoid side effects at import time.

## Dependencies
- Runtime dependency: `mcp`.
- Standard library modules used: `asyncio`, `random`, `sys`.
- Add new dependencies sparingly and document them in `pyproject.toml`.

## Configuration
- No environment variables are required.
- If you add config, document it in `README_PLAY.md` and here.
- Keep defaults safe for local execution.
- Avoid using stdout/stderr for configuration.

## Async + IO
- Keep tool handlers async and non-blocking.
- Avoid long-running CPU work in request handlers.
- Use `asyncio.to_thread` for unavoidable blocking work.
- Avoid creating global event loops outside `main()`.

## Git / Workspace Hygiene
- Do not remove user changes unless asked.
- Avoid committing generated files like `__pycache__`.
- Keep diffs focused and minimal.

## Documentation
- Update `README_PLAY.md` only when requirements change.
- Keep AGENTS.md aligned with actual tooling and practices.
- Prefer concise, actionable notes over long prose.

## Cursor / Copilot Rules
- No `.cursor/rules/`, `.cursorrules`, or `.github/copilot-instructions.md` found.
- If added later, copy those rules into this section verbatim.

## Change Checklist
- Verify tool list includes any new tools.
- Ensure schemas match tool behavior.
- Confirm stderr logging format remains consistent.
- Avoid stdout writes outside MCP protocol.
- Update version string if publishing changes.
