# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastMCP server that exposes Seoul cultural events from the Seoul Open Data API (`http://openapi.seoul.go.kr:8088/culturalEventInfo`) through the Model Context Protocol. The server provides 9 tools for querying cultural events by various criteria (title, date range, category, location, free/paid status).

## Development Commands

### Running the MCP Server

**Stdio mode (for MCP clients like Claude Desktop)**:
```bash
uv run python src/seoul_culture_mcp/server.py
```

Or via the installed script:
```bash
uv run seoul-culture-mcp
```

### Testing

Run all tests:
```bash
uv run pytest
```

Run specific test file:
```bash
uv run pytest tests/test_validation.py
```

Run tests with verbose output:
```bash
uv run pytest -v
```

### Package Management

Add a dependency:
```bash
uv add <package-name>
```

Sync dependencies:
```bash
uv sync
```

## Architecture

### Core Components

**`src/seoul_culture_mcp/server.py`**: Main MCP server entry point. Contains 9 tool functions decorated with `@mcp.tool` that expose different search capabilities. Uses a shared `_search_events()` helper function for paginated filtering across the API.

**`src/seoul_culture_mcp/clients/seoul_api.py`**: HTTP client for Seoul OpenAPI. Handles:
- URL construction with path parameters (KEY/TYPE/SERVICE/START_INDEX/END_INDEX)
- Query parameters (CODENAME, TITLE, DATE)
- Response parsing and error handling
- Returns raw payload and the actual request URL

**`src/seoul_culture_mcp/settings.py`**: Configuration management using environment variables. Singleton pattern with `get_settings()`. Loads `.env` file via python-dotenv.

**`src/seoul_culture_mcp/models.py`**: Pydantic models for API response validation (EventResponse structure).

**`src/seoul_culture_mcp/utils/validation.py`**: Input validation and client-side filtering helpers for matching events by title, date range, location, and free status.

### Data Flow

1. MCP tool receives user parameters
2. Tool validates inputs using `utils/validation.py`
3. `_search_events()` orchestrates pagination and filtering
4. `clients/seoul_api.py` makes HTTP requests to Seoul API
5. Response parsed using `extract_description_data()`
6. Client-side filtering applied (for filters not supported by API)
7. Tool returns structured result with `items` and `meta` fields

### Key Architectural Decisions

**Client-side filtering**: The Seoul API has limited query parameter support. For filters like `guname` (district), `is_free`, and fuzzy title matching, the server fetches pages from the API and filters in-memory.

**Pagination strategy**: Uses `page_size` parameter for API requests and continues fetching pages until `limit` items are matched or no more data is available.

**Dual interface**: Provides both low-level pagination tools (`get_cultural_events` with start/end index) and high-level search tools (`search_*` with limit/page_size).

**Error handling**: Wraps `SeoulAPIError` exceptions from the client layer as `RuntimeError` at the tool layer for better MCP error messages.

## Configuration

Required environment variables (set in `.env` file):
```
SEOUL_API_KEY=your_api_key_here
```

Optional environment variables:
```
SEOUL_API_BASE_URL=http://openapi.seoul.go.kr:8088
SEOUL_API_SERVICE=culturalEventInfo
SEOUL_API_TYPE=json
SEOUL_API_TIMEOUT_SECONDS=10.0
```

## MCP Client Setup

**Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "seoul-cultural-events": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\path\\to\\04.OPENAPI_MCP_Server",
        "run",
        "python",
        "src/seoul_culture_mcp/server.py"
      ],
      "env": {
        "SEOUL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## Testing Strategy

Tests are located in `tests/` and cover:
- **test_validation.py**: Input validation and filter matching logic
- **test_extract.py**: Response parsing and data extraction
- **test_integration.py**: End-to-end tool execution (requires API key)

Integration tests can be skipped if `SEOUL_API_KEY` is not set.

## Seoul API Specifics

**Response structure**:
- Top-level keys: `DESCRIPTION` (field labels in Korean) and `DATA` (array of events)
- Events use lowercase field names (e.g., `title`, `codename`, `guname`)

**Date fields**:
- `date`: Display string with range (e.g., "2026-05-15~2026-05-17")
- `strtdate`/`end_date`: Unix epoch milliseconds
- `DATE` query parameter: Single date in YYYY-MM-DD format

**Free/paid indicator**: `is_free` field is a string ("무료" or "유료"), not a boolean.

**Coordinates**: `lat` and `lot` are strings, not numbers.

## Package Structure

The package is named `seoul-culture-mcp` in pyproject.toml but the Python package is `seoul_culture_mcp` (underscore, not hyphen). Entry point script is registered as `seoul-culture-mcp`.
