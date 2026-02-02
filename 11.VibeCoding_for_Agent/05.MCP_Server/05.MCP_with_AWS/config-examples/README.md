# MCP Client Configuration Examples

이 디렉토리에는 Seoul Open Data MCP Server를 다양한 MCP 클라이언트에서 사용하기 위한 설정 예제가 포함되어 있습니다.

## 📋 설정 파일 목록

1. **claude-desktop-config.json** - Claude Desktop 앱용 설정
2. **claude-code-config.json** - Claude Code CLI용 설정
3. **cline-mcp-settings.json** - Cursor/Cline용 설정

## 🔑 API 키 발급

두 개의 API 키가 필요합니다:

1. **서울 문화행사 API 키** (`SEOUL_CULTURE_API_KEY`)
2. **서울 여성가족 이벤트 API 키** (`SEOUL_WOMEN_API_KEY`)

### API 키 발급 방법

1. [서울 열린데이터 광장](https://data.seoul.go.kr/) 접속
2. 회원가입 및 로그인
3. **오픈API** → **인증키 신청** 메뉴 선택
4. 다음 서비스에 대한 API 키 신청:
   - **문화행사정보** (culturalEventInfo)
   - **서울여성플라자 이벤트** (SeoulWomenPlazaEvent)

## 📍 설정 파일 위치

### 1. Claude Desktop

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```powershell
%APPDATA%\Claude\claude_desktop_config.json
```

**설정 방법:**
```bash
# 1. 설정 파일 위치로 이동 (Windows 예시)
cd %APPDATA%\Claude

# 2. 예제 파일 복사
copy C:\Users\skyop\jaeho_template\11.VibeCoding_for_Agent\05.MCP_Server\05.MCP_with_AWS\config-examples\claude-desktop-config.json claude_desktop_config.json

# 3. 파일 편집하여 API 키 입력
notepad claude_desktop_config.json
```

### 2. Claude Code (CLI)

**설정 파일 위치:**
```bash
~/.claude/config.json
```

**설정 방법:**
```bash
# 1. .claude 디렉토리 생성 (없는 경우)
mkdir -p ~/.claude

# 2. 예제 파일 복사
cp config-examples/claude-code-config.json ~/.claude/config.json

# 3. 파일 편집하여 API 키 입력
vi ~/.claude/config.json
```

### 3. Cursor/Cline

**설정 파일 위치:**
```
프로젝트 루트 디렉토리의 cline_mcp_settings.json
```

**설정 방법:**
```bash
# 1. 프로젝트 루트로 이동
cd your-project-root

# 2. 예제 파일 복사
cp path/to/config-examples/cline-mcp-settings.json ./cline_mcp_settings.json

# 3. Cursor에서 파일 열어 API 키 입력
```

## ⚙️ 설정 파일 수정

각 설정 파일에서 다음 부분을 수정해야 합니다:

### 1. 절대 경로 수정

```json
{
  "args": [
    "--directory",
    "여기에_실제_프로젝트_절대_경로_입력"
  ]
}
```

**Windows 경로 예시:**
```json
"C:/Users/YourName/projects/seoul-opendata-mcp-server"
```

**macOS/Linux 경로 예시:**
```json
"/Users/YourName/projects/seoul-opendata-mcp-server"
```

### 2. API 키 입력

```json
{
  "env": {
    "SEOUL_CULTURE_API_KEY": "발급받은_문화행사_API_키",
    "SEOUL_WOMEN_API_KEY": "발급받은_여성가족_API_키"
  }
}
```

## 🚀 사용 예시

### Claude Desktop에서 사용

1. 설정 완료 후 Claude Desktop 재시작
2. 대화창에서 다음과 같이 요청:

```
이번 주말 서울에서 열리는 클래식 음악 공연을 찾아줘
```

```
강남구의 여성 문화 프로그램을 알려줘
```

### Claude Code에서 사용

```bash
# Claude Code 실행
claude

# 프롬프트에서 MCP 서버 사용
> 서울 문화행사 중 전시회를 검색해줘
```

### Cursor/Cline에서 사용

1. Cursor에서 Cline 확장 열기
2. MCP 서버가 자동으로 연결됨
3. Cline 채팅에서:

```
종로구의 박물관 프로그램을 찾아줘
```

## 🔍 설정 확인

### MCP Inspector로 테스트

```bash
# 프로젝트 디렉토리에서 실행
npx @modelcontextprotocol/inspector uv --directory . run awslabs.seoul_opendata_mcp_server.server:main
```

브라우저에서 `http://localhost:5173` 열어서:
1. 서버 연결 확인
2. 도구 목록 확인
3. 각 도구 테스트

### 환경 변수로 직접 테스트

```bash
# Windows PowerShell
$env:SEOUL_CULTURE_API_KEY="your-api-key"
$env:SEOUL_WOMEN_API_KEY="your-api-key"
uv run awslabs.seoul_opendata_mcp_server.server:main

# macOS/Linux
export SEOUL_CULTURE_API_KEY="your-api-key"
export SEOUL_WOMEN_API_KEY="your-api-key"
uv run awslabs.seoul_opendata_mcp_server.server:main
```

## 📝 사용 가능한 도구

### 문화행사 도구

1. **search_culture_events**
   - 서울 문화행사 검색
   - 파라미터: codename, title, date, start_index, end_index

2. **search_public_reservations**
   - 공공서비스 예약 검색
   - 파라미터: svc_code_name, svc_name, start_index, end_index

### 여성가족 도구

1. **search_women_events**
   - 여성가족재단 이벤트 검색
   - 파라미터: title, event_type, max_results

2. **get_event_details**
   - 이벤트 상세 정보 조회
   - 파라미터: event_reg_no

3. **get_all_women_events**
   - 전체 이벤트 목록 조회
   - 파라미터: max_results

## ⚠️ 주의사항

1. **API 키 보안**: 설정 파일을 GitHub 등에 커밋하지 마세요
2. **절대 경로**: 반드시 절대 경로를 사용해야 합니다 (상대 경로 안 됨)
3. **경로 구분자**: Windows에서도 슬래시(/) 사용 권장
4. **재시작 필요**: 설정 변경 후 클라이언트 재시작 필요
5. **API 제한**: 서울 열린데이터 API는 일일 요청 제한이 있을 수 있습니다

## 🆘 문제 해결

### "서버에 연결할 수 없습니다"

1. uv가 설치되어 있는지 확인
2. 프로젝트 경로가 정확한지 확인
3. API 키가 올바른지 확인

### "도구를 찾을 수 없습니다"

1. 서버가 정상적으로 시작되었는지 확인
2. MCP Inspector로 도구 목록 확인

### "API 요청 실패"

1. API 키가 유효한지 확인
2. 네트워크 연결 확인
3. 서울 열린데이터 광장 서비스 상태 확인

## 📚 추가 리소스

- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [서울 열린데이터 광장](https://data.seoul.go.kr/)
- [FastMCP 문서](https://github.com/jlowin/fastmcp)
