# AGENTS.md

## Purpose
- Guidance for agentic contributors working in this repository.
- Prefer safe defaults, explicit validation, and predictable outputs.
- Keep this file aligned with actual tooling and update it when tools change.

## Repository summary
- Python MCP server for PostgreSQL over stdio transport.
- Supports read-only SQL queries and safe candidate updates.
- Exposes table schema resources for public tables.

## Key paths
- `server.py`: MCP server, tool handlers, resource handlers, asyncpg pool.
- `pyproject.toml`: dependencies and console script.
- `README.md`: usage guide.
- `insert_candidates.sql`: seed data from live DB.
- `candidates.csv`, `candidates.json`: snapshots from live DB.

## Setup
- Python 3.11+ required.
- Install editable: `pip install -e .`
- Dependencies: `mcp`, `asyncpg`.

## Run commands
- Stdio server: `python server.py "postgresql://user:pass@host:5432/db"`
- Or set env: `DATABASE_URL`, `POSTGRES_URL`, or `PG_URL`.
- Console script (after install): `recursive-mcp-server <db_url>`.

## Build / lint / test
- Build: not configured.
- Lint: not configured.
- Format: not configured.
- Tests: not configured.

## Single test command (if tests are added)
- Pytest example: `python -m pytest path\to\test_file.py::test_name`

## MCP tools
- `query`: read-only SQL only; single statement; returns JSON list.
- `update_candidate`: only `position`, `skills`, `company` allowed; `id` required.
- `update_candidate` auto-derives `category` from `position` when provided.

## Tool contract guidelines
- Define `inputSchema` with `type`, `properties`, and `required`.
- Always set `additionalProperties: false` for tool inputs.
- Keep tool names stable; changing names breaks clients.
- Return `TextContent` with JSON for data responses.
- Use `json.dumps(..., ensure_ascii=False, default=str)` for datetimes.

## Resource behavior
- `list_resources` should enumerate public tables only.
- Resource `name` should be stable and descriptive (e.g., `<table>_schema`).
- Resource `uri` must be absolute and parseable by clients.
- `read_resource` returns a JSON array of column metadata.
- Reject invalid resource URIs with `ValueError`.

## MCP resources
- Lists public table schemas as resources.
- Resource URIs use `postgres://<user>@<host>:<port>/<db>/<table>/schema`.
- `read_resource` returns JSON with `column_name` and `data_type`.

## Database rules
- Use parameterized SQL for updates; never interpolate user strings.
- Reject multiple SQL statements for `query`.
- Read-only tokens: `SELECT`, `WITH`, `SHOW`, `EXPLAIN`, `VALUES`, `TABLE`.
- Only mutate `public.candidates` through `update_candidate`.

## Output formatting
- Return JSON arrays for `query` results.
- Use stable field ordering where possible.
- Keep numeric values as numbers; do not stringify ids.
- Convert datetimes via `default=str` (ISO-like output).
- Do not log or return connection strings.

## Logging guidelines
- Log to stderr only (never stdout).
- Use `[debug]` prefix for operational logs.
- Log tool entry and key outcomes; avoid noisy spam.
- Do not log secrets (connection strings, tokens, passwords).

## Error handling
- Raise `ValueError` for invalid inputs or unknown tools.
- Fail fast on missing/invalid args.
- Keep errors short and user-readable.
- Let the MCP framework format JSON-RPC errors.

## Code style
- Imports: standard library, third-party, local; separate groups with blank lines.
- Formatting: 4 spaces; aim for <=100 char lines.
- Strings: double quotes.
- Avoid unused imports and side effects at import time.

## Types
- Prefer explicit type hints on public functions and handlers.
- Use built-in generics (`list[str]`, `dict[str, Any]`).
- Keep typing lightweight; avoid complex generics unless needed.

## Naming
- Constants: `UPPER_SNAKE_CASE`.
- Functions/vars: `snake_case`.
- Tool names: short, lowercase, stable.

## Async patterns
- Use async handlers for MCP tools/resources.
- Keep tool handlers non-blocking.
- Use `asyncpg` pool; create in `main()` and close on shutdown.

## Performance and reliability
- Prefer indexed columns for filters (`id`, `category`, `company`).
- Avoid long-running queries in tool handlers.
- Keep pool size modest (default 5) unless load requires more.
- Return early on validation errors.
- Ensure `READ ONLY` transaction for `query`.

## Security and privacy
- Treat tool input as untrusted.
- Never allow arbitrary SQL execution outside `query` read-only guard.
- Sanitize logs; avoid PII exposure in debug logs.

## Configuration
- Use absolute paths in client configs (Claude Desktop working dir may be undefined).
- Use `env` to pass DB URL when launched by desktop clients.

## Debugging tips
- Validate config JSON before launching a client.
- If a client fails to connect, verify the executable path is absolute.
- Check stderr logs for `[debug]` lines.
- In Claude Desktop, restart after config changes.
- Use a minimal `SELECT 1` query to confirm connectivity.

## Data sync workflow
- Prefer updating DB first, then regenerate `insert_candidates.sql`.
- Regenerate `candidates.csv` and `candidates.json` from DB snapshots.
- Keep `created_at` intact; do not backfill or rewrite timestamps.
- Note any manual overrides in commit messages or change notes.

## Files to avoid editing
- `README_PLAY.md` is a prompt log; update only if requirements change.

## Cursor / Copilot rules
- No `.cursor/rules`, `.cursorrules`, or `.github/copilot-instructions.md` found in this repo.

## Change checklist
- Update tool list when adding new tools.
- Keep input schemas strict (`additionalProperties: false`).
- Verify read-only guard for any query changes.
- Ensure update statements remain parameterized.
- Update `README.md` when behavior changes.
- Keep seed snapshots (`insert_candidates.sql`, `candidates.csv`, `candidates.json`) in sync with DB.
