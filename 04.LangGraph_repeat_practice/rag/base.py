from langchain_core.prompts import load_prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain import hub

from abc import ABC, abstractmethod
from operator import itemgetter


"""비교:             주요 차이점
특징	                    @staticmethod                                       	@abstractmethod
목적	                    독립적인 로직 실행	                                     자식 클래스에서 반드시 구현 강제
클래스/인스턴스 접근	     클래스/인스턴스 상태에 접근하지 않음	구현 강제용이라 본체에 동작 없음
상속 필요 여부	        상속 불필요	                            상속 필수
사용 위치                 클래스 내부의 보조적 기능	                    인터페이스 설계 및 강제화
구현 여부	                즉시 구현 가능	구현 없이 선언만 가능

self는 **클래스 메서드에서 해당 메서드가 호출된 객체(인스턴스)**를 나타내는 매개변수입니다.
Python에서 인스턴스 메서드를 정의할 때는 첫 번째 매개변수로 항상 self를 전달해야 합니다.
이는 메서드가 호출된 객체 자신에 접근할 수 있도록 하는 역할을 합니다.

ABC는 추상 클래스를 정의. 나중에 자식 클래스에서 구현된것을 받아온다(@abstractmethod)."""


class RetrievalChain(ABC):
    def __init__(self):
        self.source_uri = None
        self.k = 10

    @abstractmethod
    def load_documents(self, source_uris):
        """loader를 사용하여 문서를 로드합니다."""
        pass

    @abstractmethod
    def create_text_splitter(self):
        """text splitter를 생성합니다."""
        pass

    def split_documents(self, docs, text_splitter):
        """text splitter를 사용하여 문서를 분할합니다."""
        return text_splitter.split_documents(docs)

    def create_embedding(self):
        return OpenAIEmbeddings(model="text-embedding-3-small")

    def create_vectorstore(self, split_docs):
        return FAISS.from_documents(
            documents=split_docs, embedding=self.create_embedding()
        )

    def create_retriever(self, vectorstore):
        # MMR을 사용하여 검색을 수행하는 retriever를 생성합니다.
        dense_retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": self.k}
        )
        return dense_retriever

    def create_model(self):
        return ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

    def create_prompt(self):
        return hub.pull("teddynote/rag-prompt-chat-history")

    @staticmethod
    def format_docs(docs):
        return "\n".join(docs)

    def create_chain(self):
        docs = self.load_documents(self.source_uri)
        text_splitter = self.create_text_splitter()
        split_docs = self.split_documents(docs, text_splitter)
        self.vectorstore = self.create_vectorstore(split_docs)
        self.retriever = self.create_retriever(self.vectorstore)
        model = self.create_model()
        prompt = self.create_prompt()
        self.chain = (
            {
                "question": itemgetter("question"),
                "context": itemgetter("context"),
                "chat_history": itemgetter("chat_history"),
            }
            | prompt
            | model
            | StrOutputParser()
        )
        return self
