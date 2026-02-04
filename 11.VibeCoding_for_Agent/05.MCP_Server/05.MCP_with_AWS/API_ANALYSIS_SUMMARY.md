# Seoul Culture Events API Analysis Summary

**Date**: 2026-02-02
**Purpose**: Complete API specification for Seoul Culture Events MCP Server implementation

---

## 1. API Overview

### Base Configuration

```yaml
Base URL: http://openapi.seoul.go.kr:8088
Authentication: API key in URL path
Response Format: JSON
Encoding: UTF-8

URL Structure:
  {base_url}/{api_key}/json/{service_name}/{start_index}/{end_index}

Example:
  http://openapi.seoul.go.kr:8088/YOUR_API_KEY/json/culturalEventInfo/1/100
```

### Environment Variables

```yaml
Required:
  - SEOUL_API_KEY: API authentication key

Optional:
  - SEOUL_API_BASE_URL: Default is http://openapi.seoul.go.kr:8088
```

---

## 2. Available APIs (3 Services)

### 2.1 서울시 문화행사 공공서비스예약 정보 (Public Service Reservation)

**Service Name**: (To be determined from Seoul Open Data Portal)
**Total Records**: 345 (as of analysis date)
**Purpose**: Cultural event reservations through Seoul public service system

#### Field Mappings (Korean -> English)

| Korean Field | English Field | Description | Type |
|-------------|---------------|-------------|------|
| SVCID | service_id | Service ID | string |
| SVCNM | service_name | Service name | string |
| SVCSTATNM | service_status | Service status (접수중/접수종료/예약마감) | string |
| MAXCLASSNM | major_category | Major category (대분류) | string |
| MINCLASSNM | minor_category | Minor category (소분류) | string |
| AREANM | district | District name (자치구) | string |
| PLACENM | venue_name | Venue name | string |
| X | longitude | Longitude coordinate | float |
| Y | latitude | Latitude coordinate | float |
| SVCOPNBGNDT | service_start_date | Service start datetime | timestamp (milliseconds) |
| SVCOPNENDDT | service_end_date | Service end datetime | timestamp (milliseconds) |
| RCPTBGNDT | registration_start_date | Registration start datetime | timestamp (milliseconds) |
| RCPTENDDT | registration_end_date | Registration end datetime | timestamp (milliseconds) |
| V_MIN | start_time | Service start time (HH:MM) | string |
| V_MAX | end_time | Service end time (HH:MM) | string |
| USETGTINFO | target_audience | Target audience | string |
| PAYATNM | payment_method | Payment method (무료/유료) | string |
| SVCURL | reservation_url | Direct reservation URL | string |
| TELNO | phone_number | Contact phone number | string |
| DTLCONT | detail_content | Detailed description (HTML) | string |
| IMGURL | image_url | Image URL | string |
| GUBUN | service_type | Service type (자체/대관) | string |
| REVSTDDAY | cancellation_days | Cancellation period (days) | integer |
| REVSTDDAYNM | cancellation_info | Cancellation period info | string |

#### Sample Response Structure

```json
{
  "svcid": "S251218145240208050",
  "svcnm": "[서울역사박물관]2026년 우리 가족 박물관 여행(겨울방학) 수강생 모집",
  "svcstatnm": "접수종료",
  "maxclassnm": "문화체험",
  "minclassnm": "교육체험",
  "areanm": "종로구",
  "placenm": "서울역사박물관",
  "x": "126.97037430869801",
  "y": "37.570500279648634",
  "svcopnbgndt": 1768834800000,
  "svcopnenddt": 1769094000000,
  "rcptbgndt": 1767056400000,
  "rcptenddt": 1767513600000,
  "v_min": "10:00",
  "v_max": "16:00",
  "usetgtinfo": "가족(초등생을 동반한 가족)",
  "payatnm": "무료",
  "svcurl": "https://yeyak.seoul.go.kr/web/reservation/selectReservView.do?rsv_svc_id=S251218145240208050",
  "telno": "02) 724-0258 / 0196",
  "dtlcont": "1. 공공시설 예약서비스 이용시 필수 준수사항...",
  "imgurl": "https://yeyak.seoul.go.kr/web/common/file/FileDown.do?file_id=...",
  "gubun": "자체",
  "revstdday": 1,
  "revstddaynm": "접수종료일"
}
```

