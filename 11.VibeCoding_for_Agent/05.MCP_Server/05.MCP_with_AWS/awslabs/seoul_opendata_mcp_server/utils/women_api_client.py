"""Seoul Women & Family Foundation Events API client."""

from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from ..config import SeoulAPIConfig


class SeoulWomenEventsClient:
    """Client for Seoul Women & Family Foundation Events API (SeoulWomenPlazaEvent)."""

    def __init__(self, config: SeoulAPIConfig):
        """Initialize the API client.

        Args:
            config: Configuration object with API key and base URL
        """
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            headers={'User-Agent': config.user_agent},
        )

    async def _request(
        self,
        start_index: int = 1,
        end_index: int = 10,
    ) -> Dict[str, Any]:
        """Make a request to Seoul Women Plaza Event API.

        URL Format: {base_url}/{api_key}/json/SeoulWomenPlazaEvent/{start}/{end}

        Args:
            start_index: Start index for pagination (1-based)
            end_index: End index for pagination

        Returns:
            API response as dictionary

        Raises:
            ValueError: If API key is not configured or API returns an error
        """
        if not self.config.api_key:
            raise ValueError(
                'Seoul API key not configured. '
                'Set SEOUL_WOMEN_EVENTS_API_KEY environment variable.'
            )

        # Limit end_index to max 1000
        end_index = min(end_index, 1000)

        url = self.config.get_api_url(start_index=start_index, end_index=end_index)
        logger.debug(f'Requesting Seoul Women Events: {url}')

        try:
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            # Check for API errors
            if 'RESULT' in data:
                result = data['RESULT']
                code = result.get('CODE', '')

                # INFO-000 = success, INFO-200 = no results
                if code not in ['INFO-000', 'INFO-200']:
                    error_msg = result.get('MESSAGE', 'Unknown error')
                    logger.error(f'Seoul API error: {code} - {error_msg}')
                    raise ValueError(f'Seoul API error [{code}]: {error_msg}')

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f'HTTP status error: {e.response.status_code} - {e}')
            raise ValueError(f'API request failed with status {e.response.status_code}: {str(e)}')
        except httpx.HTTPError as e:
            logger.error(f'HTTP error: {e}')
            raise ValueError(f'API request failed: {str(e)}')
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            raise ValueError(f'Failed to process API response: {str(e)}')

    async def search_events(
        self,
        title: Optional[str] = None,
        event_type: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search for Seoul Women & Family Foundation events.

        Args:
            title: Optional filter by event title (substring match)
            event_type: Optional filter by event type
            max_results: Maximum number of results to return (default: 10, max: 1000)

        Returns:
            List of event dictionaries with fields:
                - EVT_REG_NO: Event registration number (key)
                - TITLE: Event title
                - EVT_REG_START_DATE: Registration start date
                - EVT_REG_END_DATE: Registration end date
                - EVT_TYPE: Event type
                - EVT_DATE: Event date
                - EVT_PLACE: Event location
                - EVT_TARGET: Target audience
                - EVT_REG_METHOD: Registration method
                - EVT_SPONSOR: Organizer/Sponsor
                - EVT_CONTACT: Contact information
                - URL: Event URL
        """
        max_results = min(max_results, self.config.max_results, 1000)
        end_index = max_results

        try:
            data = await self._request(start_index=1, end_index=end_index)

            # Extract events from response
            events = data.get('SeoulWomenPlazaEvent', {}).get('row', [])

            if not isinstance(events, list):
                events = [events] if events else []

            # Apply filters
            filtered_events = events

            if title:
                title_lower = title.lower()
                filtered_events = [
                    evt for evt in filtered_events
                    if title_lower in evt.get('TITLE', '').lower()
                ]

            if event_type:
                event_type_lower = event_type.lower()
                filtered_events = [
                    evt for evt in filtered_events
                    if event_type_lower in evt.get('EVT_TYPE', '').lower()
                ]

            return filtered_events[:max_results]

        except ValueError:
            # Re-raise API errors
            raise
        except Exception as e:
            logger.error(f'Error searching events: {e}')
            return []

    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific event by registration number.

        Args:
            event_id: Event registration number (EVT_REG_NO)

        Returns:
            Event dictionary or None if not found
        """
        try:
            # Search with a reasonable batch size
            events = await self.search_events(max_results=100)

            for event in events:
                if event.get('EVT_REG_NO') == event_id:
                    return event

            logger.warning(f'Event not found: {event_id}')
            return None

        except Exception as e:
            logger.error(f'Error getting event {event_id}: {e}')
            return None

    async def get_all_events(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get all available events.

        Args:
            max_results: Maximum number of results (default: 100, max: 1000)

        Returns:
            List of all events
        """
        return await self.search_events(max_results=max_results)

    async def close(self):
        """Close the HTTP client connection."""
        await self.client.aclose()
