# PLAN

## 1) Goal
- Build a FastMCP server that exposes the Seoul Cultural Events OpenAPI as MCP tools.
- Use STDIO transport (FastMCP `mcp.run()` default) for MCP communication.
- Package and run with `uv`, using the provided virtual environment path.

## 2) References (Context7)
- API spec: `seoul-culture-events-api.md`
- FastMCP server docs: https://gofastmcp.com/servers/server#the-fast-mcp-server
- Running server (STDIO default): https://gofastmcp.com/deployment/running-server

## 3) Constraints
- Language: Python
- MCP framework: FastMCP
- Transport: STDIO
- Package manager: `uv`
- Virtual env path: `C:\Users\skyop\jaeho_template\dotenv_windows`

## 4) Tech Stack
- Python 3.x
- fastmcp
- httpx (HTTP client)
- pydantic (data validation / typed responses)
- python-dotenv (optional env loading)
- uv (dependency + run)

## 5) Project Structure
```
.
├─ PLAN.md
├─ README.md
├─ pyproject.toml
├─ .env.example
├─ .gitignore
└─ src/
   └─ seoul_culture_mcp/
      ├─ __init__.py
      ├─ server.py
      ├─ settings.py
      ├─ models.py
      ├─ clients/
      │  └─ seoul_api.py
      └─ utils/
         └─ validation.py
```

## 6) Configuration
- Required
  - `SEOUL_API_KEY`
- Optional
  - `SEOUL_API_BASE_URL` (default: `http://openapi.seoul.go.kr:8088`)
  - `SEOUL_API_TYPE` (default: `json`)
  - `SEOUL_API_SERVICE` (default: `culturalEventInfo`)
  - `SEOUL_API_TIMEOUT_SECONDS` (default: 10)

## 7) MCP Tool Design
### Tool 1: `list_cultural_events`
- Purpose: Fetch a page of events directly from the Seoul API.
- Input
  - `start_index` (int, required, >= 1)
  - `end_index` (int, required, >= start_index)
  - `codename` (str, optional)
  - `title` (str, optional)
  - `date` (str, optional, format `YYYY-MM-DD`)
- Behavior
  - Build request: `/{KEY}/{TYPE}/{SERVICE}/{START_INDEX}/{END_INDEX}/`
  - Pass optional filters as query params: `CODENAME`, `TITLE`, `DATE`
- Output
  - `description`: field label map (`DESCRIPTION`)
  - `data`: list of events (`DATA`)
  - `meta`: request echo (start/end, applied filters, request URL)
- Error handling
  - Validate index range and required API key.
  - Propagate HTTP errors with a clean MCP error message.

### Tool 2: `search_cultural_events`
- Purpose: Search by title/codename/date across multiple pages.
- Input
  - `query` (str, optional title keyword)
  - `codename` (str, optional)
  - `date` (str, optional `YYYY-MM-DD`)
  - `limit` (int, optional, default 50)
  - `page_size` (int, optional, default 20)
- Behavior
  - Use API filters when possible; apply client-side substring match for `query`.
  - Iterate pages until `limit` or no more data.
- Output
  - `items`: matched events
  - `meta`: pages scanned, total matched, filters used

### Tool 3: `get_event_field_map`
- Purpose: Return the `DESCRIPTION` mapping (field labels).
- Input: none
- Behavior: Fetch a minimal page (1..1) and return only the `DESCRIPTION` map.
- Output: `description` map

## 8) Data Handling Rules
- Keep response fields consistent with the API spec.
- Do not coerce `lat`/`lot` unless explicitly requested by a tool parameter.
- `is_free` remains string (`무료` / `유료`).
- Keep `strtdate` and `end_date` as integers (epoch ms).

## 9) Error Handling & Logging
- Timeouts and non-200 responses return MCP errors with short messages.
- Include request URL and parameters in `meta` for debugging.
- Avoid logging the API key.

## 10) Implementation Steps
1. Initialize `pyproject.toml` with `uv` and add dependencies.
2. Create `settings.py` to load env vars and defaults.
3. Build `seoul_api.py` client with one `fetch_events` method.
4. Define `models.py` for response validation (Pydantic).
5. Implement tools in `server.py` using `@mcp.tool`.
6. Add `.env.example`, update `.gitignore`.
7. Document usage in `README.md`.

## 11) Run (STDIO)
- `uv run python -m seoul_culture_mcp.server`
- `mcp.run()` starts the server with STDIO transport by default.
