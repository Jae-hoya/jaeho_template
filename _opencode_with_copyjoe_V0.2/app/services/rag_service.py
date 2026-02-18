from app.flows.rag_graph import RagWorkflowGraph
from app.integrations.milvus_client import MilvusClient
from app.schemas.common import SourceItem
from app.schemas.rag import RagChunk, RagIndexResponse
from app.services.document_store import DocumentStore


class RagService:
    def __init__(self, vector_client: MilvusClient, document_store: DocumentStore) -> None:
        self._vector_client = vector_client
        self._graph = RagWorkflowGraph(vector_client=vector_client, document_store=document_store)

    @property
    def graph(self) -> RagWorkflowGraph:
        return self._graph

    @property
    def backend(self) -> str:
        return self._vector_client.backend

    def index_documents(self, document_ids: list[str], chunk_size: int, chunk_overlap: int) -> RagIndexResponse:
        return self._graph.run_index(
            document_ids=document_ids,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def search(self, query: str, top_k: int) -> list[RagChunk]:
        return self._graph.run_search(query=query, top_k=top_k)

    def build_context(self, query: str, top_k: int) -> tuple[str, list[SourceItem]]:
        return self._graph.run_build_context(query=query, top_k=top_k)
