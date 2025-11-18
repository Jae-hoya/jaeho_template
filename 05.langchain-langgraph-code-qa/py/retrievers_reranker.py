from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_compressors import JinaRerank
from langchain.retrievers import ContextualCompressionRetriever

from dotenv import load_dotenv
load_dotenv()

def init_retriever(db_index="LANGCHAIN_DB_INDEX", fetch_k=30, top_n=8):

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    langgraph_db = FAISS.load_local(db_index, embeddings, allow_dangerous_deserialization=True)
    
    # retriever
    retriever = langgraph_db.as_retriever(search_kwargs={"k": fetch_k})

    # JinaReranker
    compressor = JinaRerank(model="jina-reranker-v2-base-multilingual", top_n=top_n)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=retriever
    )
    return compression_retriever
