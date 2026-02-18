from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.flows.copy_generation_graph import CopyGenerationGraph
from app.flows.copy_lite_generation_graph import CopyLiteGenerationGraph
from app.flows.export_graph import ExportWorkflowGraph
from app.flows.file_upload_graph import FileUploadGraph
from app.flows.history_graph import HistoryWorkflowGraph
from app.flows.meta_graph import MetaCopyFormGuideGraph
from app.flows.rag_graph import RagWorkflowGraph
from app.flows.web_graph import WebWorkflowGraph
from app.integrations.docling_client import DoclingClient
from app.integrations.embeddings_factory import create_embeddings
from app.integrations.milvus_client import MilvusClient
from app.services.copy_lite_service import CopyLiteService
from app.services.copy_service import CopyService
from app.services.document_store import DocumentStore
from app.services.export_service import ExportService
from app.services.file_service import FileService
from app.services.history_service import HistoryService
from app.services.meta_service import MetaService
from app.services.rag_service import RagService
from app.services.web_search_service import WebSearchService


@dataclass(frozen=True)
class GraphRegistry:
    copy: CopyGenerationGraph
    copy_lite: CopyLiteGenerationGraph
    rag: RagWorkflowGraph
    web: WebWorkflowGraph
    file_upload: FileUploadGraph
    history: HistoryWorkflowGraph
    export: ExportWorkflowGraph
    meta: MetaCopyFormGuideGraph


def build_graph_registry(settings: Settings | None = None) -> GraphRegistry:
    cfg = settings or get_settings()

    store = DocumentStore()
    docling = DoclingClient()
    vector_client = MilvusClient(settings=cfg, embeddings=create_embeddings(cfg))

    rag_service = RagService(vector_client=vector_client, document_store=store)
    web_search_service = WebSearchService(settings=cfg)

    copy_service = CopyService(
        settings=cfg,
        rag_service=rag_service,
        web_search_service=web_search_service,
    )
    copy_lite_service = CopyLiteService(
        settings=cfg,
        copy_service=copy_service,
        web_search_service=web_search_service,
    )

    file_service = FileService(
        settings=cfg,
        docling_client=docling,
        document_store=store,
    )
    history_service = HistoryService()
    export_service = ExportService()
    meta_service = MetaService()

    return GraphRegistry(
        copy=copy_service.graph,
        copy_lite=copy_lite_service.graph,
        rag=rag_service.graph,
        web=web_search_service.graph,
        file_upload=file_service.graph,
        history=history_service.graph,
        export=export_service.graph,
        meta=meta_service.graph,
    )
