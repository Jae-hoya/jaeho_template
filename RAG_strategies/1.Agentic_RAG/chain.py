"""
Agentic RAG 시스템의 체인 및 그래프 생성
그래프 생성, Supervisor 에이전트, 그리고 전체 워크플로우를 정의합니다.
"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver

from states import AgentState, RouteResponse, MEMBERS, OPTIONS_FOR_NEXT
from agents import (
    create_retriever_agent, 
    create_research_agent, 
    create_coder_agent, 
    create_general_agent
)
from nodes import (
    retriever_node,
    research_node,
    coder_node,
    general_node
)


def create_supervisor_agent(llm=None):
    """
    Supervisor 에이전트 생성
    
    Args:
        llm: 언어 모델 (기본값: gpt-4.1-mini)
        
    Returns:
        supervisor_agent: Supervisor 에이전트 함수
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    
    # 시스템 프롬프트 정의: 작업자 간의 대화를 관리하는 감독자 역할
    system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers:  {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
        " If a worker has already provided a response, consider if FINISH is appropriate."
        " task and respond with their results and status."
        " You must select at least one worker before considering FINISH."
        " Do not select FINISH immediately - always try a worker first."
        " Do not select the same worker({members}) more than once times in a row."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next?"
                "Or should we FINISH? Select one of: {options}"
                " IMPORTANT: Do not select the same worker({members}) more than once times in a row."
                " IMPORTANT: You must select at least one worker({members}) before considering FINISH."
                " If a worker has already provided a response, consider FINISH."
            )
        ]
    ).partial(options=str(OPTIONS_FOR_NEXT), members=", ".join(MEMBERS))

    def supervisor_agent(state):
        supervisor_chain = prompt | llm.with_structured_output(RouteResponse)
        return supervisor_chain.invoke(state)
    
    return supervisor_agent


def create_agentic_rag_graph(retriever, llm=None, use_memory=True):
    """
    Agentic RAG 그래프 생성
    
    Args:
        retriever: 검색기 객체
        llm: 언어 모델 (기본값: gpt-4.1-mini)
        use_memory: 메모리 사용 여부 (기본값: True)
        
    Returns:
        graph: 컴파일된 그래프
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    
    # 에이전트들 생성
    retriever_agent = create_retriever_agent(retriever, llm)
    research_agent = create_research_agent(llm)
    coder_agent = create_coder_agent(llm)
    general_agent = create_general_agent(llm)
    supervisor_agent = create_supervisor_agent(llm)
    
    # 그래프 생성
    workflow = StateGraph(AgentState)

    # 그래프에 노드 추가
    workflow.add_node("Retriever", lambda state: retriever_node(state, retriever_agent))
    workflow.add_node("Researcher", lambda state: research_node(state, research_agent))
    workflow.add_node("Coder", lambda state: coder_node(state, coder_agent))
    workflow.add_node("General LLM", lambda state: general_node(state, general_agent))
    workflow.add_node("Supervisor", supervisor_agent)

    # 멤버 노드 > Supervisor 노드로 엣지 추가
    for member in MEMBERS:
        workflow.add_edge(member, "Supervisor")

    # 조건부 엣지 추가
    conditional_map = {k: k for k in MEMBERS}
    conditional_map["FINISH"] = END

    def get_next(state):
        return state["next"]

    # Supervisor 노드에서 조건부 엣지 추가
    workflow.add_conditional_edges("Supervisor", get_next, conditional_map)

    # 시작점
    workflow.add_edge(START, "Supervisor")

    # 그래프 컴파일
    if use_memory:
        graph = workflow.compile(checkpointer=MemorySaver())
    else:
        graph = workflow.compile()
    
    return graph


def create_agentic_rag_graph_no_memory(retriever, llm=None):
    """
    메모리 없는 Agentic RAG 그래프 생성 (각 질문이 완전히 독립적)
    
    Args:
        retriever: 검색기 객체
        llm: 언어 모델 (기본값: gpt-4.1-mini)
        
    Returns:
        graph: 컴파일된 그래프 (메모리 없음)
    """
    return create_agentic_rag_graph(retriever, llm, use_memory=False)
