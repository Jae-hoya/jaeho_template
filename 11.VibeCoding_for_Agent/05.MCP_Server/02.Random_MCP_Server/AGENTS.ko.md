# AGENTS.md (한국어)

## 목적
- 이 저장소에서 작업하는 에이전트용 가이드입니다.
- 안전한 기본값과 반복 가능한 명령을 우선합니다.
- 실제 도구 상태와 문서를 일치시키고, 변경 시 이 파일을 갱신합니다.
- 사용자가 리팩터를 요청하지 않는 한 기존 패턴을 따릅니다.

## 저장소 요약
- 표준 입출력 기반으로 랜덤 숫자를 반환하는 Python MCP 서버입니다.
- 주요 실행 로직은 `random_mcp_server/server.py`에 있습니다.
- 모듈 실행과 콘솔 스크립트 진입점이 모두 제공됩니다.

## 주요 경로
- `pyproject.toml`: 프로젝트 메타데이터와 스크립트 진입점.
- `random_mcp_server/server.py`: MCP 서버, 도구 정의, 실행 루프.
- `random_mcp_server/__main__.py`: `python -m` 진입점.
- `random_mcp_server/__init__.py`: 패키지 버전.
- `README_PLAY.md`: 초기 요구사항 스냅샷.

## 설정
- Python 3.11+ 필요.
- 의존성 설치: `pip install -e .`.
- Python 외 추가 시스템 패키지는 필요하지 않습니다.

## 실행 / 빌드
- 모듈 실행: `python -m random_mcp_server`.
- 콘솔 스크립트: `random-mcp-server`.
- 파일 직접 실행: `python random_mcp_server/server.py`.
- 빌드는 미구성 상태(휠/소스 배포 도구 없음).
- 빌드 도구를 추가하면 정확한 명령을 여기에 문서화하세요.

## 린트 / 포맷
- 린트: 미구성.
- 포맷: 미구성.
- PEP 8 준수, 4칸 들여쓰기.
- 줄 길이는 약 100자를 목표로 합니다(강제 없음).
- `%`나 `.format()`보다 f-string을 선호합니다.
- 명시적 import를 사용하고 `*` import는 금지합니다.

## 테스트
- 테스트 러너: 미구성.
- 현재 테스트 없음.
- 단일 테스트 실행: N/A(테스트 프레임워크 없음).
- pytest 추가 시 권장 형태:
  `pytest path/to/test_file.py::test_name`.
- 난수 테스트는 재현성을 위해 시드를 고정합니다.

## 수동 스모크 테스트
- 서버 실행: `python -m random_mcp_server`.
- MCP 클라이언트로 `get_random_number` 호출.
- stdout이 유효한 JSON-RPC인지 확인하고 stderr에 로그가 출력되는지 확인.
- 반환 값이 1..100 범위인지 확인.

## MCP 프로토콜 규칙
- 서버 정의는 `mcp.server.Server` 사용.
- stdio 전송은 `mcp.stdio_server` 사용.
- 도구 등록은 `@server.list_tools()`.
- 호출 처리기는 `@server.call_tool()`.
- 텍스트 반환은 `mcp.types.TextContent` 사용.
- `inputSchema`는 최소화하고 `additionalProperties: False` 설정.

## 도구 동작 가이드
- 도구 이름은 안정적이며 `snake_case`.
- 도구 의미 변경 시 클라이언트/테스트도 함께 갱신.
- 필요하지 않으면 도구 핸들러에서 부작용을 피합니다.
- 구조화 출력이 필요 없으면 간단한 텍스트만 반환.

## 로깅 / 디버깅
- 디버그 출력은 stderr로만 보냅니다.
- 짧은 접두어 사용, 예: `[debug] message`.
- stdout에는 로그를 쓰지 않습니다(MCP JSON-RPC 전용).
- 반복 호출에서도 로그 스팸을 피합니다.

## import
- 순서: 표준 라이브러리, 서드파티, 로컬.
- 그룹 사이에는 빈 줄로 구분.
- `mcp.types`의 타입은 필요할 때 명시적으로 import.
- 패키지 모듈 간 순환 import를 피합니다.

## 포맷팅
- 들여쓰기는 4칸.
- 최상위 정의 사이에 빈 줄 1줄.
- 함수는 작고 집중되게 유지.
- 중첩을 줄이기 위해 early return을 선호.
- 공용 문자열은 모듈 상수로 관리.

## 타입
- 타입 힌트는 선택이지만 공개 함수는 권장.
- 내장 제네릭 사용(`list[str]`, `dict[str, Any]`).
- 작은 모듈에서는 과도한 타입 복잡도를 피합니다.

## 네이밍
- 모듈/함수/변수: `snake_case`.
- 상수: `UPPER_SNAKE_CASE`.
- 도구 이름은 설명적이고 안정적으로 유지.
- 식별자는 짧지만 명확하게.

## 에러 처리
- 알 수 없는 도구명은 `ValueError`로 처리.
- 오류 메시지는 사용자 친화적으로, 스택 트레이스는 출력하지 않음.
- 의미 있는 맥락을 추가할 수 있을 때만 예외를 감쌉니다.
- JSON-RPC 오류 포맷팅은 MCP 프레임워크에 위임.

## 난수 가이드
- 기본은 Python `random` 모듈 사용.
- 재현성이 필요하면 테스트/예제에서 시드를 고정.
- 전역 상태 변경으로 난수에 영향 주는 작업은 피합니다.

## 진입점
- 콘솔 엔트리: `random-mcp-server` -> `random_mcp_server.server:main`.
- 모듈 엔트리: `python -m random_mcp_server`.
- `main()`은 가볍게 유지하고 async `run_server()`로 위임.
- import 시점 부작용은 피합니다.

## 의존성
- 런타임 의존성: `mcp`.
- 사용 표준 라이브러리: `asyncio`, `random`, `sys`.
- 새 의존성은 최소화하고 `pyproject.toml`에 기록.

## 설정
- 환경 변수 필요 없음.
- 설정을 추가하면 `README_PLAY.md`와 이 파일에 문서화.
- 로컬 실행에 안전한 기본값 유지.
- stdout/stderr를 설정 용도로 사용하지 않습니다.

## 비동기 + IO
- 도구 핸들러는 async/non-blocking 유지.
- 요청 핸들러에서 긴 CPU 작업은 피합니다.
- 불가피한 블로킹은 `asyncio.to_thread` 사용.
- `main()` 밖에서 전역 이벤트 루프 생성 금지.

## Git / 작업공간 위생
- 요청하지 않은 변경은 제거하지 않습니다.
- `__pycache__` 같은 생성 파일은 커밋하지 않습니다.
- 변경 범위를 최소화하고 집중된 diff 유지.

## 문서
- 요구사항 변경 시에만 `README_PLAY.md` 업데이트.
- AGENTS.md는 실제 도구 상태와 일치하게 유지.
- 길고 장황한 설명보다 간결한 지침을 우선.

## Cursor / Copilot 규칙
- `.cursor/rules/`, `.cursorrules`, `.github/copilot-instructions.md` 없음.
- 추후 추가되면 이 섹션에 그대로 복사합니다.

## 변경 체크리스트
- 새 도구가 있으면 목록에 포함.
- 스키마가 도구 동작과 일치하는지 확인.
- stderr 로그 포맷이 일관적인지 확인.
- MCP 프로토콜 외 stdout 출력 금지.
- 배포 시 버전 문자열 업데이트.
