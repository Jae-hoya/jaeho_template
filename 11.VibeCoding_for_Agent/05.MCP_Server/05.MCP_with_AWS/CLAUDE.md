# CLAUDE.md - AI Agent Guide for Seoul Culture Events MCP Server Template

> 이 문서는 Claude 및 AI 에이전트가 Seoul Culture Events MCP Server 템플릿을 이해하고 활용할 수 있도록 구조화된 정보를 제공합니다.

## Project Overview

**Purpose**: Cookiecutter template for creating MCP servers that integrate with Seoul Open Data API for culture events

**Framework**: FastMCP (mcp[cli]>=1.6.0, fastmcp>=2.14.0)

**Pattern**: AWS MCP Servers naming convention and monorepo structure

## Template Structure

### Core Files

```yaml
template_claudecode/
  cookiecutter.json:
    purpose: "Template variable definitions"
    key_variables:
      - project_domain: "Data Seoul"
      - api_key_env_var: "SEOUL_API_KEY"
      - description: "MCP server description"
      - instructions: "Tool usage instructions"

  project_template/:
    structure: "AWS MCP compliant Python package"
    entry_point: "awslabs.{project}_mcp_server.server:main"
    package_manager: "uv"
    python_version: ">=3.10"
```

### Generated Project Structure

```yaml
data-seoul-mcp-server/:
  awslabs/{project}_mcp_server/:
    server.py:
      role: "FastMCP server entry point"
      registers: ["search_culture_events", "get_culture_space", "get_event_details"]

    config.py:
      role: "Seoul API configuration"
      uses: "Pydantic BaseModel"
      env_var: "SEOUL_API_KEY"
      base_url: "http://openapi.seoul.go.kr:8088"

    tools/culture_events.py:
      role: "MCP tool implementations"
      tools:
        search_culture_events:
          params: ["query", "start_date", "end_date", "district", "genre", "max_results"]
          returns: "List[Dict[str, Any]]"

        get_culture_space:
          params: ["space_name", "district", "genre", "max_results"]
          returns: "List[Dict[str, Any]]"

        get_event_details:
          params: ["event_code"]
          returns: "Dict[str, Any]"

    utils/api_client.py:
      role: "Seoul API HTTP client"
      framework: "httpx.AsyncClient"
      methods: ["_request", "search_culture_events", "get_culture_spaces", "get_event_details"]
```

## Seoul API Integration

### API Endpoints

```yaml
base_url: "http://openapi.seoul.go.kr:8088"
auth: "API key in URL path"
format: "JSON"

url_structure: "{base_url}/{api_key}/json/{service}/{start_idx}/{end_idx}"

services:
  culturalEventInfo:
    description: "문화행사 정보"
    response_fields:
      - CULTCODE: "문화행사코드"
      - TITLE: "행사명"
      - STRTDATE: "시작일자"
      - END_DATE: "종료일자"
      - PLACE: "장소"
      - CODENAME: "장르명"
      - GUNAME: "자치구명"
      - DESCRIPTION: "설명"
      - ORG_LINK: "URL"

  culturalSpaceInfo:
    description: "문화공간 정보"
    response_fields:
      - FAC_CODE: "시설코드"
      - FAC_NAME: "시설명"
      - ADDR: "주소"
      - GUNAME: "자치구"
      - CODENAME: "유형"
      - PHONE: "전화번호"
```

### Data Categories

```yaml
문화행사_정보:
  - 공연: "음악, 연극, 무용"
  - 전시: "미술, 박물관"
  - 축제: "지역축제, 문화축제"
  - 교육: "문화강좌, 체험프로그램"

자치구:
  강남구, 강동구, 강북구, 강서구, 관악구, 광진구,
  구로구, 금천구, 노원구, 도봉구, 동대문구, 동작구,
  마포구, 서대문구, 서초구, 성동구, 성북구, 송파구,
  양천구, 영등포구, 용산구, 은평구, 종로구, 중구, 중랑구
```

## Usage Patterns for AI Agents

### 1. Creating New MCP Server

```python
# Step 1: Run cookiecutter
command = "uvx cookiecutter template_claudecode"

# Step 2: Provide variables
variables = {
    "author_name": "Your Name",
    "author_email": "email@example.com",
    "project_domain": "Data Seoul",
    "api_key_env_var": "SEOUL_API_KEY"
}

# Step 3: Implement API client
# Edit: utils/api_client.py
# Implement: search_culture_events(), get_culture_spaces(), get_event_details()

# Step 4: Test
commands = [
    "uv sync --all-groups",
    "uv run pytest --cov",
    "uv run pyright"
]
```

