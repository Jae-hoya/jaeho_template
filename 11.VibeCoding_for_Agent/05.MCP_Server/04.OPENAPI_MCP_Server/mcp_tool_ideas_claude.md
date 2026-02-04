# Seoul Cultural Events MCP Server - Tool 추가 계획

## 📊 현재 구현된 Tool 분석

**기본 검색**:
- get_cultural_events
- list_cultural_events
- search_cultural_events

**특화 검색**:
- search_events_by_title
- search_events_by_date_range
- search_events_by_category
- get_free_events
- get_event_by_location

**메타데이터**:
- get_event_field_map

---

## 💡 추가하면 좋은 Tool 아이디어

### 1️⃣ 시간 기반 편의 검색 도구 (높은 사용 빈도 예상)

#### get_upcoming_events
```python
@mcp.tool
async def get_upcoming_events(
    days: int = 7,
    guname: str | None = None,
    limit: int = 20
) -> Dict[str, Any]:
    """오늘부터 N일 이내 시작하는 행사 검색"""
```

#### get_this_weekend_events
```python
@mcp.tool
async def get_this_weekend_events(
    is_free: bool | None = None,
    limit: int = 20
) -> Dict[str, Any]:
    """이번 주말(토-일) 행사 검색"""
```

#### get_events_ending_soon
```python
@mcp.tool
async def get_events_ending_soon(
    days: int = 3,
    limit: int = 15
) -> Dict[str, Any]:
    """N일 이내 종료되는 행사 (놓치기 전에 가야 할 행사)"""
```

---

### 2️⃣ 추가 필드 기반 검색 도구

#### search_events_by_organization
```python
@mcp.tool
async def search_events_by_organization(
    org_name: str,
    limit: int = 15
) -> Dict[str, Any]:
    """기관명으로 검색 (예: 세종문화회관, 국립극장)"""
```

#### search_events_by_theme
```python
@mcp.tool
async def search_events_by_theme(
    themecode: str,
    limit: int = 20
) -> Dict[str, Any]:
    """테마코드로 검색 (themecode 필드 활용)"""
```

#### search_events_by_performer
```python
@mcp.tool
async def search_events_by_performer(
    performer: str,
    limit: int = 10
) -> Dict[str, Any]:
    """출연자 이름으로 검색 (player 필드)"""
```

#### search_events_for_target_audience
```python
@mcp.tool
async def search_events_for_target_audience(
    age_group: str,  # 예: "7세", "청소년", "성인"
    limit: int = 15
) -> Dict[str, Any]:
    """이용대상(use_trgt)으로 필터링"""
```

---

### 3️⃣ 위치 기반 고급 검색

#### search_nearby_events
```python
@mcp.tool
async def search_nearby_events(
    lat: float,
    lon: float,
    radius_km: float = 5.0,
    limit: int = 20
) -> Dict[str, Any]:
    """좌표 기반 반경 N km 내 행사 검색 (Haversine 거리 계산)"""
```

#### get_events_with_map_info
```python
@mcp.tool
async def get_events_with_map_info(
    guname: str | None = None,
    limit: int = 20
) -> Dict[str, Any]:
    """좌표 정보(lat/lot)가 있는 행사만 반환 (지도 표시용)"""
```

---

### 4️⃣ 통계 및 분석 도구

#### get_events_statistics
```python
@mcp.tool
async def get_events_statistics(
    start_date: str,
    end_date: str,
    group_by: str = "category"  # category, district, theme
) -> Dict[str, Any]:
    """기간 내 행사 통계 (카테고리별/지역별/테마별 집계)"""
```

#### get_popular_venues
```python
@mcp.tool
async def get_popular_venues(
    limit: int = 10
) -> Dict[str, Any]:
    """행사가 가장 많이 열리는 장소 순위"""
```

#### get_available_filters
```python
@mcp.tool
async def get_available_filters() -> Dict[str, Any]:
    """사용 가능한 필터 값 목록 (categories, districts, themes 추출)"""
```

---

### 5️⃣ 조합 검색 도구 (사용자 편의성)

#### search_family_friendly_events
```python
@mcp.tool
async def search_family_friendly_events(
    guname: str | None = None,
    limit: int = 15
) -> Dict[str, Any]:
    """가족 친화적 행사 (무료 + 연령제한 완화)"""
```