#### Major Categories (대분류)

- 문화체험
- 교육체험
- 체육시설
- 기타

#### Minor Categories (소분류)

- 교육체험
- 전시/관람
- 공연/행사
- 체험활동
- 강좌/워크숍

---

### 2.2 서울시 문화행사 정보 (Cultural Events)

**Service Name**: culturalEventInfo (tentative)
**Total Records**: 3,953 (as of analysis date)
**Purpose**: General cultural events and performances in Seoul

#### Field Mappings (Korean -> English)

| Korean Field | English Field | Description | Type |
|-------------|---------------|-------------|------|
| TITLE | title | Event/Performance title | string |
| CODENAME | category | Category (공연/전시/축제/기타) | string |
| THEMECODE | theme_code | Theme classification | string |
| GUNAME | district | District name (자치구) | string |
| PLACE | venue | Venue name | string |
| LAT | latitude | Latitude (X coordinate) | float |
| LOT | longitude | Longitude (Y coordinate) | float |
| DATE | date_range | Date range string (YYYY-MM-DD~YYYY-MM-DD) | string |
| STRTDATE | start_date | Start date | timestamp (milliseconds) |
| END_DATE | end_date | End date | timestamp (milliseconds) |
| PRO_TIME | event_time | Event time | string |
| IS_FREE | is_free | Free or paid (무료/유료) | string |
| USE_FEE | usage_fee | Fee details | string |
| USE_TRGT | target_audience | Target audience | string |
| ORG_NAME | organization | Organizing organization | string |
| ORG_LINK | organization_url | Organization website | string |
| INQUIRY | contact_info | Contact information | string |
| TICKET | ticket_type | Ticket type (시민/기관) | string |
| PLAYER | performers | Performer information | string |
| PROGRAM | program_info | Program introduction | string |
| ETC_DESC | etc_description | Other description | string |
| MAIN_IMG | main_image | Main image URL | string |
| HMPG_ADDR | detail_url | Culture portal detail URL | string |
| RGSTDATE | registration_date | Registration date | string |

#### Sample Response Structure

```json
{
  "title": "해외바이어가 직접 찾는 글로벌 전시회 [2026 인터참코리아]",
  "codename": "전시/미술",
  "themecode": "기타",
  "guname": "강남구",
  "place": "코엑스 A홀, C홀",
  "lat": "37.5118239121138",
  "lot": "127.059159043842",
  "date": "2026-07-01~2026-07-03",
  "strtdate": 1782831600000,
  "end_date": 1783004400000,
  "pro_time": "10:00~17:00",
  "is_free": "유료",
  "use_fee": "현장등록: 20,000원 (사전 등록 시, 무료 입장 가능)",
  "use_trgt": "뷰티산업 종사자",
  "org_name": "기타",
  "org_link": "https://www.intercharmkorea.com/ko-kr.html",
  "inquiry": "070-5095-9904 / 9903",
  "ticket": "시민",
  "player": null,
  "program": null,
  "etc_desc": null,
  "main_img": "https://culture.seoul.go.kr/cmmn/file/getImage.do?atchFileId=...",
  "hmpg_addr": "https://culture.seoul.go.kr/culture/culture/cultureEvent/view.do?cultcode=156571",
  "rgstdate": "2026-01-20"
}
```

#### Event Categories (CODENAME)

- 공연 (Performance)
  - 음악 (Music)
  - 연극 (Theater)
  - 무용 (Dance)
  - 클래식 (Classical)
  - 뮤지컬/오페라 (Musical/Opera)