### 2. Integrating with Claude Desktop

```yaml
config_file:
  macos: "~/Library/Application Support/Claude/claude_desktop_config.json"
  windows: "%APPDATA%\\Claude\\claude_desktop_config.json"

local_development:
  command: "uv"
  args:
    - "--directory"
    - "/absolute/path/to/data-seoul-mcp-server"
    - "run"
    - "awslabs.data_seoul_mcp_server.server:main"
  env:
    SEOUL_API_KEY: "your-api-key"

published_package:
  command: "uvx"
  args:
    - "awslabs.data-seoul-mcp-server@latest"
```

### 3. Query Patterns

```yaml
search_queries:
  by_genre: "강남구에서 열리는 클래식 음악 공연을 찾아줘"
  by_location: "종로구의 미술관 정보를 알려줘"
  by_date: "이번 주말 서울에서 열리는 전시회는?"
  by_keyword: "어린이를 위한 문화행사를 추천해줘"

response_format:
  events:
    - event_code: "CE2025010001"
      title: "서울 클래식 페스티벌"
      start_date: "20250215"
      end_date: "20250217"
      location: "세종문화회관"
      district: "종로구"
      genre: "음악"
```

## Implementation Checklist

### Required Implementations

```yaml
1_api_client:
  file: "utils/api_client.py"
  methods:
    _request: "HTTP request wrapper with error handling"
    search_culture_events: "Parse culturalEventInfo response"
    get_culture_spaces: "Parse culturalSpaceInfo response"
    get_event_details: "Fetch detailed event by code"

2_configuration:
  file: "config.py"
  validations:
    - api_key: "Check SEOUL_API_KEY env var"
    - base_url: "Default: http://openapi.seoul.go.kr:8088"
    - timeout: "Default: 30.0 seconds"

3_tools:
  file: "tools/culture_events.py"
  implementations:
    - search_culture_events: "Filter by query, date, district, genre"
    - get_culture_space: "Search cultural venues"
    - get_event_details: "Detailed event information"

4_tests:
  files: ["tests/test_init.py", "tests/test_server.py"]
  coverage: ">= 80%"
  async_tests: "Use pytest-asyncio"
```

## Naming Convention Rules

```python
# AWS MCP Servers standard
def convert_domain_name(domain: str) -> dict:
    """
    Input: "Data Seoul"

    Returns:
        directory: "data-seoul-mcp-server"
        module: "data_seoul_mcp_server"
        package: "awslabs.data-seoul-mcp-server"
    """
    lower = domain.lower()
    hyphenated = lower.replace(' ', '-').replace('_', '-')
    underscored = hyphenated.replace('-', '_')

    return {
        "directory": f"{hyphenated}-mcp-server",
        "module": f"{underscored}_mcp_server",
        "package": f"awslabs.{hyphenated}-mcp-server"
    }
```

## Error Handling Patterns

```yaml
api_errors:
  no_api_key:
    check: "config.api_key is empty"
    raise: "ValueError('Seoul API key not configured')"

  http_error:
    check: "response.status_code != 200"
    log: "logger.error(f'HTTP error: {e}')"
    raise: "ValueError(f'API request failed: {str(e)}')"

  json_parse_error:
    check: "response.json() fails"
    handle: "Return empty list or dict"

tool_errors:
  invalid_date_format:
    validate: "YYYYMMDD format"
    example: "20250201"

  max_results_exceeded:
    limit: 100
    apply: "min(max_results, 100)"
```

## Testing Strategy

```yaml
unit_tests:
  test_config:
    - "Verify SeoulAPIConfig defaults"
    - "Check API key from env var"
    - "Test get_api_url() formatting"

  test_api_client:
    - "Mock httpx responses"
    - "Test _request() error handling"
    - "Verify JSON parsing"

  test_tools:
    - "Mock SeoulAPIClient"
    - "Test parameter validation"
    - "Verify return types"

integration_tests:
  mcp_inspector:
    command: "npx @modelcontextprotocol/inspector uv --directory . run awslabs.data_seoul_mcp_server.server:main"
    verify:
      - "Tools are registered"
      - "Can execute search_culture_events"
      - "Returns valid JSON"
```

## Common Agent Tasks

### Task: Debug "Module not found" Error

```yaml
diagnosis:
  check_1: "Did you run 'uv sync' in project directory?"
  check_2: "Is --directory path absolute?"
  check_3: "Is module name using underscores (data_seoul_mcp_server)?"

solution:
  correct_path: "/absolute/path/to/data-seoul-mcp-server"
  correct_module: "awslabs.data_seoul_mcp_server.server:main"
```

