from typing import Callable, Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas.common import SourceItem
from app.schemas.copy import CopyGenerateRequest, CopyStructuredOutput
from app.services.rag_service import RagService
from app.services.web_search_service import WebSearchService


class CopyGraphState(TypedDict):
    request: CopyGenerateRequest
    query: str
    context_blocks: list[str]
    sources: list[SourceItem]
    output: CopyStructuredOutput | None


class CopyGenerationGraph:
    def __init__(
        self,
        rag_service: RagService,
        web_search_service: WebSearchService,
        generator: Callable[[CopyGenerateRequest, str], CopyStructuredOutput],
    ) -> None:
        self._rag_service = rag_service
        self._web_search_service = web_search_service
        self._generator = generator

        builder = StateGraph(CopyGraphState)
        builder.add_node("prepare", self._prepare)
        builder.add_node("rag", self._collect_rag)
        builder.add_node("web", self._collect_web)
        builder.add_node("generate", self._generate)

        builder.add_edge(START, "prepare")
        builder.add_conditional_edges(
            "prepare",
            self._route_after_prepare,
            {
                "rag": "rag",
                "web": "web",
                "generate": "generate",
            },
        )
        builder.add_conditional_edges(
            "rag",
            self._route_after_rag,
            {
                "web": "web",
                "generate": "generate",
            },
        )
        builder.add_edge("web", "generate")
        builder.add_edge("generate", END)

        self._graph = builder.compile()

    def run(self, request: CopyGenerateRequest) -> tuple[CopyStructuredOutput, list[SourceItem]]:
        state = self._graph.invoke(
            {
                "request": request,
                "query": "",
                "context_blocks": [],
                "sources": [],
                "output": None,
            }
        )

        output = state.get("output")
        if output is None:
            output = self._generator(request, "")
        return output, state.get("sources", [])

    def _prepare(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]
        query = f"{request.product_name} {request.target_audience} {request.pain_point}"
        return {
            "query": query,
            "context_blocks": [],
            "sources": [],
        }

    def _route_after_prepare(self, state: CopyGraphState) -> Literal["rag", "web", "generate"]:
        request = state["request"]
        if request.use_rag:
            return "rag"
        if request.web_search_mode:
            return "web"
        return "generate"

    def _collect_rag(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]
        query = state["query"]

        context_blocks = list(state.get("context_blocks", []))
        sources = list(state.get("sources", []))

        rag_context, rag_sources = self._rag_service.build_context(query=query, top_k=request.top_k)
        if rag_context:
            context_blocks.append(rag_context)
            sources.extend(rag_sources)

        return {
            "context_blocks": context_blocks,
            "sources": sources,
        }

    def _route_after_rag(self, state: CopyGraphState) -> Literal["web", "generate"]:
        request = state["request"]
        if request.web_search_mode:
            return "web"
        return "generate"

    def _collect_web(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]

        context_blocks = list(state.get("context_blocks", []))
        sources = list(state.get("sources", []))

        web_results = self._web_search_service.search(
            query=f"{request.product_name} {request.channel}",
            max_results=request.top_k,
            strict=False,
        )

        if web_results:
            context_blocks.append("\n\n".join(item.content for item in web_results if item.content))
            sources.extend(
                [
                    SourceItem(
                        source_type="web",
                        title=item.title,
                        url=item.url,
                        snippet=item.content[:500],
                    )
                    for item in web_results
                ]
            )

        return {
            "context_blocks": context_blocks,
            "sources": sources,
        }

    def _generate(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]
        context_text = "\n\n".join(state.get("context_blocks", []))
        output = self._generator(request, context_text)
        return {"output": output}
