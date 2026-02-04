# 서울 문화행사 MCP Tool 아이디어

`seoul-culture-events-api.md` 기준으로 현재 MCP 서버 패턴에 맞는 추가 도구 아이디어를 정리했습니다.

## 필터 확장
- `search_events_by_theme`: `themecode` 기준 필터
- `search_events_by_place`: `place` 키워드 매칭
- `search_events_by_organizer`: `org_name` 기준 필터
- `search_events_by_target`: `use_trgt` 기준 필터
- `search_events_by_ticket_type`: `ticket`(시민/기관) 기준 필터

## 편의/집계
- `get_paid_events`: `is_free = false` 전용 조회
- `list_event_categories`: `codename` 유니크 목록 + 건수
- `list_event_districts`: `guname` 유니크 목록 + 건수
- `list_event_themes`: `themecode` 유니크 목록 + 건수
- `get_event_stats`: 날짜 범위 내 `codename`, `guname`, `is_free` 요약 통계

## 지리/시간 특화
- `search_events_nearby`: 중심 좌표 + 반경(km) 기반 필터(`lat`/`lot` 사용)
- `search_events_by_registration_date`: `rgstdate` 범위 필터
- `search_events_by_time_keyword`: `pro_time` 키워드 매칭
- `search_events_with_images`: `main_img` 존재 여부 필터
