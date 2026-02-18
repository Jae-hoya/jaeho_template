import math
import uuid
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
                from langchain_milvus import Milvus

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

    def similarity_search_with_scores(
        self,
        query: str,
        top_k: int,
        document_ids: list[str] | None = None,
    ) -> list[ScoredDocument]:
        allowed_ids = set(document_ids or [])
        filter_expression = _build_milvus_document_filter_expression(allowed_ids)

        if self._milvus_vector_store is not None:
            try:
                filter_applied = False
                if filter_expression:
                    try:
                        rows = self._milvus_vector_store.similarity_search_with_score(
                            query,
                            k=top_k,
                            expr=filter_expression,
                        )
                        filter_applied = True
                    except TypeError:
                        search_k = max(top_k * 6, top_k)
                        rows = self._milvus_vector_store.similarity_search_with_score(query, k=search_k)
                else:
                    rows = self._milvus_vector_store.similarity_search_with_score(query, k=top_k)

                scored_rows = [ScoredDocument(document=row[0], score=float(row[1])) for row in rows]
                if allowed_ids and not filter_applied:
                    scored_rows = [
                        row
                        for row in scored_rows
                        if str(row.document.metadata.get("document_id", "")) in allowed_ids
                    ]
                return scored_rows[:top_k]
            except Exception:
                self._milvus_vector_store = None
                self._backend = "memory"

        if not self._memory_records:
            return []

        query_vector = self._safe_embed_query(query)
        scored: list[ScoredDocument] = []

        for _, vector, document in self._memory_records:
            if allowed_ids and str(document.metadata.get("document_id", "")) not in allowed_ids:
                continue
            score = _cosine_similarity(query_vector, vector)
            scored.append(ScoredDocument(document=document, score=score))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def clear(self) -> int:
        cleared = len(self._memory_records)
        self._memory_records.clear()

        if self._milvus_vector_store is not None:
            try:
                collection = getattr(self._milvus_vector_store, "col", None)
                milvus_count = int(getattr(collection, "num_entities", 0)) if collection is not None else 0
                if collection is not None:
                    collection.drop()

                from langchain_milvus import Milvus

                self._milvus_vector_store = Milvus(
                    embedding_function=self._embeddings,
                    collection_name=self._settings.milvus_collection,
                    connection_args={"uri": self._settings.milvus_uri},
                    auto_id=True,
                )
                self._backend = "milvus"
                return max(cleared, milvus_count)
            except Exception:
                self._milvus_vector_store = None
                self._backend = "memory"

        return cleared

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


def _build_milvus_document_filter_expression(document_ids: set[str]) -> str | None:
    if not document_ids:
        return None

    escaped_ids = [doc_id.replace("\\", "\\\\").replace('"', '\\"') for doc_id in document_ids]
    quoted_ids = ", ".join(f'"{doc_id}"' for doc_id in escaped_ids)
    return f"document_id in [{quoted_ids}]"
