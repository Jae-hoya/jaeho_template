# 한국어 버전

## 목표
`seoul-culture-events-api.md`의 스펙을 기준으로 서울시 문화행사 API를 조회하는 도구를 제공하는 FastMCP 서버를 Python으로 구축한다. 패키지 관리는 `uv`를 사용하고, 가상환경 경로는 지정된 경로를 사용한다.

## 제약 조건
- 언어: Python
- 프레임워크: FastMCP 서버
- 통신: stdio (`mcp.run()` 기본)
- 패키지 매니저: `uv`
- 가상환경 경로: `C:\Users\skyop\jaeho_template\dotenv_windows`
- FastMCP 문서는 Context7로 확인

## 기술 스택
- 언어: Python
- MCP 프레임워크: FastMCP
- HTTP 클라이언트: httpx
- 환경 변수 로딩: python-dotenv
- 패키지 매니저: uv

## 입력
- API 스펙: `seoul-culture-events-api.md`
- Base URL: `http://openapi.seoul.go.kr:8088`
- Endpoint: `GET /{KEY}/{TYPE}/{SERVICE}/{START_INDEX}/{END_INDEX}/`
- 선택 쿼리 파라미터: `CODENAME`, `TITLE`, `DATE`

## 출력
- API의 JSON 응답(`DESCRIPTION`, `DATA`)을 그대로 반환하는 MCP 도구

## 환경 변수
- `SEOUL_API_KEY` (필수)
- `SEOUL_API_BASE_URL` (선택, 기본값 `http://openapi.seoul.go.kr:8088`)
- `SEOUL_API_TYPE` (선택, 기본값 `json`)
- `SEOUL_API_SERVICE` (선택, 기본값 `culturalEventInfo`)

## MCP 도구 설계
도구: `list_cultural_events`

입력:
- `start_index` (int, 필수, >= 1)
- `end_index` (int, 필수, >= start_index)
- `codename` (str, 선택)
- `title` (str, 선택)
- `date` (str, 선택, YYYY-MM-DD)

요청 매핑:
- 경로 세그먼트 순서: `KEY`, `TYPE`, `SERVICE`, `START_INDEX`, `END_INDEX`
- 선택 필터는 쿼리 파라미터: `CODENAME`, `TITLE`, `DATE`

출력:
- `DESCRIPTION`, `DATA`를 포함한 JSON 응답을 그대로 반환

검증:
- `start_index < 1` 또는 `end_index < start_index`는 오류

오류 처리:
- HTTP 오류 및 JSON 파싱 오류를 명확한 메시지로 전달

## 구현 단계
1. `uv`로 `pyproject.toml` 생성 및 의존성 추가: `fastmcp`, `httpx`, `python-dotenv`
2. `.env.example` 생성(`SEOUL_API_KEY=`) 및 `.gitignore`에 `.env` 추가
3. `server.py` 구현:
   - `FastMCP(name="SeoulCultureEvents")`
   - `@mcp.tool`로 `list_cultural_events` 등록
   - `httpx`로 API 호출
   - `__main__`에서 `mcp.run()`으로 stdio 실행
4. `README.md`에 설치/실행 방법 정리

## 프로젝트 구조
```
.
├─ PLAN.md
├─ PLAN_KO.md
├─ README.md
├─ server.py
├─ pyproject.toml
├─ .env.example
└─ .gitignore
```

## 검증
- `python server.py`로 실행(기본 stdio)
- MCP stdio 클라이언트로 도구 호출 후 JSON 응답 확인

## 참고 (Context7)
- FastMCP 서버 문서: https://gofastmcp.com/servers/server#the-fast-mcp-server
