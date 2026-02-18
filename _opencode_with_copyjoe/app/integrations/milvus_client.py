import math
import uuid
import importlib
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from app.core.config import Settings
from app.integrations.embeddings_factory import HashEmbeddings


@dataclass
class ScoredDocument:
    document: Document
    score: float


class MilvusClient:
    def __init__(self, settings: Settings, embeddings: Embeddings) -> None:
        self._settings = settings
        self._embeddings = embeddings
        self._fallback_embeddings = HashEmbeddings()
        self._memory_records: list[tuple[str, list[float], Document]] = []
        self._backend = "memory"
        self._milvus_vector_store = None

        if settings.milvus_uri:
            try:
                milvus_module = importlib.import_module("langchain_milvus")
                Milvus = getattr(milvus_module, "Milvus")

                self._milvus_vector_store = Milvus(
                    embedding_function=embeddings,
                    collection_name=settings.milvus_collection,
                    connection_args={"uri": settings.milvus_uri},
                    auto_id=True,
                )
                self._backend = "milvus"
            except Exception:
                self._milvus_vector_store = None
                self._backend = "memory"

    @property
    def backend(self) -> str:
        return self._backend

    def add_documents(self, documents: list[Document]) -> list[str]:
        if not documents:
            return []

        if self._milvus_vector_store is not None:
            try:
                return self._milvus_vector_store.add_documents(documents)
            except Exception:
                self._milvus_vector_store = None
                self._backend = "memory"

        vectors = self._safe_embed_documents([doc.page_content for doc in documents])
        ids: list[str] = []
        for vector, document in zip(vectors, documents):
            doc_id = str(uuid.uuid4())
            self._memory_records.append((doc_id, vector, document))
            ids.append(doc_id)
        return ids

    def similarity_search_with_scores(self, query: str, top_k: int) -> list[ScoredDocument]:
        if self._milvus_vector_store is not None:
            try:
                rows = self._milvus_vector_store.similarity_search_with_score(query, k=top_k)
                return [ScoredDocument(document=row[0], score=float(row[1])) for row in rows]
            except Exception:
                self._milvus_vector_store = None
                self._backend = "memory"

        if not self._memory_records:
            return []

        query_vector = self._safe_embed_query(query)
        scored: list[ScoredDocument] = []

        for _, vector, document in self._memory_records:
            score = _cosine_similarity(query_vector, vector)
            scored.append(ScoredDocument(document=document, score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def _safe_embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            return self._embeddings.embed_documents(texts)
        except Exception:
            return self._fallback_embeddings.embed_documents(texts)

    def _safe_embed_query(self, text: str) -> list[float]:
        try:
            return self._embeddings.embed_query(text)
        except Exception:
            return self._fallback_embeddings.embed_query(text)


def _cosine_similarity(first: list[float], second: list[float]) -> float:
    if not first or not second:
        return 0.0
    numerator = sum(a * b for a, b in zip(first, second))
    first_norm = math.sqrt(sum(value * value for value in first))
    second_norm = math.sqrt(sum(value * value for value in second))
    denominator = first_norm * second_norm
    if denominator == 0:
        return 0.0
    return numerator / denominator
