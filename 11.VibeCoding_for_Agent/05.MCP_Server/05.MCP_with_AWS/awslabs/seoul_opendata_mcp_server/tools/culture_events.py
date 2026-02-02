# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Culture events tool."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from loguru import logger

from ..config import config
from ..utils.culture_api_client import SeoulAPIClient


async def search_culture_events(
    codename: Optional[str] = None,
    title: Optional[str] = None,
    date: Optional[str] = None,
    start_index: int = 1,
    end_index: int = 10,
) -> List[Dict[str, Any]]:
    """Search Seoul cultural events.

    Args:
        codename: Event category (optional)
        title: Event title (optional)
        date: Event date (YYYY-MM-DD or partial) (optional)
        start_index: Start index for pagination
        end_index: End index for pagination

    Returns:
        List of cultural events
    """
    logger.info(
        "Searching culture events: codename={}, title={}, date={}, range={}-{}",
        codename,
        title,
        date,
        start_index,
        end_index,
    )

    client = SeoulAPIClient(config.culture)
    return await client.search_culture_events(
        codename=codename,
        title=title,
        date=date,
        start_index=start_index,
        end_index=end_index,
    )


async def search_public_reservations(
    service_name: Optional[str] = None,
    area_name: Optional[str] = None,
    category: Optional[str] = None,
    start_index: int = 1,
    end_index: int = 100,
) -> List[Dict[str, Any]]:
    """Search Seoul public service reservations for cultural events.

    This tool searches for cultural events and programs that require advance
    reservation through Seoul's public service system. These include museum
    programs, cultural workshops, educational experiences, and other cultural
    activities.

    Args:
        service_name: Name of the service/event to search for (optional)
        area_name: District or area name (e.g., "강남구", "종로구") (optional)
        category: Service category (e.g., "문화교육", "체험활동") (optional)
        start_index: Start index for pagination (default: 1)
        end_index: End index for pagination (default: 100, max: 1000)

    Returns:
        List of public service reservations with details including:
        - SVCID: Service ID
        - SVCNM: Service name
        - SVCSTATNM: Service status (e.g., "접수중", "접수종료")
        - PLACENM: Venue name
        - RCPTBGNDT: Reservation start datetime
        - RCPTENDDT: Reservation end datetime
        - AREANM: District name
        - USETGTINFO: Target audience information
        - PAYATNM: Payment method
        - TELNO: Contact phone number
        - V_MAX/V_MIN: Age restrictions
        - REVSTDDAY: Cancellation deadline
        - DTLCONT: Detailed description (may contain HTML)
        - X/Y: Coordinates (WGS84)
    """
    logger.info(
        "Searching public reservations: service_name={}, area_name={}, category={}, range={}-{}",
        service_name,
        area_name,
        category,
        start_index,
        end_index,
    )

    client = SeoulAPIClient(config.culture)
    return await client.search_public_reservations(
        service_name=service_name,
        area_name=area_name,
        category=category,
        start_index=start_index,
        end_index=end_index,
    )
