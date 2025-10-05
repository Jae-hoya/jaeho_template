"""
Agentic RAG 시스템의 상태 정의
"""
from typing import TypedDict, Annotated, Sequence, Optional, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from pydantic import BaseModel


class AgentState(TypedDict):
    """
    에이전트 상태 정의
    
    Attributes:
        messages: 대화 메시지 시퀀스 (add_messages로 자동 병합)
        next: 다음에 실행할 노드를 지정하는 필드
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    next: Optional[str]  # 다음에 실행할 노드를 지정하는 필드 추가


# 멤버 정의
MEMBERS = ["Retriever", "Researcher", "Coder", "General LLM"]
OPTIONS_FOR_NEXT = ["FINISH"] + MEMBERS


class RouteResponse(BaseModel):
    """라우팅 응답 모델"""
    next: Literal[*OPTIONS_FOR_NEXT]
