from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import re
from typing import Any, Tuple

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_KST = timezone(timedelta(hours=9))


def validate_index_range(start_index: int, end_index: int) -> None:
    if start_index < 1:
        raise ValueError("start_index must be >= 1")
    if end_index < start_index:
        raise ValueError("end_index must be >= start_index")


def validate_date_str(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if not _DATE_RE.match(value):
        raise ValueError("date must be YYYY-MM-DD")
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("date must be YYYY-MM-DD") from exc
    return value


def normalize_limit(
    value: int | None,
    default: int,
    *,
    min_value: int = 1,
    max_value: int = 500,
) -> int:
    if value is None:
        return default
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def normalize_page_size(
    value: int | None,
    default: int,
    *,
    min_value: int = 1,
    max_value: int = 100,
) -> int:
    if value is None:
        return default
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def parse_event_date_range(event: dict) -> Tuple[date | None, date | None]:
    start_date = _date_from_epoch(event.get("strtdate"))
    end_date = _date_from_epoch(event.get("end_date"))
    if start_date or end_date:
        return start_date, end_date
    date_value = event.get("date")
    if isinstance(date_value, str):
        parts = [p.strip() for p in date_value.split("~") if p.strip()]
        if len(parts) == 1 and _DATE_RE.match(parts[0]):
            try:
                d = date.fromisoformat(parts[0])
                return d, d
            except ValueError:
                return None, None
        if len(parts) == 2 and _DATE_RE.match(parts[0]) and _DATE_RE.match(parts[1]):
            try:
                return date.fromisoformat(parts[0]), date.fromisoformat(parts[1])
            except ValueError:
                return None, None
    return None, None


def _date_from_epoch(value: Any) -> date | None:
    if value is None:
        return None
    try:
        ms = int(value)
    except (TypeError, ValueError):
        return None
    try:
        return datetime.fromtimestamp(ms / 1000, tz=_KST).date()
    except (OverflowError, OSError, ValueError):
        return None


def matches_title(event: dict, query: str) -> bool:
    if not query:
        return True
    title = event.get("title")
    if not isinstance(title, str):
        return False
    return query.lower() in title.lower()


def matches_guname(event: dict, guname: str | None) -> bool:
    if not guname:
        return True
    value = event.get("guname")
    if not isinstance(value, str):
        return False
    return value.strip() == guname.strip()


def matches_is_free(event: dict, is_free: bool | None) -> bool:
    if is_free is None:
        return True
    value = event.get("is_free")
    if not isinstance(value, str):
        return False
    value = value.strip()
    if is_free:
        return value == "무료"
    return value == "유료"


def matches_date_range(event: dict, start: date, end: date) -> bool:
    event_start, event_end = parse_event_date_range(event)
    if event_start is None and event_end is None:
        return False
    if event_start is None:
        event_start = event_end
    if event_end is None:
        event_end = event_start
    return not (event_end < start or event_start > end)
