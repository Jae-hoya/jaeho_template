# 트러블슈팅 및 설정 정리

이 프로젝트는 FastMCP의 STDIO 전송 방식을 사용한다. Claude Desktop은 서버를 격리된 프로세스로 실행하므로 `command`, `args`, `env` 값을 명확하게 지정해야 한다.

## 1) Claude Desktop 최종 설정
위치(Windows): `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "seoul-culture-events": {
      "command": "C:\\Users\\skyop\\jaeho_template\\dotenv_windows\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\skyop\\jaeho_template\\11.VibeCoding_for_Agent\\05.MCP_Server\\04.OPENAPI_MCP_Server\\src\\server.py"
      ],
      "env": {
        "SEOUL_API_KEY": "4e4666566e73656c38314a4e4d6345",
        "SEOUL_API_BASE_URL": "http://openapi.seoul.go.kr:8088",
        "SEOUL_API_SERVICE": "culturalEventInfo",
        "SEOUL_API_TYPE": "json",
        "SEOUL_API_TIMEOUT_SECONDS": "10"
      }
    }
  }
}
```

메모:
- 위 설정은 `.mcp_example.json`에도 동일하게 저장되어 있다.
- `src` 경로를 보장하는 단일 엔트리포인트를 쓰고 싶다면 `.mcp_example_run_server.json`을 사용한다.
- 설정을 바꾼 뒤에는 Claude Desktop을 완전히 종료했다가 다시 실행해야 한다.

## 2) run_server.py (명확한 실행 엔트리포인트)
`run_server.py`는 `src` 경로를 `sys.path`에 추가한 뒤 FastMCP 서버를 실행하는 얇은 래퍼다. 로컬 테스트에서 단일 엔트리포인트로 쓰기 좋다.

가상환경 Python으로 직접 실행:
```bash
C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\04.OPENAPI_MCP_Server\run_server.py
```

## 3) 자주 발생하는 오류와 해결

### Claude Desktop에서 도구가 안 보임
- config JSON이 유효한지 확인
- `command`, `args` 경로가 절대 경로인지 확인 (백슬래시 이스케이프 포함)
- Claude Desktop 완전히 종료 후 재실행

### ModuleNotFoundError: fastmcp
- venv Python을 사용하지 않는 경우다. config의 `command`가 아래 경로인지 확인:
  `C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe`

### SEOUL_API_KEY is required
- Claude Desktop은 쉘 환경변수를 상속하지 않는다.
- config의 `env` 블록에 `SEOUL_API_KEY`가 있는지 확인

### HTTP 401/403 또는 빈 응답
- API 키가 유효한지 확인
- `SEOUL_API_SERVICE`는 `culturalEventInfo`, `SEOUL_API_TYPE`는 `json`인지 확인

### 서버는 뜨는데 데이터가 없음
- `start_index`, `end_index` 값이 잘못됐을 수 있다.
- `start_index=1`, `end_index=5`로 먼저 테스트

## 4) OpenCode MCP 등록
OpenCode는 `opencode.json`의 MCP 설정을 읽는다.

다음과 같이 서버 항목을 추가한다(실제 API 키 사용):
```json
{
  "mcp": {
    "seoul-culture-events": {
      "type": "local",
      "command": [
        "C:\\Users\\skyop\\jaeho_template\\dotenv_windows\\Scripts\\python.exe",
        "C:\\Users\\skyop\\jaeho_template\\11.VibeCoding_for_Agent\\05.MCP_Server\\04.OPENAPI_MCP_Server\\src\\server.py"
      ],
      "enabled": true
    }
  }
}
```

메모:
- `.mcp_example_run_server.json`을 쓰려면 `args` 경로를 `run_server.py`로 바꾼다.
- OpenCode는 셸 환경변수를 상속하므로 `SEOUL_API_KEY`를 환경변수로 두거나, 필요 시 래퍼 스크립트를 사용한다.

## 5) Claude Code MCP 등록
Claude Code는 `claude mcp add`로 STDIO 서버를 등록한다.

예시(환경변수 명시):
```bash
claude mcp add seoul-culture-events \
  -e SEOUL_API_KEY=YOUR_SEOUL_API_KEY \
  -e SEOUL_API_BASE_URL=http://openapi.seoul.go.kr:8088 \
  -e SEOUL_API_SERVICE=culturalEventInfo \
  -e SEOUL_API_TYPE=json \
  -e SEOUL_API_TIMEOUT_SECONDS=10 \
  -- C:\Users\skyop\jaeho_template\dotenv_windows\Scripts\python.exe \
  C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\04.OPENAPI_MCP_Server\src\server.py
```

메모:
- 단일 엔트리포인트가 필요하면 `run_server.py`로 바꿔서 실행한다.
- `claude --version`이 되지 않으면 Claude Code CLI가 설치되지 않은 상태다.
