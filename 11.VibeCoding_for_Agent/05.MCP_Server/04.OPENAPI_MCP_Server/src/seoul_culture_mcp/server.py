from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Tuple

import httpx
from fastmcp import FastMCP

from seoul_culture_mcp.clients.seoul_api import (
    SeoulAPIError,
    extract_description_data,
    fetch_events,
)
from seoul_culture_mcp.settings import get_settings
from seoul_culture_mcp.utils.validation import (
    matches_date_range,
    matches_guname,
    matches_is_free,
    matches_title,
    normalize_limit,
    normalize_page_size,
    validate_date_str,
    validate_index_range,
)

mcp = FastMCP(name="Seoul Cultural Events")


def _filter_meta(**kwargs: Any) -> Dict[str, Any]:
    return {key: value for key, value in kwargs.items() if value not in (None, "")}


def _parse_is_free_value(value: str) -> bool:
    if value is None:
        raise ValueError("is_free is required")
    text = value.strip()
    if text == "무료":
        return True
    if text == "유료":
        return False
    raise ValueError("is_free must be '무료' or '유료'")


async def _get_cultural_events_page(
    start_index: int,
    end_index: int,
    *,
    codename: str | None = None,
    title: str | None = None,
    date: str | None = None,
) -> Dict[str, Any]:
    validate_index_range(start_index, end_index)
    date = validate_date_str(date)
    try:
        payload, request_url = await fetch_events(
            start_index,
            end_index,
            codename=codename,
            title=title,
            date=date,
        )
    except SeoulAPIError as exc:
        raise RuntimeError(str(exc)) from exc
    description, data = extract_description_data(payload)
    meta = {
        "start_index": start_index,
        "end_index": end_index,
        "filters": _filter_meta(codename=codename, title=title, date=date),
        "request_url": request_url,
    }
    return {"description": description, "data": data, "meta": meta}


async def _search_events(
    *,
    query: str | None = None,
    codename: str | None = None,
    date_filter: str | None = None,
    guname: str | None = None,
    is_free: bool | None = None,
    date_range: Tuple[date, date] | None = None,
    limit: int = 50,
    page_size: int = 500,
) -> Dict[str, Any]:
    limit = normalize_limit(limit, 50)
    page_size = normalize_page_size(page_size, 500, max_value=1000)
    items: List[Dict[str, Any]] = []
    page = 1
    pages_scanned = 0
    last_request_url = None

    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
        while len(items) < limit:
            start_index = (page - 1) * page_size + 1
            end_index = start_index + page_size - 1
            try:
                payload, request_url = await fetch_events(
                    start_index,
                    end_index,
                    codename=codename,
                    title=query,
                    date=date_filter,
                    client=client,
                )
            except SeoulAPIError as exc:
                raise RuntimeError(str(exc)) from exc
            last_request_url = request_url
            pages_scanned += 1
            _, data = extract_description_data(payload)
            if not data:
                break
            for event in data:
                if query and not matches_title(event, query):
                    continue
                if guname and not matches_guname(event, guname):
                    continue
                if is_free is not None and not matches_is_free(event, is_free):
                    continue
                if date_range and not matches_date_range(event, date_range[0], date_range[1]):
                    continue
                items.append(event)
                if len(items) >= limit:
                    break
            if len(data) < page_size:
                break
            page += 1

    meta = {
        "limit": limit,
        "page_size": page_size,
        "pages_scanned": pages_scanned,
        "total_matched": len(items),
        "filters": _filter_meta(
            query=query,
            codename=codename,
            date=date_filter,
            guname=guname,
            is_free=is_free,
        ),
        "request_url": last_request_url,
    }
    return {"items": items, "meta": meta}


@mcp.tool
async def get_cultural_events(
    start_index: int = 1,
    end_index: int = 10,
    codename: str | None = None,
    title: str | None = None,
    date: str | None = None,
) -> Dict[str, Any]:
    """Fetch a page of cultural events from Seoul OpenAPI."""
    return await _get_cultural_events_page(
        start_index,
        end_index,
        codename=codename,
        title=title,
        date=date,
    )


@mcp.tool
async def list_cultural_events(
    start_index: int = 1,
    end_index: int = 10,
    codename: str | None = None,
    title: str | None = None,
    date: str | None = None,
) -> Dict[str, Any]:
    """Alias of get_cultural_events for pagination-based listing."""
    return await _get_cultural_events_page(
        start_index,
        end_index,
        codename=codename,
        title=title,
        date=date,
    )


