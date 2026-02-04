# PRD: Playwright MCP Client

## 1. 프로젝트 개요
Playwright MCP 서버와 Context7 MCP 서버를 활용하는 Python CLI 기반 MCP 클라이언트 구현

## 2. 목적
- Playwright MCP를 통한 브라우저 자동화
- Context7 MCP를 통한 최신 라이브러리 문서 조회
- 단순하고 핵심 기능에 집중한 MCP 클라이언트 제공

## 3. 기술 스펙
- **Python**: 3.10+
- **MCP SDK**: [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
- **환경변수 관리**: jaeho_template의 dotenv 패키지
- **통신 방식**: stdio (Playwright), SSE (Context7)

## 4. 핵심 기능 요구사항

### 4.1 MCP 서버 연결
- Playwright MCP 서버 연결 (npx @playwright/mcp@latest)
- Context7 MCP 서버 연결 (필수)
- 서버 초기화 및 연결 관리

### 4.2 CLI 인터페이스
- 대화형 CLI로 사용자 입력 받기
- 자연어 명령어 처리
- 실행 결과 출력

### 4.3 Tool 사용 추적
- 사용된 MCP tool 이름 출력
- Tool 호출 파라미터 로깅
- 실행 결과 표시

### 4.4 AI 에이전트 통합
- LLM을 통한 자연어 → MCP tool 호출 변환
- MCP 서버의 tool만 사용 (직접 Python 코드 실행 금지)
- 시스템 프롬프트 기반 동작

## 5. 시스템 프롬프트 요구사항

### 5.1 역할 정의
- MCP 서버의 tool만 사용하는 에이전트
- Playwright와 Context7 tool 활용 전문가

### 5.2 동작 규칙
- 사용 가능한 tool 목록 파악
- 사용자 요청에 적합한 tool 선택
- Tool 사용 내역 명확히 전달
- 에러 발생 시 사용자 친화적 메시지 제공

### 5.3 제약사항
- MCP tool 외 직접 코드 실행 금지
- 사용 가능한 tool 범위 내에서만 작업
- 불가능한 요청은 명확히 안내

## 6. 테스트 요구사항

### 6.1 단위 테스트
- MCP 서버 연결 테스트
- Tool 목록 조회 테스트
- Tool 호출 테스트

### 6.2 통합 테스트
- Playwright tool 사용 시나리오 (브라우저 열기, 스냅샷 등)
- Context7 tool 사용 시나리오 (문서 조회)
- 에러 처리 시나리오

## 7. 구현 원칙
- **단순성**: 핵심 기능만 구현, 과도한 추상화 지양
- **명확성**: Tool 사용 내역을 명확히 출력
- **안정성**: 에러 처리 및 로깅
- **테스트 가능성**: 각 기능별 테스트 코드 작성

## 8. 구현 TODO

### Phase 1: 기본 구조
- [ ] 프로젝트 구조 설정 (pyproject.toml, 디렉토리)
- [ ] MCP 클라이언트 base 클래스 구현
- [ ] Playwright MCP 서버 연결 구현
- [ ] Context7 MCP 서버 연결 구현

### Phase 2: 핵심 기능
- [ ] Tool 목록 조회 기능
- [ ] Tool 호출 기능
- [ ] Tool 사용 추적 및 로깅
- [ ] 시스템 프롬프트 작성

### Phase 3: CLI 인터페이스
- [ ] CLI 대화형 인터페이스 구현
- [ ] LLM 통합 (Claude API)
- [ ] Tool 호출 결과 포맷팅

### Phase 4: 테스트
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] 사용 예제 작성

## 9. 참고사항
- Playwright MCP는 npx를 통해 실행
- Context7는 필수로 포함
- 환경변수는 .env 파일로 관리
- 로그는 간결하고 명확하게
