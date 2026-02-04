"""Streamlit Web UI for LangGraph RAG"""

import os
import sys
import time
from datetime import datetime

import streamlit as st

from langgraph_rag import LangGraphRAG, RAGState
from search_app.config import Config

# Page config
st.set_page_config(
    page_title="LangGraph RAG - 대출 상품 검색",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #1976d2;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .route-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: bold;
        margin-left: 0.5rem;
    }
    .route-search {
        background-color: #4caf50;
        color: white;
    }
    .route-direct {
        background-color: #ff9800;
        color: white;
    }
    .search-result {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff9800;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

STREAMING_DELAY_SEC = 0.01
STREAMING_CURSOR = "▌"


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag" not in st.session_state:
    st.session_state.rag = None

if "debug_mode" not in st.session_state:
    st.session_state.debug_mode = False

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def initialize_rag():
    """Initialize RAG instance"""
    if st.session_state.rag is None:
        with st.spinner("RAG 시스템 초기화 중..."):
            try:
                st.session_state.rag = LangGraphRAG(debug=st.session_state.debug_mode)
                st.success("✓ RAG 시스템이 초기화되었습니다!")
                return True
            except Exception as e:
                st.error(f"✗ RAG 초기화 실패: {e}")
                st.info("환경 변수(.env)와 데이터베이스가 설정되어 있는지 확인하세요.")
                return False
    return True


def format_search_results(results):
    """Format search results for display"""
    if not results:
        return ""

    html = "<div style='margin-top: 1rem;'>"
    html += "<h4>🔍 검색 결과 (Top 3)</h4>"

    for i, result in enumerate(results, 1):
        html += f"""
        <div class='search-result'>
            <h5>{i}. {result['product_name']}</h5>
            <p><strong>상품코드:</strong> {result['product_code']}</p>
            <p><strong>금리:</strong> {result['min_interest_rate']}% ~ {result['max_interest_rate']}%</p>
            <p><strong>요약:</strong> {result['product_summary'][:100]}...</p>
            <p><strong>RRF Score:</strong> {result['rrf_score']:.4f}</p>
        </div>
        """

    html += "</div>"
    return html


def stream_text(text, placeholder, delay=STREAMING_DELAY_SEC):
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(f"{displayed_text}{STREAMING_CURSOR}")
        time.sleep(delay)
    placeholder.markdown(displayed_text)


def render_assistant_extras(route, search_results):
    if route:
        badge_class = "route-search" if route == "search" else "route-direct"
        st.markdown(
            f"<span class='route-badge {badge_class}'>{route.upper()}</span>",
            unsafe_allow_html=True
        )

    if search_results:
        with st.expander("🔍 검색 결과 보기"):
            st.markdown(format_search_results(search_results), unsafe_allow_html=True)


def set_pending_question(question: str):
    st.session_state.pending_question = question


def process_question(prompt: str):
    """Process a question and return response"""
    try:
        if st.session_state.rag is None:
            raise RuntimeError("RAG 시스템이 초기화되지 않았습니다.")

        initial_state: RAGState = {
            "question": prompt,
            "route_decision": "",
            "search_results": [],
            "answer": "",
            "debug": st.session_state.debug_mode
        }

        final_state = st.session_state.rag.graph.invoke(initial_state)

        answer = final_state["answer"]
        route = final_state.get("route_decision", "unknown")
        search_results = final_state.get("search_results", [])

        return answer, route, search_results

    except Exception as e:
        import traceback
        error_msg = f"오류가 발생했습니다: {str(e)}\n\n{traceback.format_exc()}"
        return error_msg, "error", []


def main():
    # Header with home button
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("🏠 홈", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pending_question = None
            st.rerun()
    with col2:
        st.markdown("<div class='main-header'>🔍 LangGraph RAG</div>", unsafe_allow_html=True)

    st.markdown("<div class='sub-header'>Routing 기반 대출 상품 검색 시스템</div>", unsafe_allow_html=True)

    initialize_rag()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ 설정")

        # Debug mode toggle
        debug_mode = st.toggle("디버그 모드", value=st.session_state.debug_mode)
        if debug_mode != st.session_state.debug_mode:
            st.session_state.debug_mode = debug_mode
            # Reinitialize RAG with new debug mode
            if st.session_state.rag is not None:
                st.session_state.rag.close()
                st.session_state.rag = None
            initialize_rag()

        st.divider()

        # System info
        st.header("📊 시스템 정보")

        if st.session_state.rag is not None:
            st.success("🟢 RAG 시스템 활성화")
            st.info(f"모델: GPT-5-mini")
            st.info(f"검색: Hybrid (BM25 + Vector)")
            with st.expander("🧠 벡터 DB 정보", expanded=False):
                vector_info = st.session_state.rag.db.get_vector_db_info()
                if vector_info:
                    st.info(f"벡터 DB: {Config.TABLE_NAME}")
                    st.info(f"대출 상품 수: {vector_info['total']}")
                    st.info(f"임베딩 수: {vector_info['embeddings']} / {vector_info['total']}")
                else:
                    st.warning("벡터 DB 정보 조회 실패")
        else:
            st.warning("🔴 RAG 시스템 미활성화")

        st.divider()

        # Workflow info
        st.header("🔄 워크플로우")
        st.markdown("""
        ```
        START → route
                ├─ search → retrieve → generate
                └─ direct → generate
        ```
        """)

        st.divider()

        # Clear chat
        if st.button("🗑️ 대화 초기화", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # Statistics
        st.header("📈 통계")
        st.metric("총 대화 수", len(st.session_state.messages) // 2)

        # Count route types
        search_count = sum(1 for msg in st.session_state.messages
                          if msg.get("route") == "search")
        direct_count = sum(1 for msg in st.session_state.messages
                          if msg.get("route") == "direct")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("검색", search_count)
        with col2:
            st.metric("직접", direct_count)

    if st.session_state.rag is None:
        st.stop()

    # Chat interface
    st.header("💬 채팅")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message["role"] == "assistant":
                render_assistant_extras(message.get("route"), message.get("search_results"))

    # Chat input
    incoming_prompt = None
    if prompt := st.chat_input("질문을 입력하세요... (예: 의사 전용 대출 상품 추천해줘)"):
        incoming_prompt = prompt
        st.session_state.pending_question = None
    elif st.session_state.pending_question is not None:
        incoming_prompt = st.session_state.pending_question
        st.session_state.pending_question = None

    if incoming_prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": incoming_prompt,
            "timestamp": datetime.now().isoformat()
        })

        with st.chat_message("user"):
            st.markdown(incoming_prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("답변 생성 중..."):
                answer, route, search_results = process_question(incoming_prompt)
            stream_text(answer, message_placeholder)
            render_assistant_extras(route, search_results)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "route": route,
            "search_results": search_results,
            "timestamp": datetime.now().isoformat()
        })

    # Example questions
    if len(st.session_state.messages) == 0 and st.session_state.pending_question is None:
        st.markdown("---")
        st.subheader("💡 예제 질문")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**검색이 필요한 질문:**")
            examples_search = [
                "의사 전용 대출 상품 추천해줘",
                "저금리 대출 상품을 찾고 있어요",
                "전세자금대출 상품 알려주세요",
                "청년 대상 대출 상품이 있나요?"
            ]
            for example in examples_search:
                st.button(
                    f"📝 {example}",
                    key=f"ex_search_{example}",
                    use_container_width=True,
                    on_click=set_pending_question,
                    args=(example,)
                )

        with col2:
            st.markdown("**직접 답변 가능한 질문:**")
            examples_direct = [
                "안녕하세요",
                "감사합니다",
                "대출이 뭐예요?",
                "어떤 도움을 받을 수 있나요?"
            ]
            for example in examples_direct:
                st.button(
                    f"💬 {example}",
                    key=f"ex_direct_{example}",
                    use_container_width=True,
                    on_click=set_pending_question,
                    args=(example,)
                )

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.875rem;'>
        Powered by <strong>LangGraph</strong> + <strong>GPT-5-mini</strong> + <strong>Hybrid Search</strong> (BM25 + Vector)
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
