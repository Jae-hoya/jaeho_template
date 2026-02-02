# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

"""Configuration for the Seoul Open Data MCP server."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field


class CultureEventsConfig(BaseModel):
    """Configuration for Seoul Culture Events API."""

    api_key: str = Field(
        default_factory=lambda: os.getenv("SEOUL_CULTURE_API_KEY", ""),
        description="Seoul Open Data API key for culture events",
    )
    base_url: str = Field(
        default_factory=lambda: os.getenv("SEOUL_API_BASE_URL", "http://openapi.seoul.go.kr:8088"),
        description="Base URL for Seoul Open Data API",
    )
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    max_results: int = Field(default=1000, description="Maximum results per request")
    user_agent: str = Field(
        default="seoul-opendata-mcp-server/1.0",
        description="User agent for API requests",
    )

    def get_api_url(self, service: str, start_index: int, end_index: int) -> str:
        """Build the API URL for a specific service."""
        return f"{self.base_url}/{self.api_key}/json/{service}/{start_index}/{end_index}"


class WomenEventsConfig(BaseModel):
    """Configuration for Seoul Women & Family Events API."""

    api_key: str = Field(
        default_factory=lambda: os.getenv("SEOUL_WOMEN_API_KEY", ""),
        description="Seoul Open Data API key for women events",
    )
    base_url: str = Field(
        default="http://openapi.seoul.go.kr:8088",
        description="Base URL for Seoul Open Data API",
    )
    service_name: str = Field(
        default="SeoulWomenPlazaEvent",
        description="API service name for Women & Family Foundation events",
    )
    timeout: float = Field(default=30.0, description="Request timeout in seconds")
    max_results: int = Field(default=100, description="Maximum results per request")
    user_agent: str = Field(
        default="seoul-opendata-mcp-server/1.0",
        description="User agent for API requests",
    )

    def get_api_url(
        self,
        start_index: int = 1,
        end_index: int = 10,
        service: str | None = None,
    ) -> str:
        """Generate API URL for Seoul Women Plaza Event service."""
        if not self.api_key:
            raise ValueError(
                "SEOUL_WOMEN_API_KEY environment variable not configured. "
                "Please set your Seoul Open Data API key."
            )

        service_name = service or self.service_name
        return f"{self.base_url}/{self.api_key}/json/{service_name}/{start_index}/{end_index}"


class SeoulOpenDataConfig(BaseModel):
    """Unified configuration for Seoul Open Data MCP Server."""

    culture: CultureEventsConfig = Field(
        default_factory=CultureEventsConfig,
        description="Culture events API configuration",
    )
    women: WomenEventsConfig = Field(
        default_factory=WomenEventsConfig,
        description="Women events API configuration",
    )


config = SeoulOpenDataConfig()
