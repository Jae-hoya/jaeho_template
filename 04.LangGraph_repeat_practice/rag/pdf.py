from rag.base import RetrievalChain
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Annotated

"""
PDFRetrievalChain 클래스가 RetrievalChain이라는 부모 클래스를 상속받는 구조로 작성되어 있다.
이 의미는 PDFRetrievalChain이 RetrievalChain의 모든 기능을 사용할 수 있으며, 필요에 따라 추가적인 메서드나 속성을 정의하거나,
기존 메서드를 재정의(overriding)할 수 있다는 것다.
"""


class PDFRetrievalChain(RetrievalChain):
    def __init__(self, source_uri: Annotated[str, "Source URI"]):
        self.source_uri = source_uri
        self.k = 10

    def load_documents(self, source_uris: List[str]):
        docs = []
        for source_uri in source_uris:
            loader = PDFPlumberLoader(source_uri)
            docs.extend(loader.load())
        return docs

    def create_text_splitter(self):
        return RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
