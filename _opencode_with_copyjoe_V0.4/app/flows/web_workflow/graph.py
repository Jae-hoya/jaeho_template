from typing import Any

from langgraph.graph import END, START, StateGraph

from app.flows.web_workflow.nodes import (
    AnalyzeLandingNode,
    AnalyzeSelectedCandidateNode,
    ExecuteSearchNode,
    MapSearchResultsNode,
    PrepareSearchNode,
    SearchCandidatesNode,
    SelectCandidateNode,
    ToLandingResponseNode,
    route_after_prepare_search,
)
from app.flows.web_workflow.states import LandingAnalyzeState, SearchThenAnalyzeState, WebSearchState
from app.integrations.landing_page_client import LandingPageClient
from app.schemas.web import LandingAnalyzeResponse, WebSearchResult


class WebWorkflowGraph:
    def __init__(self, landing_client: LandingPageClient, tavily_client: Any | None) -> None:
        search_builder = StateGraph(WebSearchState)
        search_builder.add_node("prepare", PrepareSearchNode(tavily_client=tavily_client))
        search_builder.add_node("search", ExecuteSearchNode(tavily_client=tavily_client))
        search_builder.add_node("to_results", MapSearchResultsNode())
        search_builder.add_edge(START, "prepare")
        search_builder.add_conditional_edges(
            "prepare",
            route_after_prepare_search,
            {
                "search": "search",
                "to_results": "to_results",
            },
        )
        search_builder.add_edge("search", "to_results")
        search_builder.add_edge("to_results", END)
        self._search_graph = search_builder.compile()

        landing_builder = StateGraph(LandingAnalyzeState)
        landing_builder.add_node("analyze", AnalyzeLandingNode(landing_client=landing_client))
        landing_builder.add_node("to_response", ToLandingResponseNode())
        landing_builder.add_edge(START, "analyze")
        landing_builder.add_edge("analyze", "to_response")
        landing_builder.add_edge("to_response", END)
        self._landing_graph = landing_builder.compile()

        search_then_analyze_builder = StateGraph(SearchThenAnalyzeState)
        search_then_analyze_builder.add_node("search", SearchCandidatesNode(search=self.run_search))
        search_then_analyze_builder.add_node("select", SelectCandidateNode())
        search_then_analyze_builder.add_node("analyze", AnalyzeSelectedCandidateNode(analyze_landing=self.run_analyze_landing_page))
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
