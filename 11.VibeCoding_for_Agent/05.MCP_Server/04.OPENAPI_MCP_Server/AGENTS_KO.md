# AGENTS_KO.md

목적
- 이 파일은 에이전트형 코딩 도구가 이 레포에서 실행/테스트/코딩 스타일을 따라갈 수 있도록 안내한다.

프로젝트 요약
- 서울시 문화행사 MCP 도구를 제공하는 FastMCP (STDIO) 서버.
- Python 패키지명: `seoul_culture_mcp`.
- 엔트리포인트: `src/seoul_culture_mcp/server.py`, `run_server.py`.

외부 규칙
- Cursor 규칙: 없음 (`.cursor/rules/`, `.cursorrules`).
- Copilot 규칙: 없음 (`.github/copilot-instructions.md`).

주요 경로
- 서버: `src/seoul_culture_mcp/server.py`
- HTTP 클라이언트: `src/seoul_culture_mcp/clients/seoul_api.py`
- 검증 유틸: `src/seoul_culture_mcp/utils/validation.py`
- 설정: `src/seoul_culture_mcp/settings.py`
- 테스트: `tests/`
- 실행 헬퍼: `run_server.py`
- Windows 스크립트: `scripts/run_server.cmd`, `scripts/run_tests.cmd`, `scripts/run_smoke.cmd`, `scripts/claude_code_install.cmd`
- 클라이언트 설정: `.mcp_example.json`, `.mcp_example_run_server.json`, `opencode.json`
- 트러블슈팅: `TROUBLESHOOTING.md`, `TROUBLESHOOTING_KO.md`

환경
- Windows venv 경로: `C:\Users\skyop\jaeho_template\dotenv_windows`
- 명령 실행 시 반드시 위 Python 사용.
- Claude Desktop은 격리된 환경에서 실행되므로 config에 `env`를 명시해야 함.

빌드 / 실행 / 테스트

서버 실행 (STDIO)
- 권장 (venv Python):
  - `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\04.OPENAPI_MCP_Server\run_server.py`
- 모듈 실행 (PYTHONPATH 필요):
  - `set PYTHONPATH=src && C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m seoul_culture_mcp.server`

테스트 (전체)
- 스크립트:
  - `scripts\run_tests.cmd`
- 직접 실행:
  - `set PYTHONPATH=src && C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m unittest discover -s tests`

단일 테스트 실행
- `set PYTHONPATH=src && C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe -m unittest tests.test_validation.ValidationTests.test_validate_date_str`

스모크 테스트 (STDIO client)
- `scripts\run_smoke.cmd`
- 직접 실행:
  - `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe scripts\stdio_smoke.py`

의존성 동기화
- `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\uv.exe sync`
- 참고: 스크립트는 `uv run --active --no-sync`를 사용.

Lint / format
- `pyproject.toml`에 별도 설정 없음.
- 기존 스타일을 유지하고 불필요한 포맷 변경은 피한다.

코딩 스타일 가이드

Imports
- 순서: 표준 라이브러리 → 서드파티 → 로컬 모듈.
- 그룹 간 빈 줄 1줄.
- 가능하면 `from __future__ import annotations` 사용.

Formatting
- 들여쓰기 4칸.
- 라인 길이는 기존 패턴을 따른다.
- 불필요한 주석 추가 금지.

Typing
- Python 3.11 타입 표기 사용 (`str | None`, `list[dict]` 등).
- MCP tool 시그니처는 명확하게 타입 지정.
- Pydantic 모델은 `ConfigDict(extra="allow")` 허용.

Naming
- 함수/변수: `snake_case`.
- MCP tool: 소문자 동사형 (예: `get_cultural_events`).
- 상수: ALL_CAPS.

에러 처리
- 입력 검증: validation helper 또는 tool에서 `ValueError`.
- API 오류: client에서 `SeoulAPIError`, tool 레이어에서 `RuntimeError`로 래핑.
- API 키 등 비밀 정보 출력 금지.

설정 및 환경변수
- 설정 로딩은 `settings.get_settings()`만 사용.
- 지원 env:
  - `SEOUL_API_KEY` (필수)
  - `SEOUL_API_BASE_URL` (선택)
  - `SEOUL_API_SERVICE` (선택)
  - `SEOUL_API_TYPE` (선택)
  - `SEOUL_API_TIMEOUT_SECONDS` (선택)

데이터 처리 규칙
- API 필드 이름/타입 유지:
  - `is_free`는 문자열 (`"무료"`/`"유료"`).
  - `lat`/`lot`는 문자열 유지.
  - `strtdate`/`end_date`는 epoch ms.
- list/get은 `description`, `data`, `meta` 반환.
- search는 `items`, `meta` 반환.

네트워킹
- `httpx.AsyncClient` + `settings.timeout_seconds` 사용.
- URL은 `build_request_url()`로 생성.
- HTTP 에러는 깔끔한 메시지로 전달.

테스트 가이드
- `unittest` 사용 (pytest 금지).
- 통합 테스트(`tests/test_integration.py`)는 `SEOUL_API_KEY` 필요.
- 테스트는 결정적이어야 하며, 네트워크는 통합 테스트만.

MCP tool 목록
- `get_cultural_events`: 페이징 조회 + 필터 옵션.
- `list_cultural_events`: `get_cultural_events` 별칭.
- `search_cultural_events`: 다중 페이지 검색 + 필터.
- `search_events_by_title`: 제목 키워드 검색.
- `search_events_by_date_range`: 기간 겹침 검색.
- `search_events_by_category`: 분류(codename) 필터, 무료 옵션.
- `get_free_events`: 무료 행사만 조회, 자치구 옵션.
- `get_event_by_location`: 자치구(guname) 필터.
- `get_event_field_map`: `DESCRIPTION` 매핑 반환.

클라이언트 설정
- Claude Desktop:
  - `.mcp_example.json` (`src/server.py` 실행)
  - `.mcp_example_run_server.json` (`run_server.py` 실행)
  - 설정 변경 후 완전 종료 후 재실행.
- OpenCode: `opencode.json`에 등록.
- Claude Code: `claude mcp add` 또는 `scripts/claude_code_install.cmd` 사용.

워크스페이스 위생
- 비밀정보 커밋 금지 (`.env`는 ignore).
- 샘플 데이터 파일은 변경/삭제하지 말 것.

에이전트 참고사항
- 엔트리포인트는 `run_server.py` 우선.
- `scripts/`의 헬퍼 스크립트를 사용.
- MCP tool 이름은 기존과 호환되게 유지.
