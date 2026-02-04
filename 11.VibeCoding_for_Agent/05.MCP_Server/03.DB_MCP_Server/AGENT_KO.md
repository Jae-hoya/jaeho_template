# AGENT_KO.md

## 목적
- 이 저장소에서 작업하는 에이전트용 가이드입니다.
- 안전한 기본값, 명시적 검증, 예측 가능한 출력값을 우선합니다.
- 실제 도구 상태와 문서를 일치시키고, 변경 시 이 파일을 갱신합니다.

## 저장소 요약
- stdio 전송 기반의 PostgreSQL MCP 서버입니다.
- 읽기 전용 SQL 쿼리와 안전한 후보자 업데이트를 지원합니다.
- 공개 테이블의 스키마 리소스를 제공합니다.

## 주요 경로
- `server.py`: MCP 서버, 도구/리소스 핸들러, asyncpg 풀.
- `pyproject.toml`: 의존성과 콘솔 스크립트.
- `README.md`: 사용 가이드.
- `insert_candidates.sql`: 라이브 DB 기준 시드.
- `candidates.csv`, `candidates.json`: 라이브 DB 스냅샷.

## 설정
- Python 3.11+ 필요.
- 개발 모드 설치: `pip install -e .`
- 의존성: `mcp`, `asyncpg`.

## 실행 명령
- stdio 서버: `python server.py "postgresql://user:pass@host:5432/db"`
- 또는 환경 변수: `DATABASE_URL`, `POSTGRES_URL`, `PG_URL`.
- 콘솔 스크립트(설치 후): `recursive-mcp-server <db_url>`.

## 빌드 / 린트 / 테스트
- 빌드: 미구성.
- 린트: 미구성.
- 포맷: 미구성.
- 테스트: 미구성.

## 단일 테스트 명령 (테스트 추가 시)
- Pytest 예시: `python -m pytest path\to\test_file.py::test_name`

## MCP 도구
- `query`: 읽기 전용 SQL만 허용; 단일 문장; JSON 리스트 반환.
- `update_candidate`: `position`, `skills`, `company`만 변경 가능; `id` 필수.
- `update_candidate`는 `position` 변경 시 `category`를 자동 유도합니다.

## 도구 계약 가이드
- `inputSchema`에 `type`, `properties`, `required`를 명시합니다.
- 입력은 항상 `additionalProperties: false`로 제한합니다.
- 도구 이름은 안정적으로 유지(변경 시 클라이언트 영향).
- 데이터 응답은 `TextContent`에 JSON 문자열로 반환합니다.
- datetime은 `json.dumps(..., ensure_ascii=False, default=str)`로 처리합니다.

## 리소스 동작
- `list_resources`는 public 테이블만 나열합니다.
- 리소스 `name`은 안정적이고 설명적으로 지정합니다(예: `<table>_schema`).
- 리소스 `uri`는 절대 경로이며 클라이언트가 파싱 가능해야 합니다.
- `read_resource`는 컬럼 메타데이터 JSON 배열을 반환합니다.
- 잘못된 URI는 `ValueError`로 거부합니다.

## MCP 리소스
- public 테이블 스키마를 리소스로 제공합니다.
- URI 형식: `postgres://<user>@<host>:<port>/<db>/<table>/schema`.
- `read_resource` 결과는 `column_name`, `data_type` 포함.

## DB 규칙
- 업데이트는 파라미터화된 SQL만 사용(문자열 삽입 금지).
- `query`는 다중 SQL 문장 금지.
- 읽기 전용 토큰: `SELECT`, `WITH`, `SHOW`, `EXPLAIN`, `VALUES`, `TABLE`.
- 데이터 변경은 `public.candidates` + `update_candidate`로만 허용.

## 출력 포맷
- `query` 결과는 JSON 배열로 반환.
- 가능한 한 필드 순서를 안정적으로 유지.
- 숫자 값은 문자열로 바꾸지 않음(id 포함).
- datetime은 `default=str`로 변환(ISO 유사 출력).
- 연결 문자열은 로그/응답에 포함하지 않음.

## 로깅 가이드
- stderr로만 로그 출력(stdout 금지).
- `[debug]` 접두어 사용.
- 도구 호출/결과는 기록하되 과도한 로그는 피함.
- 비밀정보(연결 문자열, 토큰, 비밀번호) 로그 금지.

## 에러 처리
- 잘못된 입력/알 수 없는 도구는 `ValueError`.
- 누락/형식 오류는 즉시 실패.
- 오류 메시지는 짧고 사용자 친화적으로.
- JSON-RPC 에러 포맷은 MCP 프레임워크에 위임.

## 코드 스타일
- Import 순서: 표준 라이브러리 → 서드파티 → 로컬, 그룹 사이 빈 줄.
- 들여쓰기 4칸, 줄 길이 100자 내외.
- 문자열은 큰따옴표 사용.
- 미사용 import, import 시점 부작용 금지.

## 타입
- 공개 함수/핸들러는 타입 힌트 권장.
- 내장 제네릭 사용(`list[str]`, `dict[str, Any]`).
- 복잡한 제네릭은 피하고 단순하게 유지.

## 네이밍
- 상수: `UPPER_SNAKE_CASE`.
- 함수/변수: `snake_case`.
- 도구 이름: 짧고 소문자, 안정적으로 유지.

## 비동기 패턴
- MCP 도구/리소스 핸들러는 async 유지.
- 요청 핸들러에서 블로킹 작업 금지.
- `asyncpg` 풀은 `main()`에서 생성 후 종료 시 close.

## 성능/신뢰성
- 필터는 인덱스 컬럼 우선(`id`, `category`, `company`).
- 장시간 쿼리는 피함.
- 풀 크기는 기본 5 유지, 필요 시 조정.
- 검증 실패는 즉시 반환.
- `query`는 `READ ONLY` 트랜잭션 보장.

## 보안/개인정보
- 모든 입력은 신뢰하지 않습니다.
- 읽기 전용 가드 밖의 임의 SQL 실행 금지.
- 로그에서 개인정보 노출 금지.

## 구성
- Claude Desktop은 작업 디렉터리가 불명확할 수 있으므로 절대 경로 사용.
- 데스크톱 클라이언트에서 DB URL은 `env`로 전달.

## 디버깅 팁
- 설정 JSON 유효성 먼저 확인.
- 연결 실패 시 실행 파일 경로가 절대 경로인지 확인.
- stderr의 `[debug]` 로그 확인.
- Claude Desktop은 설정 변경 후 재시작 필요.
- `SELECT 1`로 연결 여부 최소 확인.

## 데이터 동기화 워크플로우
- DB를 먼저 업데이트한 뒤 `insert_candidates.sql`을 재생성.
- `candidates.csv`, `candidates.json`은 DB 스냅샷으로 재생성.
- `created_at`은 유지하고 임의 수정/백필 금지.
- 수동 변경 사항은 커밋 메시지나 변경 기록에 명시.

## 수정 금지 파일
- `README_PLAY.md`는 프롬프트 로그이며 요구사항 변경 시에만 수정.

## Cursor / Copilot 규칙
- 이 저장소에는 `.cursor/rules`, `.cursorrules`, `.github/copilot-instructions.md`가 없습니다.

## 변경 체크리스트
- 새 도구 추가 시 목록 갱신.
- `additionalProperties: false` 유지.
- 읽기 전용 가드 변경 시 동작 검증.
- UPDATE는 파라미터화 유지.
- 동작 변경 시 `README.md` 갱신.
- 시드/스냅샷(`insert_candidates.sql`, `candidates.csv`, `candidates.json`) 동기화.
