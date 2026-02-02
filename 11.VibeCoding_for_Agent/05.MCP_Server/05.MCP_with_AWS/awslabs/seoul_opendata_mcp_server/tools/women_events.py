"""Seoul Women & Family Foundation events tools."""

from typing import Any, Dict, List, Optional

from loguru import logger

from ..config import config
from ..utils.women_api_client import SeoulWomenEventsClient


async def search_women_events(
    title: Optional[str] = None,
    event_type: Optional[str] = None,
    max_results: int = 10,
) -> List[Dict[str, Any]]:
    """Search for Seoul Women & Family Foundation events.

    Search events organized by Seoul Women & Family Foundation including cultural programs,
    educational workshops, seminars, and community activities.

    Args:
        title: Search by event title (partial match, optional)
        event_type: Filter by event type/category in Korean (e.g., '공연', '전시', '강좌', '체험') (optional)
        max_results: Maximum number of results to return (default: 10, max: 100)

    Returns:
        List of events with details including:
        - EVT_REG_NO: Event registration number
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
    logger.info(
        f'Searching women events: title={title}, event_type={event_type}, max={max_results}'
    )

    client = SeoulWomenEventsClient(config.women)

    try:
        results = await client.search_events(
            title=title,
            event_type=event_type,
            max_results=min(max_results, 100),
        )

        logger.success(f'Found {len(results)} women & family events')
        return results

    except ValueError as e:
        logger.error(f'API error: {e}')
        raise
    except Exception as e:
        logger.error(f'Error searching women events: {e}')
        raise ValueError(f'Failed to search events: {str(e)}')
    finally:
        await client.close()


async def get_event_details(event_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific event by registration number.

    Retrieve comprehensive details about an event by its unique registration number.

    Args:
        event_id: Event registration number (EVT_REG_NO) obtained from search results

    Returns:
        Detailed event information or None if not found
    """
    logger.info(f'Getting event details for: {event_id}')

    client = SeoulWomenEventsClient(config.women)

    try:
        result = await client.get_event_by_id(event_id)

        if result:
            logger.success(f'Retrieved details for event: {event_id}')
        else:
            logger.warning(f'Event not found: {event_id}')

        return result

    except ValueError as e:
        logger.error(f'API error: {e}')
        raise
    except Exception as e:
        logger.error(f'Error getting event details: {e}')
        raise ValueError(f'Failed to get event details: {str(e)}')
    finally:
        await client.close()


async def get_all_women_events(max_results: int = 50) -> List[Dict[str, Any]]:
    """Get all available Seoul Women & Family Foundation events.

    Retrieve a list of all currently available events without any filters.
    Useful for browsing all upcoming events and programs.

    Args:
        max_results: Maximum number of results to return (default: 50, max: 100)

    Returns:
        List of all available events
    """
    logger.info(f'Getting all women events (max: {max_results})')

    client = SeoulWomenEventsClient(config.women)

    try:
        results = await client.get_all_events(max_results=min(max_results, 100))

        logger.success(f'Retrieved {len(results)} total events')
        return results

    except ValueError as e:
        logger.error(f'API error: {e}')
        raise
    except Exception as e:
        logger.error(f'Error getting all events: {e}')
        raise ValueError(f'Failed to get all events: {str(e)}')
    finally:
        await client.close()
