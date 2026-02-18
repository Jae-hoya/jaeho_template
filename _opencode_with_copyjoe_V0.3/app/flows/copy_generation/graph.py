from langgraph.graph import END, START, StateGraph

from app.flows.copy_generation.chains import build_retrieval_query
from app.flows.copy_generation.nodes import (
    CollectRagNode,
    CollectWebNode,
    CopyGenerator,
    GenerateNode,
    PrepareNode,
    RagContextService,
    WebSearchService,
    route_after_prepare,
    route_after_rag,
)
from app.flows.copy_generation.states import CopyGraphState
from app.schemas.common import SourceItem
from app.schemas.copy import CopyGenerateRequest, CopyStructuredOutput


class CopyGenerationGraph:
    def __init__(
        self,
        rag_service: RagContextService,
        web_search_service: WebSearchService,
        generator: CopyGenerator,
    ) -> None:
        self._generator = generator

        builder = StateGraph(CopyGraphState)
        builder.add_node("prepare", PrepareNode(build_retrieval_query))
        builder.add_node("rag", CollectRagNode(rag_service))
        builder.add_node("web", CollectWebNode(web_search_service))
        builder.add_node("generate", GenerateNode(generator))

        builder.add_edge(START, "prepare")
        builder.add_conditional_edges(
            "prepare",
            route_after_prepare,
            {
                "rag": "rag",
                "web": "web",
                "generate": "generate",
            },
        )
        builder.add_conditional_edges(
            "rag",
            route_after_rag,
            {
                "web": "web",
                "generate": "generate",
            },
        )
        builder.add_edge("web", "generate")
        builder.add_edge("generate", END)

        self._graph = builder.compile()

    def run(
        self,
        request: CopyGenerateRequest,
        extra_context_blocks: list[str] | None = None,
        extra_sources: list[SourceItem] | None = None,
    ) -> tuple[CopyStructuredOutput, list[SourceItem]]:
        initial_context_blocks = [block for block in (extra_context_blocks or []) if block.strip()]
        initial_sources = list(extra_sources or [])

        state = self._graph.invoke(
            {
                "request": request,
                "query": "",
                "context_blocks": initial_context_blocks,
                "sources": initial_sources,
                "output": None,
            }
        )

        output = state.get("output")
        if output is None:
            output = self._generator(request, "")

        return output, list(state.get("sources", []))
