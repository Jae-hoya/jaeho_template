# 서울시 문화행사 API 스펙

## 개요
- 목적: 서울시 문화행사 목록을 조회한다.
- 데이터 소스: `서울시 문화행사 정보.json`
- 공식 요청 규격: `서울시+문화행사+정보.xls`
- 응답 포맷: `application/json` (UTF-8)

## Base URL
- `http://openapi.seoul.go.kr:8088`

## Endpoint
`GET /{KEY}/{TYPE}/{SERVICE}/{START_INDEX}/{END_INDEX}/`

## 요청 파라미터
### 요청 인자 (순서)
XLS 기준 요청 인자 순서다. `KEY`부터 `END_INDEX`까지는 경로 세그먼트이며 나머지는 선택 필터로 사용된다.

| 순서 | 이름 | 타입 | 필수 | 설명 | 값/예시 |
| --- | --- | --- | --- | --- | --- |
| 1 | `KEY` | string | Y | 인증키 | 발급된 API 키 |
| 2 | `TYPE` | string | Y | 요청파일 타입 | `xml`, `xmlf`, `xls`, `json` |
| 3 | `SERVICE` | string | Y | 서비스명 | `culturalEventInfo` |
| 4 | `START_INDEX` | integer | Y | 요청 시작 위치 | `1` |
| 5 | `END_INDEX` | integer | Y | 요청 종료 위치 | `5` |
| 6 | `CODENAME` | string | N | 분류 |  |
| 7 | `TITLE` | string | N | 공연/행사명 |  |
| 8 | `DATE` | string | N | 날짜 | `YYYY-MM-DD` |

### Path parameters
| 이름 | 타입 | 필수 | 설명 | 값/예시 |
| --- | --- | --- | --- | --- |
| `KEY` | string | Y | 인증키 | 발급된 API 키 |
| `TYPE` | string | Y | 요청파일 타입 | `xml`, `xmlf`, `xls`, `json` |
| `SERVICE` | string | Y | 서비스명 | `culturalEventInfo` |
| `START_INDEX` | integer | Y | 요청 시작 위치 | `1` |
| `END_INDEX` | integer | Y | 요청 종료 위치 | `5` |

### Query parameters (optional)
| 이름 | 타입 | 필수 | 설명 | 값/예시 |
| --- | --- | --- | --- | --- |
| `CODENAME` | string | N | 분류 |  |
| `TITLE` | string | N | 공연/행사명 |  |
| `DATE` | string | N | 날짜 | `YYYY-MM-DD` |

### Sample URL
`http://openapi.seoul.go.kr:8088/sample/xml/culturalEventInfo/1/5/`

## 응답 스키마 (JSON 기준)
### 출력 필드(순서/출력명/출력설명)
XLS 기준 출력 순서이며 출력명은 대문자 표기다.

| 순서 | 출력명 | 출력설명 |
| --- | --- | --- |
| 1 | `CODENAME` | 분류 |
| 2 | `GUNAME` | 자치구 |
| 3 | `TITLE` | 공연/행사명 |
| 4 | `DATE` | 날짜 |
| 5 | `PLACE` | 장소 |
| 6 | `ORG_NAME` | 기관명 |
| 7 | `USE_TRGT` | 이용대상 |
| 8 | `USE_FEE` | 이용요금 |
| 9 | `INQUIRY` | 문의 |
| 10 | `PLAYER` | 출연자정보 |
| 11 | `PROGRAM` | 프로그램소개 |
| 12 | `ETC_DESC` | 기타내용 |
| 13 | `ORG_LINK` | 홈페이지 주소 |
| 14 | `MAIN_IMG` | 대표이미지 |
| 15 | `RGSTDATE` | 신청일 |
| 16 | `TICKET` | 시민/기관 |
| 17 | `STRTDATE` | 시작일 |
| 18 | `END_DATE` | 종료일 |
| 19 | `THEMECODE` | 테마분류 |
| 20 | `LOT` | 경도(Y좌표) |
| 21 | `LAT` | 위도(X좌표) |
| 22 | `IS_FREE` | 유무료 |
| 23 | `HMPG_ADDR` | 문화포털상세URL |
| 24 | `PRO_TIME` | 행사시간 |
### 최상위 응답
| 필드 | 타입 | 설명 |
| --- | --- | --- |
| `DESCRIPTION` | object | 필드 설명(한글 라벨) 매핑 |
| `DATA` | array | 문화행사 목록 |

### DESCRIPTION
`DESCRIPTION`는 필드명을 한글 라벨로 매핑한다. 원본 출력명은 대문자이며, `DATA`의 필드명은 소문자다.

| 키(대문자) | 한글 라벨 |
| --- | --- |
| `CODENAME` | 분류 |
| `PRO_TIME` | 행사시간 |
| `ETC_DESC` | 기타내용 |
| `ORG_NAME` | 기관명 |
| `THEMECODE` | 테마분류 |
| `END_DATE` | 종료일 |
| `STRTDATE` | 시작일 |
| `ORG_LINK` | 홈페이지 주소 |
| `MAIN_IMG` | 대표이미지 |
| `LAT` | 위도(X좌표) |
| `PLACE` | 장소 |
| `PLAYER` | 출연자정보 |
| `USE_FEE` | 이용요금 |
| `PROGRAM` | 프로그램소개 |
| `TICKET` | 시민/기관 |
| `RGSTDATE` | 신청일 |
| `DATE` | 날짜 |
| `GUNAME` | 자치구 |
| `INQUIRY` | 문의 |
| `HMPG_ADDR` | 문화포털상세URL |
| `IS_FREE` | 유무료 |
| `USE_TRGT` | 이용대상 |
| `LOT` | 경도(Y좌표) |
| `TITLE` | 공연/행사명 |

