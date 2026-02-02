# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Seoul Open Data MCP Server - Unified server for Seoul Open Data APIs."""

from loguru import logger
from mcp.server.fastmcp import FastMCP

from .tools.culture_events import search_culture_events, search_public_reservations
from .tools.women_events import (
    get_all_women_events,
    get_event_details,
    search_women_events,
)

APP_NAME = "seoul-opendata"

mcp = FastMCP(
    name=APP_NAME,
    instructions=(
        "Use this server to access Seoul Open Data APIs including:\n"
        "1. Cultural Events: Search Seoul cultural events (performances, exhibitions, festivals) "
        "and public service reservations (museum programs, workshops, educational experiences).\n"
        "2. Women & Family Events: Search and retrieve Seoul Women & Family Foundation event "
        "information including cultural programs, educational workshops, seminars, and community "
        "activities organized by Seoul Women Plaza and related organizations.\n\n"
        "Available filters: category, title, date, area, event type, etc."
    ),
)

# Register Culture Events tools
mcp.tool()(search_culture_events)
mcp.tool()(search_public_reservations)

# Register Women Events tools
mcp.tool()(search_women_events)
mcp.tool()(get_event_details)
mcp.tool()(get_all_women_events)


def main() -> None:
    """Main entry point for the MCP server."""
    logger.info("Starting {} MCP server", APP_NAME)
    mcp.run()


if __name__ == "__main__":
    main()