- 전시/미술 (Exhibition/Art)
- 축제 (Festival)
- 교육/체험 (Education/Experience)
- 기타 (Others)

---

### 2.3 서울시 여성가족재단 행사 정보 (Women & Family Foundation Events)

**Service Name**: (To be determined from Seoul Open Data Portal)
**Total Records**: 313 (as of analysis date)
**Purpose**: Events organized by Seoul Women & Family Foundation

#### Field Mappings (Korean -> English)

| Korean Field | English Field | Description | Type |
|-------------|---------------|-------------|------|
| EVT_REG_NO | event_id | Event number (primary key) | string |
| TITLE | title | Event title | string |
| EVT_TYPE | event_type | Event type/location | string |
| EVT_DATE | event_date | Event date (YYYY-MM-DD~YYYY-MM-DD) | string |
| EVT_PLACE | venue | Event venue | string |
| EVT_TARGET | target_audience | Target audience | string |
| EVT_SPONSOR | organizer | Host/Organizer | string |
| EVT_REG_START_DATE | registration_start_date | Registration start date | string (YYYY-MM-DD) |
| EVT_REG_END_DATE | registration_end_date | Registration end date | string (YYYY-MM-DD) |
| EVT_REG_METHOD | registration_method | Registration method | string |
| EVT_CONTACT | contact_info | Event inquiry contact | string |
| URL | detail_url | Detail information URL | string |

#### Sample Response Structure

```json
{
  "evt_reg_no": "30570",
  "title": "[행사] '서울, 더 아름다운 결혼을 묻다.' 토론회 안내",
  "evt_type": "서울여성플라자",
  "evt_date": "2025-12-19~2025-12-19",
  "evt_place": "서울여성플라자 피움서울 국제회의장(1F)",
  "evt_target": "예비부부, 전문가, 관련업계 종사자 등",
  "evt_sponsor": "서울특별시",
  "evt_reg_start_date": "2025-12-12",
  "evt_reg_end_date": "2025-12-19",
  "evt_reg_method": "사전 등록",
  "evt_contact": "토론회 사무국(☎ 02-6953-4817, E-mail : jw.kim@philicplan.com)",
  "url": "https://www.seoulwomen.or.kr/sfwf/contents/sfwf-event.do?schM=view&id=30570"
}
```

#### Event Types

