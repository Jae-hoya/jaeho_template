"""
Agentic RAG 시스템의 노드 함수들
각 에이전트의 노드 실행 함수들을 정의합니다.
"""
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import MessagesState

from states import AgentState


def retriever_node(state: AgentState, retriever_agent) -> AgentState:
    """
    Retriever 노드 함수
    
    Args:
        state: 현재 상태
        retriever_agent: Retriever 에이전트
        
    Returns:
        AgentState: 업데이트된 상태
    """
    # invoke 시 분리
    result = retriever_agent.invoke(
        {"messages": state["messages"]}, 
    )

    last_ai = [m for m in result["messages"] if m.type == "ai"][-1]

    return {
        "messages": [AIMessage(content=last_ai.content, name="retriever")],
    }


def research_node(state: MessagesState, research_agent) -> MessagesState:
    """
    Research 노드 함수
    
    Args:
        state: 현재 상태
        research_agent: Research 에이전트
        
    Returns:
        MessagesState: 업데이트된 상태
    """
    result = research_agent.invoke(
        {"messages": state["messages"]},
    )
    last_message = HumanMessage(
        content=result["messages"][-1].content, name="research"
    )
    return {
        "messages": [last_message],
    }


def coder_node(state: MessagesState, coder_agent) -> MessagesState:
    """
    Coder 노드 함수
    
    Args:
        state: 현재 상태
        coder_agent: Coder 에이전트
        
    Returns:
        MessagesState: 업데이트된 상태
    """
    result = coder_agent.invoke(state)

    # 마지막 메시지를 HumanMessage 로 변환
    last_message = HumanMessage(
        content=result["messages"][-1].content, name="coder",
    )
    
    return {
        "messages": [last_message],
    }


def general_node(state: MessagesState, general_agent) -> MessagesState:
    """
    General 노드 함수
    
    Args:
        state: 현재 상태
        general_agent: General 에이전트
        
    Returns:
        MessagesState: 업데이트된 상태
    """
    # react_agent 사용
    result = general_agent.invoke(
        {"messages": state["messages"]},
    )
    
    # AI 메시지 중에서 실제 답변을 찾기
    ai_messages = [m for m in result["messages"] if m.type == "ai"]
    if ai_messages:
        # 마지막 AI 메시지의 내용 사용
        answer_content = ai_messages[-1].content
    else:
        # AI 메시지가 없으면 마지막 메시지 사용
        answer_content = result["messages"][-1].content
    
    # AIMessage로 변환 (일관성을 위해)
    last_message = AIMessage(
        content=answer_content, name="general",
    )
    
    return {
        "messages": [last_message],
    }