@mcp.tool
async def search_cultural_events(
    query: str | None = None,
    codename: str | None = None,
    date: str | None = None,
    limit: int = 50,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Search events with optional query and filters."""
    date = validate_date_str(date)
    return await _search_events(
        query=query,
        codename=codename,
        date_filter=date,
        limit=limit,
        page_size=page_size,
    )


@mcp.tool
async def search_events_by_title(
    title: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """Search events by title keyword."""
    if not title or not title.strip():
        raise ValueError("title is required")
    return await _search_events(query=title, limit=limit)


async def _get_event_free_status_result(
    title: str,
    limit: int,
    page_size: int,
) -> Dict[str, Any]:
    if not title or not title.strip():
        raise ValueError("title is required")
    results = await _search_events(query=title, limit=limit, page_size=page_size)
    items = [
        {
            "title": event.get("title"),
            "is_free": event.get("is_free"),
            "date": event.get("date"),
            "guname": event.get("guname"),
            "place": event.get("place"),
            "hmpg_addr": event.get("hmpg_addr"),
        }
        for event in results.get("items", [])
    ]
    return {"items": items, "meta": results.get("meta", {})}


@mcp.tool
async def get_event_free_status(
    title: str,
    limit: int = 10,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Return free/paid status for events matching a title."""
    return await _get_event_free_status_result(title, limit, page_size)


@mcp.tool
async def get_is_free_by_title(
    title: str,
    limit: int = 10,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Alias of get_event_free_status for title queries."""
    return await _get_event_free_status_result(title, limit, page_size)


@mcp.tool
async def search_events_by_date_range(
    start_date: str,
    end_date: str | None = None,
    limit: int = 20,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Search events that overlap with a date range."""
    start_date_value = validate_date_str(start_date)
    if not start_date_value:
        raise ValueError("start_date is required")
    end_date_value = validate_date_str(end_date) or start_date_value
    start = date.fromisoformat(start_date_value)
    end = date.fromisoformat(end_date_value)
    if end < start:
        raise ValueError("end_date must be >= start_date")
    date_filter = start_date_value if start == end else None
    return await _search_events(
        date_filter=date_filter,
        date_range=(start, end),
        limit=limit,
        page_size=page_size,
    )


@mcp.tool
async def search_events_by_category(
    category: str,
    is_free: bool | None = None,
    limit: int = 15,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Search events by category (codename)."""
    if not category or not category.strip():
        raise ValueError("category is required")
    return await _search_events(
        codename=category,
        is_free=is_free,
        limit=limit,
        page_size=page_size,
    )


@mcp.tool
async def search_events_by_is_free(
    is_free: bool,
    guname: str | None = None,
    limit: int = 20,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Search events by free/paid status."""
    return await _search_events(
        is_free=is_free,
        guname=guname,
        limit=limit,
        page_size=page_size,
    )


@mcp.tool
async def search_events_by_is_free_value(
    is_free: str,
    guname: str | None = None,
    limit: int = 20,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Search events by IS_FREE string value (무료/유료)."""
    return await _search_events(
        is_free=_parse_is_free_value(is_free),
        guname=guname,
        limit=limit,
        page_size=page_size,
    )


@mcp.tool
async def get_free_events(
    limit: int = 20,
    guname: str | None = None,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Fetch free events, optionally filtered by district (guname)."""
    return await _search_events(
        is_free=True,
        guname=guname,
        limit=limit,
        page_size=page_size,
    )


@mcp.tool
async def get_event_by_location(
    guname: str,
    limit: int = 15,
    page_size: int = 500,
) -> Dict[str, Any]:
    """Search events by district (guname)."""
    if not guname or not guname.strip():
        raise ValueError("guname is required")
    return await _search_events(
        guname=guname,
        limit=limit,
        page_size=page_size,
    )


@mcp.tool
async def get_event_field_map() -> Dict[str, Any]:
    """Return the DESCRIPTION field map from a minimal request."""
    try:
        payload, request_url = await fetch_events(1, 1)
    except SeoulAPIError as exc:
        raise RuntimeError(str(exc)) from exc
    description, _ = extract_description_data(payload)
    return {"description": description, "meta": {"request_url": request_url}}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
