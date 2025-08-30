# 상태값 정의

from typing_extensions import TypedDict, Annotated
from langchain_core.documents import Document
from langgraph.prebuilt.chat_agent_executor import AgentState


# class GraphState(TypedDict):
#     question: Annotated[str, "User question"]
#     generation: Annotated[str, "LLM generated answer"]
#     documents: Annotated[list[Document], "List of documents"]

class GraphState(AgentState):
    """
    그래프의 상태를 나타내는 데이터 모델

    Attributes:
        question: 질문
        generation: LLM 생성된 답변
        documents: 도큐먼트 리스트
    """
    question: Annotated[str, "User question"]
    generation: Annotated[str, "LLM generated answer"]
    documents: Annotated[list[Document], "List of documents"]