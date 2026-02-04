# AGENTS

This repository is a cookiecutter template for a Seoul culture events MCP server.

## Scope

- Maintain the MCP server entry point, tools, and API client integration.
- Keep documentation aligned with the OpenAPI description and tool surface.
- Preserve cookiecutter placeholders exactly as written.

## Project Structure

- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/server.py`: MCP server entry point and tool registration.
- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/tools/culture_events.py`: Tool definitions and request parameters.
- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/utils/api_client.py`: Seoul Open Data API client.
- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/config.py`: Environment configuration and defaults.
- `tests/`: Placeholder test suite.

## 프로젝트 구조

- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/server.py`: MCP 서버 엔트리 포인트와 도구 등록
- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/tools/culture_events.py`: 도구 정의와 요청 파라미터
- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/utils/api_client.py`: 서울 Open Data API 클라이언트
- `awslabs/{{cookiecutter.project_domain | lower | replace(' ', '-') | replace('_', '-') | replace('-', '_')}}_mcp_server/config.py`: 환경설정 및 기본값
- `tests/`: 테스트 스위트

## Conventions

- Keep tool signatures stable; the MCP server registers functions by name.
- Enforce `max_results` limits consistently with tool defaults.
- Avoid logging secrets or API keys.
- Documentation changes should update `README.md` when tools or env vars change.

## Development Workflow

- Follow TDD: write a failing test first, implement, then refactor.
- Keep commits atomic; stage only files related to the change.
- Never run `git push` in this repository.

## 개발 워크플로우

- TDD 기반으로 진행: 실패하는 테스트를 먼저 작성한 뒤 구현하고 리팩터링합니다.
- 커밋은 atomic 단위로 유지하고, 변경과 관련된 파일만 스테이징합니다.
- 이 저장소에서는 `git push`를 실행하지 않습니다.

## Environment Variables

- `{{cookiecutter.api_key_env_var}}` (required): Seoul Open Data API key.
- `SEOUL_API_BASE_URL` (optional): Base URL for the OpenAPI endpoint.
- `FASTMCP_LOG_LEVEL` (optional): MCP log verbosity.

## Development Commands

- `uv sync --all-groups`
- `uv run pytest --cov`
- `uv run pyright`
- `uv run ruff check .`

## 개발 명령어

- `uv sync --all-groups`
- `uv run pytest --cov`
- `uv run pyright`
- `uv run ruff check .`
