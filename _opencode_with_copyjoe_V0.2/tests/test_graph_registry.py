import asyncio

from app.core.config import Settings
from app.flows.copy_generation_graph import CopyGenerationGraph
from app.flows.copy_lite_generation_graph import CopyLiteGenerationGraph
from app.flows.export_graph import ExportWorkflowGraph
from app.flows.file_upload_graph import FileUploadGraph
from app.flows.graph_registry import build_graph_registry
from app.flows.history_graph import HistoryWorkflowGraph
from app.flows.meta_graph import MetaCopyFormGuideGraph
from app.flows.rag_graph import RagWorkflowGraph
from app.flows.web_graph import WebWorkflowGraph
from app.schemas.copy import CopyGenerateRequest, CopyLiteRequest, Objective, Style


def test_graph_registry_builds_all_domain_graphs() -> None:
    registry = build_graph_registry(Settings(force_mock_mode=True))

    assert isinstance(registry.copy, CopyGenerationGraph)
    assert isinstance(registry.copy_lite, CopyLiteGenerationGraph)
    assert isinstance(registry.rag, RagWorkflowGraph)
    assert isinstance(registry.web, WebWorkflowGraph)
    assert isinstance(registry.file_upload, FileUploadGraph)
    assert isinstance(registry.history, HistoryWorkflowGraph)
    assert isinstance(registry.export, ExportWorkflowGraph)
    assert isinstance(registry.meta, MetaCopyFormGuideGraph)


def test_graph_registry_graphs_are_invokable_for_tests() -> None:
    registry = build_graph_registry(Settings(force_mock_mode=True))

    request = CopyGenerateRequest(
        product_name="Copyjoe",
        target_audience="퍼포먼스 마케터",
        pain_point="카피 작성이 느리다",
        differentiator="근거 기반 생성",
        tone="신뢰형",
        objective=Objective.click,
        styles=[Style.head, Style.body, Style.cta],
        channel="상세페이지",
        language="ko",
        web_search_mode=False,
        use_rag=False,
        top_k=5,
    )

    output, sources = registry.copy.run(request)
    assert output.head
    assert sources == []

    payload = CopyLiteRequest(
        prompt="광고 클릭률이 떨어져서 카피 개선이 필요해",
        styles=[Style.head, Style.cta],
        web_search_mode=False,
        use_rag=False,
        top_k=5,
    )
    lite_response = asyncio.run(registry.copy_lite.run(payload))
    assert lite_response.result.head
    assert lite_response.normalized_request.objective == Objective.click