### Task: Add New Search Filter

```yaml
steps:
  1_update_tool:
    file: "tools/culture_events.py"
    add_parameter: "price_range: Optional[str] = None"

  2_update_client:
    file: "utils/api_client.py"
    add_logic: "Filter results by price_range"

  3_add_test:
    file: "tests/test_server.py"
    test: "test_search_with_price_filter()"

  4_update_docs:
    file: "README.md"
    section: "## Tools > search_culture_events"
```

## Best Practices for AI Agents

1. **Always use absolute paths** in MCP configurations
2. **Check env vars** before API calls (SEOUL_API_KEY)
3. **Use async/await** for all API operations
4. **Validate dates** in YYYYMMDD format
5. **Limit results** to prevent memory issues (max 100)
6. **Handle Korean text** properly (UTF-8 encoding)
7. **Test with MCP Inspector** before production
8. **Follow AWS naming** conventions strictly

## Quick Reference

```yaml
commands:
  create_project: "uvx cookiecutter template_claudecode"
  install_deps: "uv sync --all-groups"
  run_tests: "uv run pytest --cov"
  type_check: "uv run pyright"
  lint: "uv run ruff check ."
  format: "uv run ruff format ."
  inspect: "npx @modelcontextprotocol/inspector uv --directory . run awslabs.data_seoul_mcp_server.server:main"

files_to_implement:
  - "utils/api_client.py"
  - "tests/test_server.py"

files_to_configure:
  - "Claude Desktop config.json"
  - "Cursor cline_mcp_settings.json"
```

## Development Workflow (TDD)

```yaml
tdd_cycle:
  1_red:
    action: "Write failing test"
    command: "uv run pytest -x"
    commit: "git add tests/ && git commit -m 'test: add <feature> test'"

  2_green:
    action: "Implement minimum code"
    command: "uv run pytest -x"
    commit: "git add awslabs/ && git commit -m 'feat: implement <feature>'"

  3_refactor:
    action: "Improve code quality"
    command: "uv run pytest && uv run pyright && uv run ruff check ."
    commit: "git add awslabs/ && git commit -m 'refactor: improve <feature>'"

git_workflow:
  principles:
    - "Atomic commits (one change per commit)"
    - "Add related files only (not 'git add .')"
    - "NEVER git push (local development only)"

  commit_convention:
    format: "<type>(<scope>): <subject>"
    types: ["feat", "fix", "test", "refactor", "docs", "chore"]
    example: "feat(tools): add genre filter to search_culture_events"

  commands:
    stage_specific: "git add <file1> <file2>"
    commit_atomic: "git commit -m '<type>: <message>'"
    check_status: "git status"
    review_changes: "git diff"
    undo_last_commit: "git reset --soft HEAD~1"

quality_checks:
  before_commit:
    - "uv run pytest"
    - "uv run pyright"
    - "uv run ruff check ."

  coverage_requirement: ">= 80%"

  type_hints: "All public functions must have type hints"

  docstrings: "Google style for all public functions"
```

## Development Commands Reference

```bash
# Testing
uv run pytest                           # Run all tests
uv run pytest -v                        # Verbose output
uv run pytest -x                        # Stop on first failure
uv run pytest --lf                      # Run last failed tests
uv run pytest -m "not live"             # Skip live API tests
uv run pytest --cov --cov-report=html   # Coverage report

# Type Checking
uv run pyright                          # Check all files
uv run pyright awslabs/                 # Check specific directory

# Linting & Formatting
uv run ruff check .                     # Lint check
uv run ruff check --fix .               # Auto-fix issues
uv run ruff format .                    # Format code
uv run ruff format --check .            # Check formatting

# Running Server
uv run awslabs.data_seoul_mcp_server.server:main  # Direct run
SEOUL_API_KEY=key uv run awslabs.data_seoul_mcp_server.server:main  # With env var

# MCP Inspector
npx @modelcontextprotocol/inspector uv --directory . run awslabs.data_seoul_mcp_server.server:main

# Dependencies
uv add <package>                        # Add dependency
uv add --dev <package>                  # Add dev dependency
uv sync                                 # Sync dependencies
```

---

**Document Type**: AI Agent Technical Guide
**Last Updated**: 2025-02-01
**Template Version**: 0.0.0
**Optimized For**: Claude Sonnet, GPT-4, AI Code Assistants
