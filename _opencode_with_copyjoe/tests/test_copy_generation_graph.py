from app.flows.copy_generation_graph import CopyGenerationGraph
from app.schemas.common import SourceItem
from app.schemas.copy import CopyGenerateRequest, CopyStructuredOutput, Objective, Style
from app.schemas.web import WebSearchResult


class DummyRagService:
    def build_context(self, query: str, top_k: int) -> tuple[str, list[SourceItem]]:
        _ = (query, top_k)
        return (
            "rag context block",
            [SourceItem(source_type="rag", title="doc", snippet="rag snippet")],
        )


class DummyWebSearchService:
    def search(self, query: str, max_results: int, strict: bool = True) -> list[WebSearchResult]:
        _ = (query, max_results, strict)
        return [
            WebSearchResult(
                title="web title",
                url="https://example.com",
                content="web context block",
            )
        ]


def test_graph_collects_rag_and_web_context() -> None:
    captured: dict[str, str] = {}

    def generator(_: CopyGenerateRequest, context: str) -> CopyStructuredOutput:
        captured["context"] = context
        return CopyStructuredOutput(
            head="h",
            body="b",
            cta="c",
            slogan="s",
            sns="n",
            description="d",
            storyboard_outline=["1", "2", "3", "4"],
            rationale="ok",
        )

    graph = CopyGenerationGraph(
        rag_service=DummyRagService(),
        web_search_service=DummyWebSearchService(),
        generator=generator,
    )

    request = CopyGenerateRequest(
        product_name="Copyjoe",
        target_audience="마케터",
        pain_point="카피가 느리다",
        differentiator="근거 기반",
        tone="신뢰형",
        objective=Objective.click,
        styles=[Style.head, Style.body, Style.cta],
        channel="상세페이지",
        language="ko",
        web_search_mode=True,
        use_rag=True,
        top_k=3,
    )

    output, sources = graph.run(request)
    assert output.head == "h"
    assert "rag context block" in captured["context"]
    assert "web context block" in captured["context"]
    assert len(sources) == 2
