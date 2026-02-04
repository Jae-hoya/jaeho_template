# Seoul Culture MCP Tool Ideas

Based on `seoul-culture-events-api.md`, here are practical tool additions that fit the current MCP server pattern.

## Filter Extensions
- `search_events_by_theme`: filter by `themecode`
- `search_events_by_place`: keyword match on `place`
- `search_events_by_organizer`: filter by `org_name`
- `search_events_by_target`: filter by `use_trgt`
- `search_events_by_ticket_type`: filter by `ticket` (citizen/organization)

## Convenience and Aggregation
- `get_paid_events`: filter by `is_free = false`
- `list_event_categories`: unique `codename` list + counts
- `list_event_districts`: unique `guname` list + counts
- `list_event_themes`: unique `themecode` list + counts
- `get_event_stats`: summary counts by `codename`, `guname`, `is_free` within a date range

## Geo and Time-focused
- `search_events_nearby`: center coordinate + radius (km) using `lat`/`lot`
- `search_events_by_registration_date`: filter by `rgstdate` range
- `search_events_by_time_keyword`: keyword match on `pro_time`
- `search_events_with_images`: filter where `main_img` is present
