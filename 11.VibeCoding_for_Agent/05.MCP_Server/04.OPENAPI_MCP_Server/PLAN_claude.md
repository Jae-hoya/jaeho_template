# 서울시 문화행사 MCP 서버 개발 계획

## 프로젝트 개요
서울시 문화행사 OpenAPI를 MCP(Model Context Protocol) 서버로 구현하여 LLM이 문화행사 정보를 조회할 수 있도록 합니다.

---

## 기술 스택

### 핵심 기술
- **언어**: Python 3.11+
- **프레임워크**: FastMCP (v2.14.4+)
- **패키지 관리자**: uv
- **HTTP 클라이언트**: httpx (async)
- **통신 방식**: stdio (Standard Input/Output)

### 개발 환경
- **가상환경**: `C:\Users\skyop\jaeho_template\dotenv_windows`
- **데이터 소스**: 서울시 문화행사 정보 OpenAPI
- **Base URL**: `http://openapi.seoul.go.kr:8088`

### 주요 의존성
```toml
[dependencies]
fastmcp = ">=2.14.4"
httpx = ">=0.27.0"
pydantic = ">=2.0.0"
python-dotenv = ">=1.0.0"
```

---

## 프로젝트 구조

```
04.OPENAPI_MCP_Server/
├── src/
│   ├── __init__.py
│   ├── server.py              # MCP 서버 메인 엔트리포인트
│   ├── config.py              # 환경 변수 및 설정 관리
│   ├── models.py              # Pydantic 데이터 모델
│   └── services/
│       ├── __init__.py
│       └── seoul_api.py       # 서울시 API 호출 로직
├── tests/
│   ├── __init__.py
│   └── test_server.py
├── .env.example               # 환경 변수 템플릿
├── .env                       # 실제 API 키 (gitignore)
├── pyproject.toml             # uv 프로젝트 설정
├── README.md
├── PLAN_claude.md             # 이 파일
└── seoul-culture-events-api.md
```

---

## MCP Tool 설계

### 1. get_cultural_events
**목적**: 문화행사 목록 조회 (기본)

**Parameters**:
- `start_index` (int, default=1): 시작 위치
- `end_index` (int, default=10): 종료 위치
- `codename` (str, optional): 분류 필터 (예: "무용", "연극")
- `title` (str, optional): 공연/행사명 필터
- `date` (str, optional): 날짜 필터 (YYYY-MM-DD)

**Returns**: 문화행사 목록 JSON (DESCRIPTION + DATA)

---

### 2. search_events_by_title
**목적**: 제목으로 행사 검색

**Parameters**:
- `title` (str, required): 검색할 행사명
- `limit` (int, default=10): 최대 결과 수

**Returns**: 매칭되는 행사 목록

---

### 3. search_events_by_date_range
**목적**: 특정 기간 내 행사 검색

**Parameters**:
- `start_date` (str, required): 시작일 (YYYY-MM-DD)
- `end_date` (str, optional): 종료일 (YYYY-MM-DD, 미지정시 start_date와 동일)
- `limit` (int, default=20): 최대 결과 수

**Returns**: 해당 기간의 행사 목록

---

### 4. search_events_by_category
**목적**: 카테고리별 행사 필터링

**Parameters**:
- `category` (str, required): 분류명 (예: "무용", "음악", "연극")
- `is_free` (bool, optional): 무료 행사만 필터링
- `limit` (int, default=15): 최대 결과 수

**Returns**: 카테고리에 맞는 행사 목록

---

### 5. get_free_events
**목적**: 무료 행사만 조회

**Parameters**:
- `limit` (int, default=20): 최대 결과 수
- `guname` (str, optional): 자치구 필터 (예: "종로구")

**Returns**: 무료 행사 목록

---

### 6. get_event_by_location
**목적**: 위치 기반 행사 검색 (자치구)

**Parameters**:
- `guname` (str, required): 자치구명 (예: "강남구", "종로구")
- `limit` (int, default=15): 최대 결과 수

**Returns**: 해당 지역의 행사 목록

---

## 구현 단계

### Phase 1: 환경 설정 및 기본 구조 (1단계)
- [x] 프로젝트 디렉토리 생성
- [ ] uv로 pyproject.toml 초기화
- [ ] 가상환경 연결 (`C:\Users\skyop\jaeho_template\dotenv_windows`)
- [ ] 의존성 패키지 설치 (fastmcp, httpx, pydantic, python-dotenv)
- [ ] .env 파일 생성 (API_KEY 설정)

**주요 파일**:
- `pyproject.toml`
- `.env`

---

### Phase 2: 데이터 모델 정의 (2단계)
- [ ] Pydantic 모델 작성 (`models.py`)
  - `CulturalEvent`: 개별 행사 데이터
  - `EventResponse`: API 응답 구조 (DESCRIPTION + DATA)
  - `EventFilter`: 검색 필터 옵션

