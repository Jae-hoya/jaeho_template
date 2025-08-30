from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore, FastEmbedSparse, RetrievalMode
from qdrant_client import QdrantClient, models


from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.document_compressors import JinaRerank


client = QdrantClient(host="localhost", port=6333)

dense_embedding = OllamaEmbeddings(model="bge-m3")
sparse_embedding = FastEmbedSparse(model_name="Qdrant/bm25")

qdrant = QdrantVectorStore(
    client=client,
    collection_name="LangChain_LangGraph_QA",
    embedding = dense_embedding,
    sparse_embedding = sparse_embedding,
    retrieval_mode = RetrievalMode.HYBRID,
    vector_name= "dense",
    sparse_vector_name = "sparse",
)

def create_qdrant_retriever(fetch_k= 8):
    code_retriever = qdrant.as_retriever(search_kwargs={"k": fetch_k})
    return code_retriever

def create_compression_retriever(fetch_k=30, top_n=8):
    # retriever 생성
    code_retriever = qdrant.as_retriever(search_kwargs={"k": fetch_k})

    # JinaRerank 설정
    compressor = JinaRerank(model="jina-reranker-v2-base-multilingual", top_n=top_n)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=code_retriever
    )
    return compression_retriever