### DATA (Event)
| 필드 | 타입 | 널 허용 | 설명 | 예시 |
| --- | --- | --- | --- | --- |
| `org_name` | string | N | 기관명 | `세종문화회관` |
| `use_fee` | string | Y | 이용요금 | `R석 60,000원` |
| `org_link` | string | N | 홈페이지 주소 | `https://www.sejongpac.or.kr/...` |
| `player` | string | Y | 출연자정보 | `마이클 케나(영국)...` |
| `guname` | string | N | 자치구 | `종로구` |
| `pro_time` | string | N | 행사시간 | `19:30` |
| `main_img` | string | N | 대표이미지 URL | `https://culture.seoul.go.kr/...` |
| `themecode` | string | N | 테마분류 | `기타` |
| `date` | string | N | 날짜 범위 | `2026-05-15~2026-05-17` |
| `etc_desc` | string | Y | 기타내용 | `null` |
| `end_date` | integer | N | 종료일(Unix epoch ms) | `1778943600000` |
| `title` | string | N | 공연/행사명 | `[세종문화회관] In the Bamboo Forest` |
| `inquiry` | string | N | 문의 | `02-399-1000` |
| `ticket` | string | N | 시민/기관 구분 | `기관` |
| `codename` | string | N | 분류 | `무용` |
| `use_trgt` | string | N | 이용대상 | `7세 이상 관람 가능` |
| `program` | string | Y | 프로그램소개 | `예술이 지켜낸 풍경...` |
| `lot` | string | N | 경도(Y좌표) | `126.9760053` |
| `rgstdate` | string | N | 신청일(YYYY-MM-DD) | `2026-01-23` |
| `strtdate` | integer | N | 시작일(Unix epoch ms) | `1778770800000` |
| `place` | string | N | 장소 | `세종M씨어터` |
| `hmpg_addr` | string | N | 문화포털상세URL | `https://culture.seoul.go.kr/...` |
| `lat` | string | N | 위도(X좌표) | `37.5726241` |
| `is_free` | string | N | 유무료 | `유료` |

## 응답 예시
```json
{
  "DESCRIPTION": {
    "CODENAME": "분류",
    "PRO_TIME": "행사시간",
    "ETC_DESC": "기타내용",
    "ORG_NAME": "기관명",
    "THEMECODE": "테마분류",
    "END_DATE": "종료일",
    "STRTDATE": "시작일",
    "ORG_LINK": "홈페이지 주소",
    "MAIN_IMG": "대표이미지",
    "LAT": "위도(X좌표)",
    "PLACE": "장소",
    "PLAYER": "출연자정보",
    "USE_FEE": "이용요금",
    "PROGRAM": "프로그램소개",
    "TICKET": "시민/기관",
    "RGSTDATE": "신청일",
    "DATE": "날짜",
    "GUNAME": "자치구",
    "INQUIRY": "문의",
    "HMPG_ADDR": "문화포털상세URL",
    "IS_FREE": "유무료",
    "USE_TRGT": "이용대상",
    "LOT": "경도(Y좌표)",
    "TITLE": "공연/행사명"
  },
  "DATA": [
    {
      "org_name": "세종문화회관",
      "use_fee": "R석 60,000원 S석 40,000원",
      "org_link": "https://www.sejongpac.or.kr/portal/performance/performance/performTicket.do?performIdx=36777&menuNo=200320#none",
      "player": null,
      "guname": "종로구",
      "pro_time": "5.15(금) 1회차 19:30 / 5.16(토) 1회차 14:00 2회차 18:00 / 5.17(일) 1회차 14:00",
      "main_img": "https://culture.seoul.go.kr/cmmn/file/getImage.do?atchFileId=1f6d8ad0d1ac4643a7df58c9037ccf21&thumb=Y",
      "themecode": "기타",
      "date": "2026-05-15~2026-05-17",
      "etc_desc": null,
      "end_date": 1778943600000,
      "title": "[세종문화회관] In the Bamboo Forest",
      "inquiry": "02-399-1000",
      "ticket": "기관",
      "codename": "무용",
      "use_trgt": "7세 이상 관람 가능 (2019년 이전 출생자)",
      "program": null,
      "lot": "126.9760053",
      "rgstdate": "2026-01-23",
      "strtdate": 1778770800000,
      "place": "세종M씨어터",
      "hmpg_addr": "https://culture.seoul.go.kr/culture/culture/cultureEvent/view.do?cultcode=156602&menuNo=200008",
      "lat": "37.5726241",
      "is_free": "유료"
    }
  ]
}
```

## 데이터 처리 참고
- `date`는 범위 문자열이며 `strtdate`/`end_date`는 epoch(ms) 형식이다.
- `lat`/`lot`는 문자열로 제공되며 좌표 계산 시 숫자 변환이 필요하다.
- `is_free`는 boolean이 아니라 `무료`/`유료` 문자열이다.
