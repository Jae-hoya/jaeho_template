# Seoul Open Data MCP Server

**Unified Model Context Protocol (MCP) server for Seoul Open Data APIs**

This MCP server provides access to multiple Seoul Open Data services through a single, unified interface:

- **Culture Events**: Seoul cultural events, performances, exhibitions, festivals
- **Public Reservations**: Museum programs, workshops, educational experiences
- **Women & Family Events**: Seoul Women & Family Foundation events and programs

## Features

- 🎭 Search Seoul cultural events by category, title, date, and location
- 📅 Access public service reservation information
- 👥 Retrieve women & family foundation events
- 🔍 Flexible filtering and search capabilities
- 🚀 FastMCP-based implementation with async support
- 🔑 Support for multiple API keys

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Install the server

```bash
# Clone or navigate to the project directory
cd seoul-opendata-mcp-server

# Install dependencies
uv sync --all-groups

# Or install without dev dependencies
uv sync
```

## Configuration

### API Keys

You need API keys from [Seoul Open Data Portal](https://data.seoul.go.kr/):

1. Register for an account at https://data.seoul.go.kr/
2. Request API keys for:
   - Culture Events API (문화행사정보)
   - Women & Family Foundation Events API (서울여성플라자 이벤트)

### Environment Variables

Set the following environment variables:

```bash
export SEOUL_CULTURE_API_KEY="your-culture-events-api-key"
export SEOUL_WOMEN_API_KEY="your-women-events-api-key"
```

## Usage

### Running the Server

```bash
# Using uv
uv run awslabs.seoul_opendata_mcp_server.server:main

# Or if installed
seoul-opendata-mcp-server
```

### Claude Desktop Integration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "seoul-opendata": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/seoul-opendata-mcp-server",
        "run",
        "awslabs.seoul_opendata_mcp_server.server:main"
      ],
      "env": {
        "SEOUL_CULTURE_API_KEY": "your-culture-api-key",
        "SEOUL_WOMEN_API_KEY": "your-women-api-key"
      }
    }
  }
}
```

### Cursor/Cline Integration

Add to your `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "seoul-opendata": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/seoul-opendata-mcp-server",
        "run",
        "awslabs.seoul_opendata_mcp_server.server:main"
      ],
      "env": {
        "SEOUL_CULTURE_API_KEY": "your-culture-api-key",
        "SEOUL_WOMEN_API_KEY": "your-women-api-key"
      }
    }
  }
}
```

## Available Tools

### Culture Events Tools

#### `search_culture_events`
Search Seoul cultural events.

**Parameters:**
- `codename` (optional): Event category (공연, 전시, 축제, etc.)
- `title` (optional): Event title (partial match)
- `date` (optional): Event date (YYYY-MM-DD format)
- `start_index`: Start index for pagination (default: 1)
- `end_index`: End index for pagination (default: 10)

**Example:**
```
Search for classical music concerts in Seoul
Search for exhibitions happening this weekend
```

#### `search_public_reservations`
Search public service reservations.

**Parameters:**
- `svc_code_name` (optional): Service category
- `svc_name` (optional): Service name
- `start_index`: Start index for pagination (default: 1)
- `end_index`: End index for pagination (default: 10)

### Women & Family Events Tools

#### `search_women_events`
Search Seoul Women & Family Foundation events.

**Parameters:**
- `title` (optional): Event title (partial match)
- `event_type` (optional): Event type (공연, 전시, 강좌, 체험, etc.)
- `max_results`: Maximum results to return (default: 10, max: 100)

**Example:**
```
Find women's cultural programs in Seoul
Search for family workshops and seminars
```

#### `get_event_details`
Get detailed information about a specific event.

**Parameters:**
- `event_reg_no`: Event registration number

#### `get_all_women_events`
Retrieve all available women & family events.

**Parameters:**
- `max_results`: Maximum results to return (default: 50, max: 100)

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Skip live API tests
uv run pytest -m "not live"
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Auto-fix
uv run ruff check --fix .

# Formatting
uv run ruff format .

# Type checking
uv run pyright
```

### Project Structure

```
seoul-opendata-mcp-server/
├── awslabs/
│   └── seoul_opendata_mcp_server/
│       ├── __init__.py
│       ├── server.py                  # Main MCP server
│       ├── config.py                  # Configuration
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── culture_events.py      # Culture events tools
│       │   └── women_events.py        # Women events tools
│       └── utils/
│           ├── __init__.py
│           ├── culture_api_client.py  # Culture API client
│           └── women_api_client.py    # Women API client
├── tests/
│   └── ... (test files)
├── pyproject.toml
└── README.md
```

## API Services

This server integrates with the following Seoul Open Data services:

1. **문화행사정보 (Culture Events)**
   - Service: `culturalEventInfo`
   - Base URL: `http://openapi.seoul.go.kr:8088`

2. **문화행사 공공서비스예약정보 (Public Reservations)**
   - Service: `culturalSpaceInfo`
   - Base URL: `http://openapi.seoul.go.kr:8088`

3. **서울여성플라자 이벤트 (Women Plaza Events)**
   - Service: `SeoulWomenPlazaEvent`
   - Base URL: `http://openapi.seoul.go.kr:8088`

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

## Links

- [Seoul Open Data Portal](https://data.seoul.go.kr/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [AWS MCP Servers](https://github.com/awslabs/mcp)

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For issues or questions:
- GitHub Issues: [Report an issue](https://github.com/awslabs/mcp/issues)
- Documentation: [Read the docs](https://awslabs.github.io/mcp/)
