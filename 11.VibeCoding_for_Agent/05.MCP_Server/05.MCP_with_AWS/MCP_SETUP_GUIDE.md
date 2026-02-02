# Seoul Open Data MCP Server - 설치 및 설정 가이드

## 📋 목차

1. [빠른 시작](#빠른-시작)
2. [API 키 발급](#api-키-발급)
3. [클라이언트별 설정](#클라이언트별-설정)
4. [사용 예시](#사용-예시)
5. [문제 해결](#문제-해결)

---

## 🚀 빠른 시작

### 1단계: 프로젝트 설치

```bash
# 프로젝트 디렉토리로 이동
cd C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS

# 의존성 설치
uv sync --all-groups
```

### 2단계: API 키 발급

[서울 열린데이터 광장](https://data.seoul.go.kr/)에서 두 개의 API 키를 발급받으세요:
- 문화행사정보 API 키
- 서울여성플라자 이벤트 API 키

### 3단계: 클라이언트 설정

원하는 클라이언트의 설정 파일을 복사하고 API 키를 입력하세요.

---

## 🔑 API 키 발급

### 발급 절차

1. **회원가입**
   - https://data.seoul.go.kr/ 접속
   - 회원가입 (무료)

2. **인증키 신청**
   - 로그인 후 **마이페이지** 이동
   - **오픈API** → **인증키 신청**

3. **서비스 선택**
   다음 두 서비스에 대한 키 신청:

   **① 문화행사정보**
   - 서비스명: `culturalEventInfo`
   - 용도: 서울시 문화행사 검색

   **② 서울여성플라자 이벤트**
   - 서비스명: `SeoulWomenPlazaEvent`
   - 용도: 여성가족재단 이벤트 정보

4. **키 발급 완료**
   - 즉시 발급됨 (승인 대기 없음)
   - 마이페이지에서 키 확인 가능

---

## ⚙️ 클라이언트별 설정

### 1️⃣ Claude Desktop

**설정 파일 위치:**

| OS | 경로 |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

**설정 방법:**

```bash
# Windows PowerShell
cd $env:APPDATA\Claude
notepad claude_desktop_config.json

# macOS/Linux
cd ~/Library/Application\ Support/Claude
nano claude_desktop_config.json
```

**설정 내용:**

```json
{
  "mcpServers": {
    "seoul-opendata": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS",
        "run",
        "awslabs.seoul_opendata_mcp_server.server:main"
      ],
      "env": {
        "SEOUL_CULTURE_API_KEY": "여기에_문화행사_API_키",
        "SEOUL_WOMEN_API_KEY": "여기에_여성가족_API_키"
      }
    }
  }
}
```

**주의사항:**
- 경로는 절대 경로로 입력
- Windows에서도 슬래시(`/`) 사용
- 설정 후 Claude Desktop 재시작 필수

---

### 2️⃣ Claude Code (CLI)

**설정 파일 위치:**
```
~/.claude/config.json
```

**설정 방법:**

```bash
# 디렉토리 생성
mkdir -p ~/.claude

# 설정 파일 생성
cat > ~/.claude/config.json << 'EOF'
{
  "mcpServers": {
    "seoul-opendata": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS",
        "run",
        "awslabs.seoul_opendata_mcp_server.server:main"
      ],
      "env": {
        "SEOUL_CULTURE_API_KEY": "여기에_문화행사_API_키",
        "SEOUL_WOMEN_API_KEY": "여기에_여성가족_API_키"
      }
    }
  }
}
EOF

# 편집기로 API 키 입력
vi ~/.claude/config.json
```

**사용 방법:**

```bash
# Claude Code 시작
claude

# MCP 서버가 자동으로 로드됨
# 프롬프트에서 바로 사용 가능
```

---

### 3️⃣ Cursor/Cline

**설정 파일 위치:**
```
프로젝트_루트/cline_mcp_settings.json
```

**설정 방법:**

```bash
# 프로젝트 루트에서
cd your-project

# 설정 파일 생성
cat > cline_mcp_settings.json << 'EOF'
{
  "mcpServers": {
    "seoul-opendata": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS",
        "run",
        "awslabs.seoul_opendata_mcp_server.server:main"
      ],
      "env": {
        "SEOUL_CULTURE_API_KEY": "여기에_문화행사_API_키",
        "SEOUL_WOMEN_API_KEY": "여기에_여성가족_API_키"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
EOF
```

**Cursor에서 설정:**

1. Cursor 열기
2. `Cmd/Ctrl + Shift + P` → "Cline: Open MCP Settings"
3. 또는 프로젝트 루트의 `cline_mcp_settings.json` 직접 편집

---

## 💡 사용 예시

### Claude Desktop에서

```
[사용자]
이번 주말 서울에서 열리는 클래식 음악 공연을 찾아줘

[Claude]
search_culture_events를 사용하여 검색합니다...
```

```
[사용자]
강남구의 여성 문화 프로그램 정보 알려줘

[Claude]
search_women_events를 사용하여 검색합니다...
```

### 사용 가능한 질문 예시

**문화행사 관련:**
- "이번 달 서울에서 열리는 전시회는?"
- "종로구의 공연 일정 알려줘"
- "무료 문화 프로그램 찾아줘"
- "어린이를 위한 체험 프로그램은?"

**여성가족 관련:**
- "서울여성플라자의 강좌 정보 알려줘"
- "여성을 위한 교육 프로그램은?"
- "가족과 함께할 수 있는 이벤트 찾아줘"

---

## 🧪 설정 테스트

### MCP Inspector로 테스트

```bash
# 프로젝트 디렉토리에서
cd C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS

# MCP Inspector 실행
npx @modelcontextprotocol/inspector uv --directory . run awslabs.seoul_opendata_mcp_server.server:main
```

브라우저에서 `http://localhost:5173` 접속 후:

1. **서버 연결 확인**
   - "Connected" 상태 확인

2. **도구 목록 확인**
   - `search_culture_events`
   - `search_public_reservations`
   - `search_women_events`
   - `get_event_details`
   - `get_all_women_events`

3. **도구 실행 테스트**
   - 각 도구 선택
   - 파라미터 입력
   - "Execute" 클릭
   - 결과 확인

### 직접 실행 테스트

```bash
# 환경 변수 설정 (Windows PowerShell)
$env:SEOUL_CULTURE_API_KEY="your-api-key"
$env:SEOUL_WOMEN_API_KEY="your-api-key"

# 서버 실행
uv run awslabs.seoul_opendata_mcp_server.server:main

# macOS/Linux
export SEOUL_CULTURE_API_KEY="your-api-key"
export SEOUL_WOMEN_API_KEY="your-api-key"
uv run awslabs.seoul_opendata_mcp_server.server:main
```

---

## 🔧 문제 해결

### "uv: command not found"

**해결:**
```bash
# uv 설치
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "서버에 연결할 수 없습니다"

**체크리스트:**
1. ✅ 프로젝트 경로가 정확한가?
2. ✅ API 키가 올바르게 입력되었는가?
3. ✅ uv가 설치되어 있는가?
4. ✅ 의존성이 설치되었는가? (`uv sync`)

**디버깅:**
```bash
# 서버를 직접 실행하여 에러 확인
cd C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS
uv run awslabs.seoul_opendata_mcp_server.server:main
```

### "API 키가 유효하지 않습니다"

**확인 사항:**
1. 서울 열린데이터 광장에서 키 상태 확인
2. 올바른 서비스의 키를 사용하고 있는지 확인
3. 키에 공백이나 특수문자가 없는지 확인

**테스트:**
```bash
# API 키 직접 테스트
curl "http://openapi.seoul.go.kr:8088/YOUR_API_KEY/json/culturalEventInfo/1/5"
```

### "도구를 찾을 수 없습니다"

**해결:**
```bash
# 프로젝트 재설치
cd C:/Users/skyop/jaeho_template/11.VibeCoding_for_Agent/05.MCP_Server/05.MCP_with_AWS
uv sync --all-groups

# 클라이언트 재시작
```

### Windows 경로 문제

**잘못된 예:**
```json
"C:\Users\skyop\..."  ❌ (백슬래시)
```

**올바른 예:**
```json
"C:/Users/skyop/..."  ✅ (슬래시)
```

---

## 📚 추가 정보

### 환경 변수 영구 설정 (선택)

**Windows:**
```powershell
# 시스템 환경 변수 설정
[System.Environment]::SetEnvironmentVariable('SEOUL_CULTURE_API_KEY', 'your-key', 'User')
[System.Environment]::SetEnvironmentVariable('SEOUL_WOMEN_API_KEY', 'your-key', 'User')
```

**macOS/Linux:**
```bash
# ~/.bashrc 또는 ~/.zshrc에 추가
echo 'export SEOUL_CULTURE_API_KEY="your-key"' >> ~/.bashrc
echo 'export SEOUL_WOMEN_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

### 보안 권장사항

1. **API 키 관리**
   - 설정 파일을 버전 관리에 포함하지 마세요
   - 공개 저장소에 키를 업로드하지 마세요

2. **.gitignore 추가**
   ```gitignore
   # MCP 설정 파일
   claude_desktop_config.json
   cline_mcp_settings.json
   .claude/config.json

   # 환경 변수 파일
   .env
   .env.local
   ```

3. **키 교체**
   - 정기적으로 API 키 교체
   - 노출 의심 시 즉시 재발급

---

## 🎯 다음 단계

1. ✅ API 키 발급 완료
2. ✅ 클라이언트 설정 완료
3. ✅ 서버 연결 테스트
4. 📖 [README.md](README.md)에서 사용 가능한 도구 확인
5. 🚀 Claude와 함께 서울 문화 정보 탐색!

---

**문서 버전:** 1.0.0
**최종 수정:** 2025-02-02
**문의:** [GitHub Issues](https://github.com/awslabs/mcp/issues)
