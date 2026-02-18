from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.core.errors import AppException, ErrorCode
from app.integrations.landing_page_client import LandingPageClient
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


class WebWorkflowGraph:
    def __init__(self, landing_client: LandingPageClient, tavily_client: Any | None) -> None:
        self._landing_client = landing_client
        self._tavily_client = tavily_client

        search_builder = StateGraph(WebSearchState)
        search_builder.add_node("prepare", self._prepare_search)
        search_builder.add_node("search", self._execute_search)
        search_builder.add_node("to_results", self._map_search_results)
        search_builder.add_edge(START, "prepare")
        search_builder.add_conditional_edges(
            "prepare",
            self._route_after_prepare_search,
            {
                "search": "search",
                "to_results": "to_results",
            },
        )
        search_builder.add_edge("search", "to_results")
        search_builder.add_edge("to_results", END)
        self._search_graph = search_builder.compile()

        landing_builder = StateGraph(LandingAnalyzeState)
        landing_builder.add_node("analyze", self._analyze_landing)
        landing_builder.add_node("to_response", self._to_landing_response)
        landing_builder.add_edge(START, "analyze")
        landing_builder.add_edge("analyze", "to_response")
        landing_builder.add_edge("to_response", END)
        self._landing_graph = landing_builder.compile()

        search_then_analyze_builder = StateGraph(SearchThenAnalyzeState)
        search_then_analyze_builder.add_node("search", self._search_candidates)
        search_then_analyze_builder.add_node("select", self._select_candidate)
        search_then_analyze_builder.add_node("analyze", self._analyze_selected_candidate)
        search_then_analyze_builder.add_edge(START, "search")
        search_then_analyze_builder.add_edge("search", "select")
        search_then_analyze_builder.add_edge("select", "analyze")
        search_then_analyze_builder.add_edge("analyze", END)
        self._search_then_analyze_graph = search_then_analyze_builder.compile()

    def run_search(self, query: str, max_results: int, strict: bool = True) -> list[WebSearchResult]:
        state = self._search_graph.invoke(
            {
                "query": query,
                "max_results": max_results,
                "strict": strict,
                "should_search": False,
                "raw_items": [],
                "results": [],
            }
        )
        return list(state.get("results", []))

    async def run_analyze_landing_page(self, url: str, from_tavily: bool = False) -> LandingAnalyzeResponse:
        state = await self._landing_graph.ainvoke(
            {
                "url": url,
                "from_tavily": from_tavily,
                "payload": None,
                "response": None,
            }
        )
        response = state.get("response")
        if response is None:
            raise RuntimeError("Landing analyze graph failed to produce a response")
        return response

    async def run_search_then_analyze(self, query: str, max_results: int) -> LandingAnalyzeResponse:
        state = await self._search_then_analyze_graph.ainvoke(
            {
                "query": query,
                "max_results": max_results,
                "results": [],
                "selected_url": "",
                "response": None,
            }
        )
        response = state.get("response")
        if response is None:
            raise RuntimeError("Search-then-analyze graph failed to produce a response")
        return response

    def _prepare_search(self, state: WebSearchState) -> dict[str, object]:
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

    def _route_after_prepare_search(self, state: WebSearchState) -> str:
        if state.get("should_search"):
            return "search"
        return "to_results"

    def _execute_search(self, state: WebSearchState) -> dict[str, object]:
        if self._tavily_client is None:
            return {"raw_items": []}

        try:
            response = self._tavily_client.search(query=state["query"], max_results=state["max_results"])
        except Exception as exc:
            raise AppException(
                status_code=502,
                code=ErrorCode.web_search_error,
                message="Tavily search failed",
                details={"reason": str(exc)},
            ) from exc

        return {"raw_items": list(response.get("results", []))}

    def _map_search_results(self, state: WebSearchState) -> dict[str, object]:
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

    async def _analyze_landing(self, state: LandingAnalyzeState) -> dict[str, object]:
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

    def _to_landing_response(self, state: LandingAnalyzeState) -> dict[str, object]:
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

    def _search_candidates(self, state: SearchThenAnalyzeState) -> dict[str, object]:
        results = self.run_search(query=state["query"], max_results=state["max_results"], strict=True)
        return {"results": results}

    def _select_candidate(self, state: SearchThenAnalyzeState) -> dict[str, object]:
        results = list(state.get("results", []))
        if not results:
            raise AppException(
                status_code=404,
                code=ErrorCode.web_search_error,
                message="No search results found from Tavily",
            )

        return {"selected_url": results[0].url}

    async def _analyze_selected_candidate(self, state: SearchThenAnalyzeState) -> dict[str, object]:
        response = await self.run_analyze_landing_page(state["selected_url"], from_tavily=True)
        return {"response": response}
