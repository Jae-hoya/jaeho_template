from app.flows.rag_workflow import RagWorkflowGraph
from app.integrations.milvus_client import MilvusClient
from app.schemas.common import SourceItem
from app.schemas.rag import RagChunk, RagIndexResponse, RagResetResponse
from app.services.document_store import DocumentStore


class RagService:
    def __init__(self, vector_client: MilvusClient, document_store: DocumentStore) -> None:
        self._vector_client = vector_client
        self._document_store = document_store
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

    def search(self, query: str, top_k: int, document_ids: list[str] | None = None) -> list[RagChunk]:
        return self._graph.run_search(query=query, top_k=top_k, document_ids=document_ids)

    def build_context(
        self,
        query: str,
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> tuple[str, list[SourceItem]]:
        return self._graph.run_build_context(query=query, top_k=top_k, document_ids=document_ids)

    def reset_index(self) -> RagResetResponse:
        cleared_documents = self._document_store.clear(remove_files=True)
        cleared_vectors = self._vector_client.clear()
        return RagResetResponse(
            backend=self.backend,
            cleared_documents=cleared_documents,
            cleared_vectors=cleared_vectors,
        )
