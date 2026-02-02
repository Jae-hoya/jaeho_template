# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Seoul Open Data API client."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import httpx
from loguru import logger

from ..config import SeoulAPIConfig

SERVICE_NAME = "culturalEventInfo"
PUBLIC_RESERVATION_SERVICE = "ListPublicReservationCulture"
SUCCESS_CODE = "INFO-000"


class SeoulAPIClient:
    """Client for Seoul Open Data API."""

    def __init__(self, config: SeoulAPIConfig) -> None:
        self.config = config

    async def _request(self, service: str, start_index: int, end_index: int) -> Dict[str, Any]:
        if not self.config.api_key:
            raise ValueError("Seoul API key not configured. Set SEOUL_CULTURE_API_KEY.")

        url = self.config.get_api_url(service, start_index, end_index)
        logger.debug("Requesting: {}", url)

        async with httpx.AsyncClient(
            timeout=self.config.timeout,
            headers={"User-Agent": self.config.user_agent},
        ) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPError as exc:
                logger.error("HTTP error: {}", exc)
                raise ValueError("API request failed") from exc

        payload = data.get(service)
        if payload is None:
            raise ValueError("Unexpected API response format.")

        result = payload.get("RESULT")
        if result and result.get("CODE") != SUCCESS_CODE:
            message = result.get("MESSAGE", "Unknown error")
            raise ValueError(f"Seoul API error: {message}")

        return payload

    async def search_culture_events(
        self,
        codename: Optional[str] = None,
        title: Optional[str] = None,
        date: Optional[str] = None,
        start_index: int = 1,
        end_index: int = 10,
    ) -> List[Dict[str, Any]]:
        if end_index < start_index:
            raise ValueError("end_index must be greater than or equal to start_index")
        max_span = self.config.max_results
        if end_index - start_index + 1 > max_span:
            end_index = start_index + max_span - 1

        payload = await self._request(SERVICE_NAME, start_index, end_index)
        rows = payload.get("row") or payload.get("ROW") or []
        if not rows:
            return []

        def matches(item: Dict[str, Any], key: str, expected: Optional[str]) -> bool:
            if expected is None:
                return True
            value = _lookup_value(item, key)
            if value is None:
                return False
            return expected.casefold() in str(value).casefold()

        filtered: List[Dict[str, Any]] = []
        for item in rows:
            if not matches(item, "CODENAME", codename):
                continue
            if not matches(item, "TITLE", title):
                continue
            if not matches(item, "DATE", date):
                continue
            filtered.append(item)

        return filtered

    async def search_public_reservations(
        self,
        service_name: Optional[str] = None,
        area_name: Optional[str] = None,
        category: Optional[str] = None,
        start_index: int = 1,
        end_index: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search Seoul public service reservations.

        Args:
            service_name: Service/event name to search for (optional)
            area_name: District/area name (optional)
            category: Service category (optional)
            start_index: Start index for pagination (default: 1)
            end_index: End index for pagination (default: 100, max: 1000)

        Returns:
            List of public service reservations matching the criteria
        """
        if end_index < start_index:
            raise ValueError("end_index must be greater than or equal to start_index")
        max_span = self.config.max_results
        if end_index - start_index + 1 > max_span:
            end_index = start_index + max_span - 1

        payload = await self._request(PUBLIC_RESERVATION_SERVICE, start_index, end_index)
        rows = payload.get("row") or payload.get("ROW") or []
        if not rows:
            return []

        def matches(item: Dict[str, Any], key: str, expected: Optional[str]) -> bool:
            if expected is None:
                return True
            value = _lookup_value(item, key)
            if value is None:
                return False
            return expected.casefold() in str(value).casefold()

        filtered: List[Dict[str, Any]] = []
        for item in rows:
            if not matches(item, "SVCNM", service_name):
                continue
            if not matches(item, "AREANM", area_name):
                continue
            if not matches(item, "MINCLASSNM", category):
                continue
            filtered.append(item)

        return filtered


def _lookup_value(item: Dict[str, Any], key: str) -> Optional[Any]:
    candidates: Iterable[str] = (key, key.lower(), key.upper())
    for candidate in candidates:
        if candidate in item:
            return item[candidate]
    return None
