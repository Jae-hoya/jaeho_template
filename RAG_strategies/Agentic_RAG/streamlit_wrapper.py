from dotenv import load_dotenv
load_dotenv()

# Agentic RAG 시스템 모듈들 import
from retriever import QdrantRetrieverFactory, FAISSRetrieverFactory
from graph import create_agentic_rag_graph
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.errors import GraphRecursionError

import streamlit as st

# QdrantRetrieverFactory 인스턴스 생성
qs = QdrantRetrieverFactory()
faiss = FAISSRetrieverFactory()

DB_INDEX = "LANGCHAIN_FAISS_DB_INDEX/index.faiss"
# ./jaeho_template/RAG_strategies/Agentic_RAG/LANGCHAIN_FAISS_DB_INDEX
def create_graph():
    """
    Agentic RAG 그래프 생성
    
    Returns:
        graph: 컴파일된 Agentic RAG 그래프
    """
    # Retriever 생성 (FAISS 인덱스 사용)
    retriever = faiss.retriever(
        index_path="/RAG_strategies/Agentic_RAG/LANGCHAIN_FAISS_DB_INDEX",
        fetch_k=3
    )
    
    # Agentic RAG 그래프 생성 (메모리 포함)
    graph = create_agentic_rag_graph(retriever, use_memory=True)
    
    return graph

# def create_graph():
#     """
#     Agentic RAG 그래프 생성
    
#     Returns:
#         graph: 컴파일된 Agentic RAG 그래프
#     """
#     # Retriever 생성 (SPRI AI Brief 컬렉션 사용)
#     retriever = qs.retriever(
#         collection_name="RAG_Example(RAG_strategies)", 
#         fetch_k=3
#     )
    
#     # Agentic RAG 그래프 생성 (메모리 포함)
#     graph = create_agentic_rag_graph(retriever, use_memory=True)
    
#     return graph

def stream_graph(app, query, streamlit_container, thread_id, chat_history=None):
    """
    Agentic RAG 그래프를 스트리밍으로 실행
    
    Args:
        app: Agentic RAG 그래프
        query: 사용자 질문
        streamlit_container: Streamlit 컨테이너
        thread_id: 스레드 ID
        chat_history: 대화 기록 (선택사항)
        
    Returns:
        dict: 그래프 실행 결과
    """
    config = RunnableConfig(recursion_limit=30, configurable={"thread_id": thread_id})
    
    # chat_history가 None이면 빈 리스트로 초기화
    if chat_history is None:
        chat_history = []
    
    # 현재 질문을 HumanMessage로 변환
    current_message = HumanMessage(content=query)
    
    # 입력 메시지 구성: 이전 대화 기록 + 현재 질문
    messages = chat_history + [current_message]
    
    inputs = {
        "messages": messages
    }
    
    # 디버깅 로그 제거됨
    
    # 노드별 상태 메시지
    node_actions = {
        "Supervisor": "🤖 에이전트를 선택하는 중입니다...",
        "Retriever": "📚 SPRI 문서를 검색하는 중입니다...",
        "Researcher": "🔍 웹에서 최신 정보를 찾는 중입니다...",
        "Coder": "📊 차트를 생성하는 중입니다...",
        "General LLM": "💭 답변을 생성하는 중입니다...",
    }
    
    # 사용된 도구들을 추적하기 위한 리스트
    used_tools = []
    
    try:
        with streamlit_container.status(
            "🤔 생각하는 중입니다...", expanded=True
        ) as status:
            final_output = None
            for output in app.stream(inputs, config=config):
                final_output = output  # 마지막 출력 저장
                for node_name, node_output in output.items():
                    if node_name in node_actions:
                        # 사용된 도구 추적 (Supervisor 제외)
                        if node_name != "Supervisor" and node_name not in used_tools:
                            used_tools.append(node_name)
                        
                        st.write(node_actions[node_name])
                        
                        # 특정 노드에서 추가 정보 표시
                        if node_name == "Retriever":
                            st.write("📄 관련 문서를 찾았습니다.")
                        elif node_name == "Researcher":
                            st.write("🌐 웹 검색 결과를 분석하고 있습니다.")
                        elif node_name == "Coder":
                            st.write("🐍 Python 코드를 실행하고 있습니다.")
                        elif node_name == "General LLM":
                            st.write("✨ 최종 답변을 정리하고 있습니다.")
            
            # 사용된 도구들 표시
            if used_tools:
                tool_names = {
                    "Retriever": "📚 SPRI 문서 검색",
                    "Researcher": "🔍 웹 검색 (TavilySearch)",
                    "Coder": "📊 Python 차트 생성",
                    "General LLM": "💭 일반 대화"
                }
                st.write("---")
                st.write("**🛠️ 사용된 도구들:**")
                for tool in used_tools:
                    st.write(f"• {tool_names.get(tool, tool)}")
            
            # 모든 스트리밍이 완료된 후에만 "답변 완료" 표시
            status.update(label="✅ 답변 완료!", state="complete", expanded=False)
                
    except GraphRecursionError as e:
        st.error(f"재귀 한계에 도달했습니다: {e}")
        return {"answer": "죄송합니다. 질문이 너무 복잡해서 처리할 수 없습니다."}
    
    # 최종 답변 추출
    try:
        # 스트리밍 중에 생성된 최종 출력에서 답변 추출
        if final_output:
            # 마지막 출력에서 메시지 추출
            for node_name, node_output in final_output.items():
                if hasattr(node_output, 'get') and 'messages' in node_output:
                    messages = node_output['messages']
                    # AI 메시지 찾기
                    ai_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == 'ai']
                    if ai_messages:
                        answer = ai_messages[-1].content
                        return {"answer": answer, "used_tools": used_tools}
        
        # 위 방법이 실패하면 그래프 상태에서 추출
        final_state = app.get_state(config={"configurable": {"thread_id": thread_id}})
        messages = final_state.values.get("messages", [])
        
        # 마지막 AI 메시지 찾기
        ai_messages = [msg for msg in messages if hasattr(msg, 'type') and msg.type == 'ai']
        if ai_messages:
            answer = ai_messages[-1].content
        else:
            # AI 메시지가 없으면 마지막 메시지 사용
            answer = messages[-1].content if messages else "답변을 생성할 수 없습니다."
            
        return {"answer": answer, "used_tools": used_tools}
        
    except Exception as e:
        st.error(f"답변 추출 중 오류가 발생했습니다: {e}")
        return {"answer": "죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다.", "used_tools": used_tools}
