# Playwright MCP Client

Playwright MCP 서버와 통신하여 웹 브라우저 자동화 작업을 수행하는 Python CLI 클라이언트입니다.

## 특징

- Playwright MCP 서버와 stdio 통신
- Claude API를 통한 자연어 기반 웹 자동화
- MCP tool을 Claude function calling으로 통합
- 실행된 tool과 파라미터를 콘솔에 출력
- 간단한 대화형 CLI 인터페이스

## 요구사항

- Python 3.10+
- Node.js (Playwright MCP 서버 실행용)
- Anthropic API Key

## 설치

1. 저장소 클론 및 디렉토리 이동

```bash
cd playwrite_context7_mcp
```

2. uv를 사용한 의존성 설치

```bash
uv pip install -e .
```

개발 의존성 포함 설치:

```bash
uv pip install -e ".[dev]"
```

3. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 API 키를 설정합니다:

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 Anthropic API 키를 입력:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## 사용법

CLI 실행:

```bash
python src/main.py
```

실행 후 대화형 인터페이스가 시작됩니다:

```
Playwright MCP Client
==================================================

Connecting to MCP server: npx -y @modelcontextprotocol/server-playwright
Connected! Found XX tools

==================================================
Ready! Type your requests below (or 'quit' to exit)
==================================================

You:
```

### 명령어

- 일반 요청: 웹 자동화 작업을 자연어로 입력
- `reset`: 대화 기록 초기화
- `quit`, `exit`, `q`: 프로그램 종료

### 사용 예시

```
You: Go to https://example.com and take a screenshot

[Tool Call] browser_navigate
[Parameters] {
  "url": "https://example.com"
}
[Result] Success

[Tool Call] browser_take_screenshot
[Parameters] {
  "filename": "screenshot.png"
}
[Result] Success