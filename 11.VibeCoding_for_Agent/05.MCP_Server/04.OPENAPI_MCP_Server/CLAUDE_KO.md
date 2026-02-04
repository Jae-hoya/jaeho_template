# CLAUDE_KO.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소에서 작업할 때 참고할 가이드입니다.

## 프로젝트 개요

서울 열린데이터 광장 API (`http://openapi.seoul.go.kr:8088/culturalEventInfo`)의 문화행사 정보를 Model Context Protocol을 통해 제공하는 FastMCP 서버입니다. 제목, 날짜 범위, 카테고리, 지역, 유무료 등 다양한 조건으로 문화행사를 조회할 수 있는 9개의 툴을 제공합니다.

## 개발 명령어

### MCP 서버 실행

**Stdio 모드 (Claude Desktop 등 MCP 클라이언트용)**:
```bash
uv run python src/seoul_culture_mcp/server.py
```

설치된 스크립트로 실행:
```bash
uv run seoul-culture-mcp
```

### 테스트

전체 테스트 실행:
```bash
uv run pytest
```

특정 테스트 파일 실행:
```bash
uv run pytest tests/test_validation.py
```

상세 출력으로 테스트 실행:
```bash
uv run pytest -v
```

### 패키지 관리

의존성 추가:
```bash
uv add <패키지명>
```

의존성 동기화:
```bash
uv sync
```

## 아키텍처

### 핵심 컴포넌트

**`src/seoul_culture_mcp/server.py`**: MCP 서버의 메인 진입점. 9개의 툴 함수가 `@mcp.tool` 데코레이터로 정의되어 있으며, 다양한 검색 기능을 제공합니다. 공통 헬퍼 함수 `_search_events()`를 사용하여 API 전반에 걸친 페이지네이션 및 필터링을 처리합니다.

**`src/seoul_culture_mcp/clients/seoul_api.py`**: 서울시 OpenAPI HTTP 클라이언트. 다음 기능을 처리합니다:
- 경로 파라미터로 URL 구성 (KEY/TYPE/SERVICE/START_INDEX/END_INDEX)
- 쿼리 파라미터 처리 (CODENAME, TITLE, DATE)
- 응답 파싱 및 에러 처리
- 원본 페이로드와 실제 요청 URL 반환

**`src/seoul_culture_mcp/settings.py`**: 환경 변수를 사용한 설정 관리. `get_settings()`를 통한 싱글톤 패턴. python-dotenv로 `.env` 파일 로드.

**`src/seoul_culture_mcp/models.py`**: API 응답 검증을 위한 Pydantic 모델 (EventResponse 구조).

**`src/seoul_culture_mcp/utils/validation.py`**: 입력 검증 및 클라이언트 측 필터링 헬퍼. 제목, 날짜 범위, 지역, 무료 여부로 행사를 매칭합니다.

### 데이터 흐름

1. MCP 툴이 사용자 파라미터를 받음
2. 툴이 `utils/validation.py`를 사용하여 입력 검증
3. `_search_events()`가 페이지네이션과 필터링을 조율
4. `clients/seoul_api.py`가 서울시 API에 HTTP 요청
5. `extract_description_data()`를 사용하여 응답 파싱
6. 클라이언트 측 필터링 적용 (API가 지원하지 않는 필터용)
7. 툴이 `items`와 `meta` 필드가 포함된 구조화된 결과 반환

### 주요 아키텍처 결정사항

**클라이언트 측 필터링**: 서울시 API는 쿼리 파라미터 지원이 제한적입니다. `guname`(자치구), `is_free`, 퍼지 제목 매칭 같은 필터는 API에서 페이지를 가져온 후 메모리 내에서 필터링합니다.

**페이지네이션 전략**: API 요청에는 `page_size` 파라미터를 사용하고, `limit` 개수의 항목이 매칭되거나 더 이상 데이터가 없을 때까지 페이지를 계속 가져옵니다.

**이중 인터페이스**: 저수준 페이지네이션 툴(`get_cultural_events` - start/end index 사용)과 고수준 검색 툴(`search_*` - limit/page_size 사용) 모두 제공합니다.

**에러 처리**: 클라이언트 레이어의 `SeoulAPIError` 예외를 툴 레이어에서 `RuntimeError`로 래핑하여 더 나은 MCP 에러 메시지를 제공합니다.

## 설정

필수 환경 변수 (`.env` 파일에 설정):
```
SEOUL_API_KEY=발급받은_API_키
```

선택적 환경 변수:
```
SEOUL_API_BASE_URL=http://openapi.seoul.go.kr:8088
SEOUL_API_SERVICE=culturalEventInfo
SEOUL_API_TYPE=json
SEOUL_API_TIMEOUT_SECONDS=10.0
```

## MCP 클라이언트 설정

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
        "SEOUL_API_KEY": "발급받은_API_키"
      }
    }
  }
}
```

## 테스트 전략

테스트는 `tests/` 디렉토리에 있으며 다음을 커버합니다:
- **test_validation.py**: 입력 검증 및 필터 매칭 로직
- **test_extract.py**: 응답 파싱 및 데이터 추출
- **test_integration.py**: 엔드-투-엔드 툴 실행 (API 키 필요)

통합 테스트는 `SEOUL_API_KEY`가 설정되지 않은 경우 건너뜁니다.

## 서울시 API 상세

**응답 구조**:
- 최상위 키: `DESCRIPTION` (한글 필드 라벨)과 `DATA` (행사 배열)
- 행사는 소문자 필드명 사용 (예: `title`, `codename`, `guname`)

**날짜 필드**:
- `date`: 범위를 포함한 표시 문자열 (예: "2026-05-15~2026-05-17")
- `strtdate`/`end_date`: Unix epoch 밀리초
- `DATE` 쿼리 파라미터: YYYY-MM-DD 형식의 단일 날짜

**유무료 표시**: `is_free` 필드는 불린이 아닌 문자열 ("무료" 또는 "유료")입니다.

**좌표**: `lat`와 `lot`는 숫자가 아닌 문자열입니다.

## 패키지 구조

pyproject.toml에서 패키지명은 `seoul-culture-mcp`이지만, Python 패키지명은 `seoul_culture_mcp` (하이픈이 아닌 언더스코어)입니다. 진입점 스크립트는 `seoul-culture-mcp`로 등록되어 있습니다.
