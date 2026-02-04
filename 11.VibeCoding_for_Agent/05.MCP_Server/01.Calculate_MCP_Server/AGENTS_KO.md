# AGENTS.md (한국어)

이 저장소는 산술 도구를 제공하는 최소한의 Python MCP 서버입니다.
수정/확장 시 아래 지침을 참고하세요.

## 리포지토리 구조
- `server.py`: MCP 서버 정의 및 도구 구현.
- `requirements.txt`: Python 의존성.
- `README_PLAY.md`: 프롬프트 메모(실행 파일 아님).

## 환경 가정
- 플랫폼: Windows (예시 경로는 백슬래시 사용).
- Python 3.11+ 권장 (asyncio + typing).
- MCP 프로토콜 지원을 위해 `mcp` 패키지 사용.

## 설정
- 리포지토리 루트에서 가상환경 생성/활성화.
- 의존성 설치: `pip install -r requirements.txt`.
- 별도의 빌드 단계 없음.

## 실행(수동)
- 서버 시작(표준입출력): `python server.py`.
- 서버는 stdio로 통신하며 TCP 포트를 열지 않음.
- 디버그 로그는 stderr로 `[debug]` 프리픽스와 함께 출력.

## 빌드 명령
- 빌드 시스템 없음.
- 추후 패키징 추가 시 `pyproject.toml` 또는 `setup.cfg` 사용.

## Lint/Format 명령
- 현재 린터/포매터 설정 없음.
- 추가한다면 `ruff` + `black` 조합 권장, 명령을 여기에 문서화.
- 예시(추가된 경우에만): `python -m ruff .`, `python -m black .`.

## 테스트 명령
- 테스트 러너/테스트 파일 없음.
- pytest를 추가했다면: `python -m pytest`.
- 단일 테스트 실행(pytest): `python -m pytest path\to\test_file.py::test_name`.

## MCP 동작 규칙
- 서버 이름 상수: `calculate-mcp-server`.
- 도구 등록: `@server.list_tools()` / `@server.call_tool()`.
- 도구 응답은 plain text를 담은 `TextContent`.
- 입력 검증은 `Decimal` 변환 실패 시 `ValueError` 사용.

## 도구 계약 가이드
- 각 도구는 `inputSchema`에 `type`, `properties`, `required` 정의.
- 숫자 입력은 `number` 스키마 타입 사용.
- 도구 `description`은 짧고 명령형으로.
- 도구 이름은 짧고 소문자 동사로(예: `add`, `multiply`).

## 로깅 가이드
- 모든 운영 로그는 `log_debug()`로 출력.
- 연산 전 입력값 로그.
- 연산 후 포맷된 결과 로그.
- 에러 조건은 예외 발생 전 로그.
- stderr로 `flush=True` 설정 필수.

## 숫자 처리
- 부동소수점 오차 방지를 위해 `Decimal` 사용.
- 입력 파싱은 `Decimal(str(value))` 사용.
- 전역 정밀도는 `getcontext().prec`로 유지.
- 출력은 `format(value, "f")`로 지수 표기 금지.

## 에러 처리
- 잘못된 도구/입력은 `ValueError`.
- 0으로 나누기: 먼저 로그 후 `ValueError`.
- 예외를 삼키지 말고 MCP 프레임워크로 전달.

## 비동기 패턴
- MCP 핸들러와 `main()`은 `async def`.
- 실행은 `asyncio.run(main())`.
- `main()` 최상단에서 `stdio_server()` 컨텍스트 사용.

## 임포트
- 표준 라이브러리 → 서드파티 → 로컬 순서.
- 동일 모듈의 여러 심볼만 예외적으로 한 줄 사용.
- 미사용 임포트 금지; stderr 로그용 `sys`는 유지.

## 포맷팅
- PEP 8 라인 길이 88 또는 100 허용.
- 4칸 들여쓰기, 탭 금지.
- 문자열은 쌍따옴표 사용(기존 코드와 일치).
- 최상위 정의 사이에 빈 줄 유지.

## 타입
- 공개 함수/핸들러에 명시적 타입 힌트 권장.
- `list[Tool]`, `list[TextContent]` 스타일 사용(Python 3.9+).
- 알 수 없는 입력은 `object`로 받고 검증.

## 네이밍 규칙
- 상수: `UPPER_SNAKE_CASE`.
- 함수: `lower_snake_case`.
- 변수: `lower_snake_case`.
- 도구 이름은 짧은 소문자 동사.

## 데이터 흐름
- 도구 인자는 `arguments` dict에서 읽기.
- 입력은 초기에 검증하고 빠르게 실패.
- 계산은 순수 함수 형태 유지(로깅 제외).

## 파일 구성
- MCP 서버 엔트리는 `server.py`.
- 모듈 추가 시 `src/` 패키지 생성 및 import 정리.
- 새 파일은 ASCII만 사용(도메인상 필요 시 예외).

## 도구 추가 시
- `list_tools()`에 새 `Tool` 등록.
- `call_tool()` 분기 로직 확장.
- 입력 검증 및 로깅 추가.
- 포맷 규칙이 늘면 `format_decimal()` 확장.

## 보안/안전
- 비밀키/토큰 등 민감 정보 로그 금지.
- 모든 입력은 신뢰하지 말 것.
- 도구 입력으로 쉘 명령 실행 금지.

## 문서화
- `README_PLAY.md`는 메모 용도(설정 파일 아님).
- 사용 예시는 필요 시 `README.md` 신설.

## Git 규칙
- 사용자가 요청할 때만 커밋.
- 관련 없는 파일은 건드리지 말 것.

## Cursor/Copilot 규칙
- `.cursor/rules`, `.cursorrules`, `.github/copilot-instructions.md` 없음.
- 추후 추가되면 이 섹션에 반영.

## 흔한 실수
- 입력/출력 로그 누락.
- 과학적 표기 반환(반드시 `format(..., "f")`).
- float 직접 파싱.
- `inputSchema` 없이 도구 추가.

## 향후 개선(선택)
- 각 도구/에러 케이스별 pytest 추가.
- ruff/black 설정 추가.
- 규모 증가 시 타입체커(mypy/pyright) 도입.

## 단일 테스트 실행 예시(pytest)
- `python -m pytest tests\test_math.py::test_divide_by_zero`

## stdio 실행 예시
- `python server.py`
- MCP 호환 클라이언트로 stdio 통신.

## 연락/엔트리 포인트
- 주요 엔트리: `server.py`.
- 의존성: `requirements.txt`.
