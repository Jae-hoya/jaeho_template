from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Tuple

import httpx

from seoul_culture_mcp.models import EventResponse
from seoul_culture_mcp.settings import get_settings


class SeoulAPIError(RuntimeError):
    pass


_KST = timezone(timedelta(hours=9))
_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S.%f",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
)


def _parse_epoch_ms(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    if text.isdigit():
        return int(text)
    for fmt in _DATETIME_FORMATS:
        try:
            parsed = datetime.strptime(text, fmt)
        except ValueError:
            continue
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=_KST)
        return int(parsed.timestamp() * 1000)
    return None


def _normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
    normalized = {str(key).lower(): value for key, value in event.items()}
    for field in ("strtdate", "end_date"):
        parsed = _parse_epoch_ms(normalized.get(field))
        if parsed is not None:
            normalized[field] = parsed
    return normalized


def _normalize_events(data: List[Any]) -> List[Any]:
    normalized: List[Any] = []
    for item in data:
        if isinstance(item, dict):
            normalized.append(_normalize_event(item))
        else:
            normalized.append(item)
    return normalized


def build_request_url(start_index: int, end_index: int) -> str:
    settings = get_settings()
    base_url = settings.base_url.rstrip("/")
    return (
        f"{base_url}/"
        f"{settings.api_key}/"
        f"{settings.response_type}/"
        f"{settings.service_name}/"
        f"{start_index}/"
        f"{end_index}/"
    )


def extract_description_data(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Any]]:
    if isinstance(payload, dict):
        if "DESCRIPTION" in payload and "DATA" in payload:
            return payload.get("DESCRIPTION") or {}, payload.get("DATA") or []
        if "description" in payload and "data" in payload:
            return payload.get("description") or {}, payload.get("data") or []
        if "row" in payload:
            data = payload.get("row") or []
            if isinstance(data, list):
                description = payload.get("DESCRIPTION") or payload.get("description") or {}
                return description, _normalize_events(data)
        if len(payload) == 1:
            inner = next(iter(payload.values()))
            if isinstance(inner, dict):
                if "DESCRIPTION" in inner and "DATA" in inner:
                    return inner.get("DESCRIPTION") or {}, inner.get("DATA") or []
                if "description" in inner and "data" in inner:
                    return inner.get("description") or {}, inner.get("data") or []
                if "row" in inner:
                    data = inner.get("row") or []
                    if isinstance(data, list):
                        description = inner.get("DESCRIPTION") or inner.get("description") or {}
                        return description, _normalize_events(data)
    return {}, []


def _clean_param(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


async def fetch_events(
    start_index: int,
    end_index: int,
    *,
    codename: str | None = None,
    title: str | None = None,
    date: str | None = None,
    client: httpx.AsyncClient | None = None,
) -> Tuple[Dict[str, Any], str]:
    settings = get_settings()
    if not settings.api_key:
        raise SeoulAPIError("SEOUL_API_KEY is required")
    url = build_request_url(start_index, end_index)
    params: Dict[str, str] = {}
    codename = _clean_param(codename)
    title = _clean_param(title)
    date = _clean_param(date)
    if codename:
        params["CODENAME"] = codename
    if title:
        params["TITLE"] = title
    if date:
        params["DATE"] = date
    try:
        if client is None:
            async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client_session:
                response = await client_session.get(url, params=params)
        else:
            response = await client.get(url, params=params)
    except httpx.HTTPError as exc:
        raise SeoulAPIError("HTTP request failed") from exc
    if response.status_code >= 400:
        raise SeoulAPIError(f"HTTP {response.status_code} from Seoul API")
    try:
        payload = response.json()
    except ValueError as exc:
        raise SeoulAPIError("Response was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise SeoulAPIError("Unexpected response format")
    try:
        EventResponse.model_validate(payload)
    except Exception:
        pass
    return payload, str(response.request.url)