- 서울여성플라자 (Seoul Women's Plaza)
- 교육/강좌 (Education/Lectures)
- 행사/문화 (Events/Culture)
- 상담/지원 (Counseling/Support)

---

## 3. Seoul Districts (자치구)

All 25 districts of Seoul:

```
강남구, 강동구, 강북구, 강서구, 관악구, 광진구,
구로구, 금천구, 노원구, 도봉구, 동대문구, 동작구,
마포구, 서대문구, 서초구, 성동구, 성북구, 송파구,
양천구, 영등포구, 용산구, 은평구, 종로구, 중구, 중랑구
```

---

## 4. API Response Format

### Standard Response Structure

All Seoul Open Data APIs follow this structure:

```json
{
  "DESCRIPTION": {
    "FIELD_NAME": "Field Description in Korean",
    ...
  },
  "DATA": [
    {
      "field_name": "value",
      ...
    }
  ]
}
```

### Error Response

```json
{
  "RESULT": {
    "CODE": "ERROR-XXX",
    "MESSAGE": "Error description"
  }
}
```

### Common Error Codes

- `ERROR-300`: Invalid API key
- `ERROR-310`: Request limit exceeded
- `ERROR-336`: Service temporarily unavailable
- `ERROR-500`: Database connection error
- `ERROR-600`: Invalid service name

---

## 5. Implementation Guidelines

### 5.1 Date/Time Handling

```python
# Timestamps are in milliseconds
from datetime import datetime

# Convert from API timestamp
def parse_timestamp(ms_timestamp: int) -> datetime:
    return datetime.fromtimestamp(ms_timestamp / 1000)

# Convert to API timestamp
def to_timestamp(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)

# Date format for filtering: YYYYMMDD
def format_date(dt: datetime) -> str:
    return dt.strftime("%Y%m%d")
```

### 5.2 Pagination

```python
# Seoul API uses 1-based indexing
# Max 1000 records per request

def paginate_request(total_count: int, page_size: int = 100):
    """Generate (start_idx, end_idx) tuples for pagination"""
    for start in range(1, total_count + 1, page_size):
        end = min(start + page_size - 1, total_count)
        yield (start, end)

# Example:
# list(paginate_request(345, 100))
# [(1, 100), (101, 200), (201, 300), (301, 345)]
```

### 5.3 Filtering Best Practices

```python
# Client-side filtering is recommended since API has limited query params

def filter_events(events: List[Dict], **filters):
    """
    Filter events by:
    - query: text search in title/description
    - district: exact match on GUNAME/AREANM
    - category: exact match on CODENAME/MAXCLASSNM
    - start_date: events starting after this date
    - end_date: events ending before this date
    - is_free: "무료" or "유료"
    """
    results = events

    if query := filters.get('query'):
        results = [e for e in results
                   if query.lower() in e.get('title', '').lower()
                   or query.lower() in e.get('svcnm', '').lower()]

    if district := filters.get('district'):
        results = [e for e in results
                   if e.get('guname') == district
                   or e.get('areanm') == district]

    # Add more filters as needed

    return results
```

### 5.4 Coordinate System

```yaml
Coordinate System: WGS84 (World Geodetic System 1984)
Format: Decimal degrees
Latitude Range: ~37.4 to 37.7 (Seoul area)
Longitude Range: ~126.7 to 127.2 (Seoul area)

Example:
  City Hall: 37.5665° N, 126.9780° E
  Gangnam: 37.5172° N, 127.0473° E
```

---

## 6. MCP Server Tool Specifications

### Tool 1: search_culture_events

```python
async def search_culture_events(
    query: Optional[str] = None,
    start_date: Optional[str] = None,  # YYYYMMDD
    end_date: Optional[str] = None,    # YYYYMMDD
    district: Optional[str] = None,     # 자치구명
    category: Optional[str] = None,     # 공연/전시/축제 etc
    is_free: Optional[bool] = None,
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    Search cultural events with multiple filters.
    Returns events from both reservation system and general events.
    """
    pass
```

### Tool 2: get_culture_space

```python
async def get_culture_space(
    space_name: Optional[str] = None,
    district: Optional[str] = None,
    category: Optional[str] = None,
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    Search cultural venues and spaces.
    Useful for finding museums, theaters, galleries.
    """
    pass
```

### Tool 3: get_event_details

```python
async def get_event_details(
    event_id: str,
    source: str = "auto"  # "reservation", "events", "women", or "auto"
) -> Dict[str, Any]:
    """
    Get detailed information about a specific event.
    Auto-detects source if not specified.
    """
    pass
```

### Tool 4: get_women_family_events

```python
async def get_women_family_events(
    query: Optional[str] = None,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,  # YYYY-MM-DD
    end_date: Optional[str] = None,    # YYYY-MM-DD
    max_results: int = 50
) -> List[Dict[str, Any]]:
    """
    Search events from Seoul Women & Family Foundation.
    """
    pass
```

---

## 7. Testing Strategy

### Test Cases

```python
# test_api_client.py

@pytest.mark.asyncio
async def test_fetch_reservation_events():
    """Test fetching public service reservation events"""
    client = SeoulAPIClient(config)
    result = await client.get_reservation_events(1, 10)

    assert len(result) <= 10
    assert all('svcid' in event for event in result)
    assert all('svcnm' in event for event in result)

@pytest.mark.asyncio
async def test_fetch_cultural_events():
    """Test fetching cultural events"""
    client = SeoulAPIClient(config)
    result = await client.get_cultural_events(1, 10)

    assert len(result) <= 10
    assert all('title' in event for event in result)
    assert all('codename' in event for event in result)

@pytest.mark.asyncio
async def test_filter_by_district():
    """Test district filtering"""
    events = [
        {'guname': '강남구', 'title': 'Test 1'},
        {'guname': '종로구', 'title': 'Test 2'},
    ]
    filtered = filter_events(events, district='강남구')
    assert len(filtered) == 1
    assert filtered[0]['title'] == 'Test 1'

@pytest.mark.asyncio
async def test_date_range_filtering():
    """Test date range filtering"""
    # Implementation based on timestamp conversion
    pass
```

---

## 8. Known Issues & Limitations

### API Limitations

1. **Rate Limiting**: Check Seoul Open Data API documentation for specific limits
2. **Max Results**: 1000 records per request maximum
3. **No Fuzzy Search**: Exact match required for most fields
4. **No Sorting**: Results are returned in registration order
5. **HTML Content**: Some description fields contain HTML tags
6. **Timestamp Format**: Milliseconds since epoch (not seconds)

### Data Quality Issues

1. **Inconsistent Dates**: Some events use string dates, others use timestamps
2. **Missing Fields**: Many optional fields are `null`
3. **HTML in Text**: `dtlcont` and description fields contain HTML
4. **Coordinate Precision**: Variable precision in lat/lon values
5. **Phone Format**: Inconsistent phone number formatting

### Recommended Workarounds

```python
# 1. HTML cleaning
from html import unescape
import re

def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities"""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    return text.strip()

# 2. Date normalization
def normalize_date(date_value) -> Optional[datetime]:
    """Handle both timestamp and string dates"""
    if isinstance(date_value, int):
        return datetime.fromtimestamp(date_value / 1000)
    elif isinstance(date_value, str):
        # Try multiple formats
        for fmt in ['%Y-%m-%d', '%Y%m%d', '%Y.%m.%d']:
            try:
                return datetime.strptime(date_value, fmt)
            except ValueError:
                continue
    return None

# 3. Phone normalization
def normalize_phone(phone: str) -> str:
    """Normalize phone number format"""
    # Remove all non-digit except +
    digits = re.sub(r'[^\d+]', '', phone)
    # Format: 02-XXXX-XXXX or 010-XXXX-XXXX
    if digits.startswith('02'):
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    elif digits.startswith('0'):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    return phone
```

---

## 9. Security Considerations

### API Key Management

```python
# NEVER commit API keys to version control
# Use environment variables or secret management

# .env file (add to .gitignore)
SEOUL_API_KEY=your_actual_api_key_here

# config.py
import os
from pydantic import Field, BaseModel

class SeoulAPIConfig(BaseModel):
    api_key: str = Field(
        default_factory=lambda: os.getenv("SEOUL_API_KEY", ""),
        description="Seoul Open Data API key"
    )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)
```

### Input Validation

```python
# Validate user inputs to prevent injection attacks

def validate_district(district: str) -> bool:
    """Validate district name against known list"""
    valid_districts = {
        '강남구', '강동구', '강북구', '강서구', '관악구', '광진구',
        '구로구', '금천구', '노원구', '도봉구', '동대문구', '동작구',
        '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구',
        '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
    }
    return district in valid_districts

def validate_date_format(date_str: str) -> bool:
    """Validate YYYYMMDD format"""
    import re
    return bool(re.match(r'^\d{8}$', date_str))
```

---

## 10. Next Steps for Implementation

### Phase 1: Core API Client (Priority)

1. Implement `SeoulAPIClient` class in `utils/api_client.py`
   - HTTP client setup with `httpx.AsyncClient`
   - Error handling and retry logic
   - Response parsing and validation

2. Implement data fetching methods:
   - `get_reservation_events(start_idx, end_idx)`
   - `get_cultural_events(start_idx, end_idx)`
   - `get_women_family_events(start_idx, end_idx)`

3. Write unit tests for API client
   - Mock HTTP responses
   - Test error scenarios
   - Validate response parsing

### Phase 2: MCP Tools Implementation

1. Implement `search_culture_events` tool
   - Aggregate data from multiple sources
   - Apply filters
   - Return normalized results

2. Implement `get_event_details` tool
   - Auto-detect event source
   - Fetch complete details
   - Format response

3. Implement `get_women_family_events` tool
   - Specific filtering for women/family events
   - Date range support

### Phase 3: Testing & Refinement

1. Integration testing with live API
2. Performance optimization
3. Error handling improvements
4. Documentation updates

### Phase 4: Deployment

1. Package for distribution
2. Update Claude Desktop config
3. Test with MCP Inspector
4. User documentation

---

## 11. Reference Links

### Official Documentation

- Seoul Open Data Portal: https://data.seoul.go.kr
- Seoul Public Service Reservation: https://yeyak.seoul.go.kr
- Seoul Culture Portal: https://culture.seoul.go.kr
- Seoul Women & Family Foundation: https://www.seoulwomen.or.kr

### MCP Resources

- FastMCP Documentation: https://github.com/jlowin/fastmcp
- MCP Protocol Specification: https://spec.modelcontextprotocol.io
- AWS MCP Servers Examples: https://github.com/awslabs/mcp-servers

---

## Appendix A: Complete Field Reference

### Reservation Events (공공서비스예약)

```
svcid         - Service ID (unique identifier)
svcnm         - Service name
svcstatnm     - Service status
maxclassnm    - Major category
minclassnm    - Minor category
areanm        - District
placenm       - Venue name
x             - Longitude
y             - Latitude
svcopnbgndt   - Service start timestamp (ms)
svcopnenddt   - Service end timestamp (ms)
rcptbgndt     - Registration start timestamp (ms)
rcptenddt     - Registration end timestamp (ms)
v_min         - Start time (HH:MM)
v_max         - End time (HH:MM)
usetgtinfo    - Target audience
payatnm       - Payment method
svcurl        - Reservation URL
telno         - Phone number
dtlcont       - Detail content (HTML)
imgurl        - Image URL
gubun         - Service type
revstdday     - Cancellation days
revstddaynm   - Cancellation info
```

### Cultural Events (문화행사)

```
title         - Event title
codename      - Category
themecode     - Theme code
guname        - District
place         - Venue
lat           - Latitude
lot           - Longitude
date          - Date range string
strtdate      - Start timestamp (ms)
end_date      - End timestamp (ms)
pro_time      - Event time
is_free       - Free/Paid status
use_fee       - Fee details
use_trgt      - Target audience
org_name      - Organization
org_link      - Organization URL
inquiry       - Contact info
ticket        - Ticket type
player        - Performers
program       - Program info
etc_desc      - Other description
main_img      - Main image URL
hmpg_addr     - Detail URL
rgstdate      - Registration date
```

### Women & Family Events (여성가족재단)

```
evt_reg_no            - Event ID
title                 - Title
evt_type              - Event type
evt_date              - Date range string
evt_place             - Venue
evt_target            - Target audience
evt_sponsor           - Organizer
evt_reg_start_date    - Registration start (YYYY-MM-DD)
evt_reg_end_date      - Registration end (YYYY-MM-DD)
evt_reg_method        - Registration method
evt_contact           - Contact info
url                   - Detail URL
```

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Analyzed Data Sources**:
- 서울시 문화행사 공공서비스예약 정보.json (345 records)
- 서울시 문화행사 정보.json (3,953 records)
- 서울시 여성가족재단 행사 정보.json (313 records)
- CLAUDE.md (Project guidelines)
