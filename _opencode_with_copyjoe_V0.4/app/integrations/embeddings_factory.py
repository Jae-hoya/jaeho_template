import hashlib
import math
import re

from langchain_core.embeddings import Embeddings

from app.core.config import Settings


class HashEmbeddings(Embeddings):
    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _embed(self, text: str) -> list[float]:
        tokens = re.findall(r"[\w\-]+", text.lower())
        vector = [0.0] * self.dim

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[idx] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def create_embeddings(settings: Settings) -> Embeddings:
    provider = settings.llm_provider.lower().strip()

    if provider == "openai" and settings.openai_api_key:
        try:
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(
                model=settings.openai_embedding_model,
                api_key=settings.openai_api_key,
            )
        except Exception:
            return HashEmbeddings()

    if provider == "ollama":
        try:
            from langchain_ollama import OllamaEmbeddings

            return OllamaEmbeddings(
                model=settings.ollama_embedding_model,
                base_url=settings.ollama_base_url,
            )
        except Exception:
            return HashEmbeddings()

    return HashEmbeddings()
