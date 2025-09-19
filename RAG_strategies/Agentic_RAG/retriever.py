from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient
from langchain_community.vectorstores.faiss import FAISS
from langchain.storage import LocalFileStore
from langchain.embeddings import CacheBackedEmbeddings

from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors import JinaRerank


class QdrantRetrieverFactory:
    """
    Qdrant VectorStore 기반 retriever 생성기.
    - collection_name은 각 메서드 호출 시 입력
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        dense_model: str = "bge-m3",
        sparse_model: str = "Qdrant/bm25",
    ):
        """
        QdrantRetrieverFactory 초기화
        
        Args:
            host: Qdrant 서버의 호스트 주소 (기본값: "localhost")
            port: Qdrant 서버의 포트 번호 (기본값: 6333)
            dense_model: Dense embedding을 위한 Ollama 모델명 (기본값: "bge-m3")
            sparse_model: Sparse embedding을 위한 모델명 (기본값: "Qdrant/bm25")
        """
        self.client = QdrantClient(host=host, port=port)
        self.dense_embedding = OllamaEmbeddings(model=dense_model)
        self.sparse_embedding = FastEmbedSparse(model_name=sparse_model)

    def _get_vectorstore(self, collection_name: str) -> QdrantVectorStore:
        """
        내부적으로 QdrantVectorStore 생성
        
        Args:
            collection_name: Qdrant 컬렉션 이름
            
        Returns:
            QdrantVectorStore: 하이브리드 검색 모드로 설정된 벡터스토어
        """
        return QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=self.dense_embedding,
            sparse_embedding=self.sparse_embedding,
            retrieval_mode=RetrievalMode.HYBRID,
            vector_name="dense",
            sparse_vector_name="sparse",
        )

    def retriever(self, collection_name: str, fetch_k: int = 5):
        """
        일반 retriever 생성
        
        Args:
            collection_name: 검색할 Qdrant 컬렉션 이름
            fetch_k: 검색할 문서 개수 (기본값: 5)
            
        Returns:
            BaseRetriever: 기본 검색 retriever
        """
        vs = self._get_vectorstore(collection_name)
        return vs.as_retriever(search_kwargs={"k": fetch_k})

    def compression_retriever(self, collection_name: str, fetch_k: int = 20, top_n: int = 5):
        """
        JinaRerank 기반 압축 retriever 생성
        
        Args:
            collection_name: 검색할 Qdrant 컬렉션 이름
            fetch_k: 초기 검색에서 가져올 문서 개수 (기본값: 20)
            top_n: 재순위화 후 최종 반환할 문서 개수 (기본값: 5)
            
        Returns:
            ContextualCompressionRetriever: 재순위화가 적용된 압축 retriever
        """
        vs = self._get_vectorstore(collection_name)
        base_retriever = vs.as_retriever(search_kwargs={"k": fetch_k})
        compressor = JinaRerank(model="jina-reranker-v2-base-multilingual", top_n=top_n)
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever,
        )


class FAISSRetrieverFactory:
    """
    FAISS VectorStore 기반 retriever 생성기.
    - index_path는 각 메서드 호출 시 입력
    """

    def __init__(
        self,
        model: str = "bge-m3",
        cache_dir: str = "./cache/",
    ):
        """
        FAISSRetrieverFactory 초기화
        
        Args:
            model: 임베딩을 위한 Ollama 모델명 (기본값: "bge-m3")
            cache_dir: 임베딩 캐시 디렉토리 (기본값: "./cache/")
        """
        self.embeddings = OllamaEmbeddings(model=model)
        
        # 로컬 파일 저장소 설정
        self.store = LocalFileStore(cache_dir)
        
        # 캐시를 지원하는 임베딩 생성
        self.cached_embedder = CacheBackedEmbeddings.from_bytes_store(
            underlying_embeddings=self.embeddings,
            document_embedding_cache=self.store,
            namespace=self.embeddings.model,
        )

    def _get_vectorstore(self, index_path: str) -> FAISS:
        """
        내부적으로 FAISS VectorStore 로드
        
        Args:
            index_path: FAISS 인덱스 파일 경로
            
        Returns:
            FAISS: 로드된 FAISS 벡터스토어
        """
        return FAISS.load_local(
            index_path, 
            self.cached_embedder, 
            allow_dangerous_deserialization=True
        )

    def retriever(self, index_path: str, fetch_k: int = 5):
        """
        일반 retriever 생성
        
        Args:
            index_path: FAISS 인덱스 파일 경로
            fetch_k: 검색할 문서 개수 (기본값: 5)
            
        Returns:
            BaseRetriever: 기본 검색 retriever
        """
        vs = self._get_vectorstore(index_path)
        return vs.as_retriever(search_kwargs={"k": fetch_k})

    def compression_retriever(self, index_path: str, fetch_k: int = 20, top_n: int = 5):
        """
        JinaRerank 기반 압축 retriever 생성
        
        Args:
            index_path: FAISS 인덱스 파일 경로
            fetch_k: 초기 검색에서 가져올 문서 개수 (기본값: 20)
            top_n: 재순위화 후 최종 반환할 문서 개수 (기본값: 5)
            
        Returns:
            ContextualCompressionRetriever: 재순위화가 적용된 압축 retriever
        """
        vs = self._get_vectorstore(index_path)
        base_retriever = vs.as_retriever(search_kwargs={"k": fetch_k})
        compressor = JinaRerank(model="jina-reranker-v2-base-multilingual", top_n=top_n)
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever,
        )




