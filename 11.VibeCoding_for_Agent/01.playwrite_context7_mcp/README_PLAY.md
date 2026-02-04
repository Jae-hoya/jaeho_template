### playwright 
claude mcp add playwright npx @playwright/mcp@latest -s project

- 웹 브라우저 자동화 및 테스트
- 팀 전체가 동일한 테스트 환경 사용
- E2E 테스트 시나리오 작성 및 실행

### Context7
claude mcp add --transport http context7 https://mcp.context7.com/mcp -s user

- Context7이 최신 라이브러리 문서를 가져와 AI가 정확한 정보로 개발 가능

`{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "linear": {
      "transport": {
        "type": "sse",
        "url": "https://mcp.linear.app/sse"
      }
    }
  }
}`
---
### PRD(Product Requirements Document) 

AI 에이전트는 사람이 아니기 때문에 필요한 모든 맥락을 명확하게 제공해야 합니다.

토큰을 많이 사용하기 때문에, 구현할 때 사용할 코드는 많이 부족하다. 
따라서 문서로 PRD파일을 만들고, 그 문서를 바탕으로 Clear해서 새로운 세션을 열어서 다시 구현을 시키는것이 좋다.

- 나쁜 예시:
MCP client를 만들어줘

- 좋은 예시:
Python MCP SDK를 사용해서 stdio 방식으로 통신하는
weather-api MCP server에 연결하는 client를 구현해줘.
connect, list_tools, call_tool 메서드 필요.

1. 시작!
입력:
playwright mcp를 사용하는 mcp client 구현하는 PRD 문서로 작성해줘. PRD2.md

스펙:
- Python 3.10+
- mcp Python SDK https://github.com/modelcontextprotocol/python-sdk
- jaeho_template에 있는 dotenv 패키지 사용

요구사항:
- mcp server를 잘 사용할 수 있는 시스템 프롬프트 작성
- python cli로 동작
- 어떤 tool을 사용했는지 출력
- mcp server의 tool 만 사용하기
- 테스트코드 작성
- 핵심 요구사항만 수행할 수 있도록 단순한 형태로 구현

주의:
- PRD는 핵심만 간략하게
- PRD에는 코드 작성하지 않기
- todo 작성

context7 mcp 반드시 사용해줘

---


2. /clear 후, 
입력:
@PRD2.md 문서를 읽고 구현해줘 

(art + t로 thinking 모드 키기. meta가 왼쪽 art였다. 2가 잘됐으니 2를 가지고 한다.)
PRD를 하나씩 보면서 고칠수도 있지만, 모든 permession을 준다. 문제가 있으면 새로 하면 되니까! 구현버전에서는 버전을 업그레이드 시켰다.

3. 다른 calude창에서 
입력:
@PRD2.md 를 읽어줘

요청한것과 달라진것이 없는지 확인한다. 
나의 경우에는 USAGE.md에 되는 경우도 있다.

4. 여기서 생성된것은 test, src, .env.example, README.md ...

5. 입력:
openai키로 실행할거야. .env에 openai api key 저장했어. 실제 동작 해줘.

나는 엔트로픽 api 요금이 없기 때문에, openai로 변경해서 실행한다.

6. 오류가 생기면, 
입력:
다른 클로드 창에서 mcp server playwright가 제대로 동작을 안하는 것 같은데, 확인좀 해줘.

만약 오류 코드가 있다면, 이 내용을 복붙해서 확인해달라고 할 수도 있다.