**주요 필드**:
```python
class CulturalEvent(BaseModel):
    title: str
    codename: str
    guname: str
    date: str
    place: str
    org_name: str
    use_fee: str | None
    is_free: str
    main_img: str
    lat: str
    lot: str
    strtdate: int
    end_date: int
    # ... 기타 필드
```

---

### Phase 3: API 서비스 레이어 (3단계)
- [ ] `config.py` 작성
  - 환경 변수 로드 (API_KEY, BASE_URL)
  - 설정 클래스 정의

- [ ] `services/seoul_api.py` 작성
  - `httpx.AsyncClient` 기반 API 클라이언트
  - `fetch_events()`: 기본 조회 함수
  - 에러 핸들링 (HTTP 에러, 타임아웃)
  - 응답 파싱 및 검증

**핵심 함수**:
```python
async def fetch_events(
    start_index: int,
    end_index: int,
    filters: dict | None = None
) -> EventResponse:
    """서울시 문화행사 API 호출"""
    # API 요청 로직
```

---

### Phase 4: MCP 서버 구현 (4단계)
- [ ] `server.py` 작성
  - FastMCP 인스턴스 생성
  - 6개 Tool 함수 구현 (@mcp.tool 데코레이터)
  - 각 Tool에서 `seoul_api` 호출
  - 에러 처리 및 로깅

**서버 구조**:
```python
from fastmcp import FastMCP
from services.seoul_api import fetch_events

mcp = FastMCP(name="Seoul Cultural Events MCP Server")

@mcp.tool
async def get_cultural_events(
    start_index: int = 1,
    end_index: int = 10,
    codename: str | None = None,
    title: str | None = None,
    date: str | None = None
) -> dict:
    """서울시 문화행사 목록을 조회합니다."""
    # 구현 로직

# ... 나머지 5개 Tool 구현

if __name__ == "__main__":
    mcp.run()  # stdio 방식으로 실행
```

---

### Phase 5: 테스트 및 검증 (5단계)
- [ ] 단위 테스트 작성 (`tests/test_server.py`)
- [ ] 실제 API 호출 테스트
- [ ] MCP 클라이언트 연동 테스트
- [ ] 에러 케이스 검증

---

### Phase 6: 문서화 및 배포 준비 (6단계)
- [ ] README.md 작성
  - 설치 방법
  - API 키 발급 안내
  - 사용 예시
  - MCP 클라이언트 설정 방법
- [ ] Claude Desktop 설정 가이드
- [ ] 배포 가이드 (stdio 방식)

---

## 기술적 고려사항

### 1. 비동기 처리
- httpx의 `AsyncClient` 사용
- FastMCP의 async tool 지원 활용
- 여러 API 호출 시 병렬 처리 고려

### 2. 에러 핸들링
- API 키 미설정 체크
- HTTP 에러 (401, 403, 404, 500) 처리
- 타임아웃 설정 (default: 30초)
- 잘못된 파라미터 검증

### 3. 데이터 정규화
- `date` 범위 파싱 (YYYY-MM-DD~YYYY-MM-DD)
- `strtdate`, `end_date` epoch ms를 datetime 변환
- `lat`, `lot` 문자열을 float 변환 옵션
- `is_free` 문자열 ("무료"/"유료") 처리

### 4. 성능 최적화
- API 응답 캐싱 (선택적)
- Connection pooling (httpx 기본 제공)
- 페이징 제한 (MAX_ITEMS_PER_REQUEST = 100)

---

## 환경 변수 설정

### .env 파일
```env
# 서울시 OpenAPI 인증키
SEOUL_API_KEY=your_api_key_here

# API Base URL
SEOUL_API_BASE_URL=http://openapi.seoul.go.kr:8088

# 서비스명
SEOUL_SERVICE_NAME=culturalEventInfo

# 응답 타입
SEOUL_RESPONSE_TYPE=json
```

---

## MCP 클라이언트 설정 (Claude Desktop 예시)

### claude_desktop_config.json
```json
{
  "mcpServers": {
    "seoul-cultural-events": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\skyop\\jaeho_template\\11.VibeCoding_for_Agent\\05.MCP_Server\\04.OPENAPI_MCP_Server",
        "run",
        "python",
        "src/server.py"
      ],
      "env": {
        "SEOUL_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

---

## 예상 결과물

### 1. 코드 베이스
- 구조화된 Python MCP 서버
- 6개의 문화행사 조회/검색 Tool
- 재사용 가능한 API 서비스 레이어

### 2. 문서
- 상세한 README.md
- API 사용 가이드
- MCP 클라이언트 통합 가이드

### 3. 테스트
- 단위 테스트 커버리지
- 통합 테스트 시나리오

---

## 참고 자료

1. **FastMCP 공식 문서**: https://gofastmcp.com/
2. **서울시 OpenAPI**: http://openapi.seoul.go.kr:8088
3. **MCP 프로토콜**: Model Context Protocol Specification
4. **httpx 문서**: https://www.python-httpx.org/

---

## 변경 이력

- 2026-01-30: 초안 작성
