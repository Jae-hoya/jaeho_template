from typing import Any, TypedDict

from app.schemas.web import LandingAnalyzeResponse, WebSearchResult


class WebSearchState(TypedDict):
    query: str
    max_results: int
    strict: bool
    should_search: bool
    raw_items: list[dict[str, Any]]
    results: list[WebSearchResult]


class LandingAnalyzeState(TypedDict):
    url: str
    from_tavily: bool
    payload: dict[str, Any] | None
    response: LandingAnalyzeResponse | None


class SearchThenAnalyzeState(TypedDict):
    query: str
    max_results: int
    results: list[WebSearchResult]
    selected_url: str
    response: LandingAnalyzeResponse | None
