from functools import lru_cache

from app.core.config import Settings, get_settings
from app.integrations.docling_client import DoclingClient
from app.integrations.embeddings_factory import create_embeddings
from app.integrations.milvus_client import MilvusClient
from app.services.copy_lite_service import CopyLiteService
from app.services.copy_service import CopyService
from app.services.document_store import DocumentStore
from app.services.export_service import ExportService
from app.services.file_service import FileService
from app.services.history_service import HistoryService
from app.services.rag_service import RagService
from app.services.web_search_service import WebSearchService


@lru_cache
def settings() -> Settings:
    return get_settings()


@lru_cache
def document_store() -> DocumentStore:
    return DocumentStore()


@lru_cache
def docling_client() -> DoclingClient:
    return DoclingClient()


@lru_cache
def file_service() -> FileService:
    return FileService(settings=settings(), docling_client=docling_client(), document_store=document_store())


@lru_cache
def vector_client() -> MilvusClient:
    return MilvusClient(settings=settings(), embeddings=create_embeddings(settings()))


@lru_cache
def rag_service() -> RagService:
    return RagService(vector_client=vector_client(), document_store=document_store())


@lru_cache
def web_search_service() -> WebSearchService:
    return WebSearchService(settings=settings())


@lru_cache
def copy_service() -> CopyService:
    return CopyService(
        settings=settings(),
        rag_service=rag_service(),
        web_search_service=web_search_service(),
    )


@lru_cache
def copy_lite_service() -> CopyLiteService:
    return CopyLiteService(settings=settings(), copy_service=copy_service())


@lru_cache
def export_service() -> ExportService:
    return ExportService()


@lru_cache
def history_service() -> HistoryService:
    return HistoryService()
