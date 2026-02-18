from abc import ABC, abstractmethod
from typing import Callable, Literal, Protocol

from app.flows.copy_generation.chains import build_web_search_query, merge_context_blocks
from app.flows.copy_generation.states import CopyGraphState
from app.schemas.common import SourceItem
from app.schemas.copy import CopyGenerateRequest, CopyStructuredOutput
from app.schemas.web import WebSearchResult

CopyGenerator = Callable[[CopyGenerateRequest, str], CopyStructuredOutput]
QueryBuilder = Callable[[CopyGenerateRequest], str]


class RagContextService(Protocol):
    def build_context(
        self,
        query: str,
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> tuple[str, list[SourceItem]]:
        ...


class WebSearchService(Protocol):
    def search(self, query: str, max_results: int, strict: bool = True) -> list[WebSearchResult]:
        ...


class BaseNode(ABC):
    @abstractmethod
    def execute(self, state: CopyGraphState) -> dict[str, object] | str:
        raise NotImplementedError

    def __call__(self, state: CopyGraphState) -> dict[str, object] | str:
        return self.execute(state)


class PrepareNode(BaseNode):
    def __init__(self, query_builder: QueryBuilder) -> None:
        self._query_builder = query_builder

    def execute(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]
        return {
            "query": self._query_builder(request),
            "context_blocks": list(state.get("context_blocks", [])),
            "sources": list(state.get("sources", [])),
        }


class CollectRagNode(BaseNode):
    def __init__(self, rag_service: RagContextService) -> None:
        self._rag_service = rag_service

    def execute(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]
        context_blocks = list(state.get("context_blocks", []))
        sources = list(state.get("sources", []))

        try:
            rag_context, rag_sources = self._rag_service.build_context(
                query=state["query"],
                top_k=request.top_k,
                document_ids=request.rag_document_ids,
            )
        except TypeError:
            rag_context, rag_sources = self._rag_service.build_context(
                query=state["query"],
                top_k=request.top_k,
            )
        context_blocks = merge_context_blocks(context_blocks, rag_context)
        if rag_context:
            sources.extend(rag_sources)

        return {
            "context_blocks": context_blocks,
            "sources": sources,
        }


class CollectWebNode(BaseNode):
    def __init__(self, web_search_service: WebSearchService, query_builder: QueryBuilder = build_web_search_query) -> None:
        self._web_search_service = web_search_service
        self._query_builder = query_builder

    def execute(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]
        context_blocks = list(state.get("context_blocks", []))
        sources = list(state.get("sources", []))

        query = self._query_builder(request)
        web_results = self._web_search_service.search(query=query, max_results=request.top_k, strict=False)
        web_context = "\n\n".join(item.content for item in web_results if item.content)
        context_blocks = merge_context_blocks(context_blocks, web_context)

        if web_results:
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


class GenerateNode(BaseNode):
    def __init__(self, generator: CopyGenerator) -> None:
        self._generator = generator

    def execute(self, state: CopyGraphState) -> dict[str, object]:
        request = state["request"]
        context_text = "\n\n".join(state.get("context_blocks", []))
        return {
            "output": self._generator(request, context_text),
        }


def route_after_prepare(state: CopyGraphState) -> Literal["rag", "web", "generate"]:
    request = state["request"]
    if request.use_rag:
        return "rag"
    if request.web_search_mode:
        return "web"
    return "generate"


def route_after_rag(state: CopyGraphState) -> Literal["web", "generate"]:
    if state["request"].web_search_mode:
        return "web"
    return "generate"
