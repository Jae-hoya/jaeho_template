# PRD: Playwright MCP Client

## 목적
Playwright MCP 서버와 통신하여 웹 브라우저 자동화 작업을 수행하는 Python CLI 클라이언트 구현

## 핵심 기능

### 1. MCP Server 연결
- Playwright MCP 서버와 stdio 방식으로 연결
- 서버로부터 사용 가능한 tool 목록 가져오기

### 2. LLM 통합
- Anthropic Claude API를 사용하여 사용자 요청 처리
- MCP tool을 Claude function calling으로 연결
- 시스템 프롬프트: MCP tool 사용법 및 웹 자동화 작업 가이드 제공

### 3. Tool 실행 및 로깅
- Claude가 선택한 tool 실행
- 실행된 tool 이름과 파라미터를 콘솔에 출력
- tool 실행 결과를 Claude에게 전달

### 4. CLI 인터페이스
- 간단한 대화형 CLI
- 사용자 입력 → Claude 처리 → Tool 실행 → 결과 출력 루프

### 5. 테스트
- MCP 서버 연결 테스트
- Tool 목록 조회 테스트
- Tool 실행 테스트 (mock)

## 기술 스택
- Python 3.10+
- MCP Python SDK
- uv (패키지 관리)
- Anthropic SDK
- pytest (테스팅)

## 비기능 요구사항
- 단순하고 읽기 쉬운 코드 구조
- 핵심 기능만 구현 (과도한 추상화 지양)
- 에러 처리는 필수적인 부분만 포함

## 제외 사항
- GUI 인터페이스
- 복잡한 설정 관리
- 다중 MCP 서버 연결
- 대화 히스토리 저장