#### search_budget_events
```python
@mcp.tool
async def search_budget_events(
    max_price: int = 10000,
    limit: int = 20
) -> Dict[str, Any]:
    """저가 행사 검색 (use_fee 파싱하여 가격 필터)"""
```

#### get_recently_added_events
```python
@mcp.tool
async def get_recently_added_events(
    days: int = 7,
    limit: int = 20
) -> Dict[str, Any]:
    """최근 N일 이내 등록된 행사 (rgstdate 기준)"""
```

---

### 6️⃣ 상세 조회 도구

#### get_event_full_details
```python
@mcp.tool
async def get_event_full_details(
    title_keyword: str
) -> Dict[str, Any]:
    """제목 키워드로 검색 후 상위 1건의 모든 필드 반환 (이미지, 링크 포함)"""
```

#### get_events_by_registration_period
```python
@mcp.tool
async def get_events_by_registration_period(
    start_date: str,
    end_date: str,
    limit: int = 20
) -> Dict[str, Any]:
    """신청일(rgstdate) 기준 검색"""
```

---

## 🎯 우선순위 추천 (실용성 순)

### High Priority (바로 추가하면 좋음)
1. **get_upcoming_events** - 가장 자주 쓰일 검색 패턴
2. **get_this_weekend_events** - 주말 계획용
3. **search_nearby_events** - 위치 기반 추천의 핵심
4. **get_available_filters** - 사용자가 어떤 값을 쓸 수 있는지 알려줌
5. **search_events_by_organization** - 특정 기관 팬층 존재

### Medium Priority
6. **get_events_ending_soon** - FOMO 마케팅 효과
7. **search_family_friendly_events** - 타겟 명확
8. **get_recently_added_events** - 신규 행사 발견
9. **get_events_statistics** - 데이터 분석 니즈

### Low Priority (필요시)
10. search_events_by_theme, search_events_by_performer 등

---

## 🔧 구현 시 고려사항

### 1. 좌표 계산 (search_nearby_events)
- Haversine 공식을 사용한 거리 계산 필요
- `lat`, `lot` 필드는 문자열이므로 float 변환 필수

### 2. 가격 파싱 (search_budget_events)
- `use_fee` 필드는 자유 텍스트 형식 (예: "R석 60,000원 S석 40,000원")
- 정규식을 사용한 가격 추출 로직 필요
- 여러 가격이 있을 경우 최소값 또는 최대값 기준 결정

### 3. 날짜 계산
- `strtdate`/`end_date`는 Unix epoch milliseconds 형식
- datetime 변환 필요: `datetime.fromtimestamp(strtdate / 1000)`
- `rgstdate`는 "YYYY-MM-DD" 문자열 형식

### 4. 주말 계산 (get_this_weekend_events)
- 현재 날짜를 기준으로 다가오는 토요일, 일요일 계산
- `datetime.weekday()` 활용 (월요일=0, 일요일=6)

### 5. 통계 집계 (get_events_statistics)
- client-side에서 전체 데이터 스캔 필요
- 메모리 효율성 고려하여 limit 설정
- Counter 또는 defaultdict 사용

### 6. 필터 추출 (get_available_filters)
- 대량 데이터 샘플링 후 unique 값 추출
- codename, guname, themecode 등의 distinct 값 반환
- 캐싱 고려 (자주 변하지 않는 데이터)

---

## 📝 데이터 필드 참고

API 응답에 포함된 주요 필드:
- **기본 정보**: title, codename, date, place, org_name
- **이용 정보**: use_trgt (이용대상), use_fee (이용요금), is_free (유무료)
- **메타 정보**: inquiry (문의), player (출연자정보), program (프로그램소개), etc_desc (기타내용)
- **위치 정보**: guname (자치구), lat/lot (좌표)
- **링크**: org_link (홈페이지), hmpg_addr (문화포털상세URL), main_img (대표이미지)
- **날짜**: strtdate (시작일), end_date (종료일), rgstdate (신청일), pro_time (행사시간)
- **분류**: themecode (테마분류), ticket (시민/기관)

---

## 🚀 다음 단계

1. High Priority tool부터 순차 구현
2. validation.py에 필요한 helper 함수 추가
3. 테스트 코드 작성
4. CLAUDE.md 업데이트
