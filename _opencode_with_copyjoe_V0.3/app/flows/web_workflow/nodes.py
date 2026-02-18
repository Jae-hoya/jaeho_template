from typing import Any, Awaitable, Callable, Literal, Protocol

from app.core.errors import AppException, ErrorCode
from app.flows.web_workflow.states import LandingAnalyzeState, SearchThenAnalyzeState, WebSearchState
from app.schemas.web import LandingAnalyzeResponse, WebSearchResult

SearchFn = Callable[[str, int, bool], list[WebSearchResult]]
AnalyzeLandingFn = Callable[[str, bool], Awaitable[LandingAnalyzeResponse]]


class LandingClientBackend(Protocol):
    async def analyze(self, url: str) -> dict[str, Any]:
        ...


class TavilyClientBackend(Protocol):
    def search(self, query: str, max_results: int) -> dict[str, Any]:
        ...


class PrepareSearchNode:
    def __init__(self, tavily_client: TavilyClientBackend | None) -> None:
        self._tavily_client = tavily_client

    def __call__(self, state: WebSearchState) -> dict[str, object]:
        if self._tavily_client is None:
            if state["strict"]:
                raise AppException(
                    status_code=400,
                    code=ErrorCode.web_search_error,
                    message="Tavily API key is missing or Tavily client is unavailable",
                )
            return {
                "should_search": False,
                "raw_items": [],
            }

        return {"should_search": True}


def route_after_prepare_search(state: WebSearchState) -> Literal["search", "to_results"]:
    if state.get("should_search"):
        return "search"
    return "to_results"


class ExecuteSearchNode:
    def __init__(self, tavily_client: TavilyClientBackend | None) -> None:
        self._tavily_client = tavily_client

    def __call__(self, state: WebSearchState) -> dict[str, object]:
        if self._tavily_client is None:
            return {"raw_items": []}

        try:
            response = self._tavily_client.search(
                query=state["query"],
                max_results=state["max_results"],
            )
        except Exception as exc:
            raise AppException(
                status_code=502,
                code=ErrorCode.web_search_error,
                message="Tavily search failed",
                details={"reason": str(exc)},
            ) from exc

        return {"raw_items": list(response.get("results", []))}


class MapSearchResultsNode:
    def __call__(self, state: WebSearchState) -> dict[str, object]:
        rows = list(state.get("raw_items", []))
        return {
            "results": [
                WebSearchResult(
                    title=row.get("title", ""),
                    url=row.get("url", ""),
                    content=row.get("content", ""),
                )
                for row in rows
            ]
        }


class AnalyzeLandingNode:
    def __init__(self, landing_client: LandingClientBackend) -> None:
        self._landing_client = landing_client

    async def __call__(self, state: LandingAnalyzeState) -> dict[str, object]:
        try:
            payload = await self._landing_client.analyze(state["url"])
        except Exception as exc:
            raise AppException(
                status_code=502,
                code=ErrorCode.web_search_error,
                message="Landing page analysis failed",
                details={"reason": str(exc)},
            ) from exc

        return {"payload": payload}


class ToLandingResponseNode:
    def __call__(self, state: LandingAnalyzeState) -> dict[str, object]:
        payload = state.get("payload") or {}
        return {
            "response": LandingAnalyzeResponse(
                url=payload.get("url", state["url"]),
                title=payload.get("title", ""),
                h1=payload.get("h1", []),
                h2=payload.get("h2", []),
                cta_buttons=payload.get("cta_buttons", []),
                body=payload.get("body", ""),
                from_tavily=state["from_tavily"],
            )
        }


class SearchCandidatesNode:
    def __init__(self, search: SearchFn) -> None:
        self._search = search

    def __call__(self, state: SearchThenAnalyzeState) -> dict[str, object]:
        return {
            "results": self._search(state["query"], state["max_results"], True)
        }


class SelectCandidateNode:
    def __call__(self, state: SearchThenAnalyzeState) -> dict[str, object]:
        results = list(state.get("results", []))
        if not results:
            raise AppException(
                status_code=404,
                code=ErrorCode.web_search_error,
                message="No search results found from Tavily",
            )

        return {"selected_url": results[0].url}


class AnalyzeSelectedCandidateNode:
    def __init__(self, analyze_landing: AnalyzeLandingFn) -> None:
        self._analyze_landing = analyze_landing

    async def __call__(self, state: SearchThenAnalyzeState) -> dict[str, object]:
        response = await self._analyze_landing(state["selected_url"], True)
        return {"response": response}
