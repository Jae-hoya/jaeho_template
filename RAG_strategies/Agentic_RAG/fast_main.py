import streamlit as st
from uuid import uuid4

from dotenv import load_dotenv

from streamlit_wrapper import create_graph, stream_graph

from langchain_teddynote import logging
from langsmith import Client
from langchain_core.messages import HumanMessage, AIMessage, ChatMessage

import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

LANGSMITH_PROJECT = "Agentic RAG System"
FASTAPI_SERVER_URL = "http://localhost:8000"  # FastAPI 서버 URL

logging.langsmith(LANGSMITH_PROJECT)

NAMESPACE = "agentic_rag"

# 비동기 처리를 위한 스레드 풀
if "thread_pool" not in st.session_state:
    st.session_state["thread_pool"] = ThreadPoolExecutor(max_workers=5)

if "langsmith_client" not in st.session_state:
    st.session_state["langsmith_client"] = Client()
    
st.set_page_config(
    page_title="Agentic RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)   

st.title("🤖 Agentic RAG System")
st.markdown("**다중 에이전트 기반 RAG 시스템** - SPRI AI Brief 문서와 웹 검색을 활용한 지능형 질의응답")

with st.sidebar:
    st.markdown("**제작자**: 김재호")
    st.markdown("**시스템**: Agentic RAG")
    st.markdown("**기능**:")
    st.markdown("- 📚 SPRI 문서 검색")
    st.markdown("- 🔍 웹 검색")
    st.markdown("- 📊 차트 생성")
    st.markdown("- 💭 일반 대화")
    
    st.markdown("---")
    st.markdown("### 🤖 에이전트 소개")
    st.markdown("**Retriever**: SPRI AI Brief 문서 검색")
    st.markdown("**Researcher**: 웹 검색 (TavilySearch)")
    st.markdown("**Coder**: Python 차트 생성")
    st.markdown("**General LLM**: 일반 대화")
    st.markdown("**Supervisor**: 에이전트 관리")

# 대화기록을 저장하기 위한 상태값
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 스레드 ID를저장하기 위한 상태값    
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid4())

# 질문 횟수를 추적하기 위한 상태값
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 0

# SIDE BAR생성
with st.sidebar:
    st.markdown("---")
    st.markdown("**대화 관리**")
    
    # 초기화 버튼 생성
    clear_btn = st.button(
        "🔄 새로운 주제로 질문", type="primary", use_container_width=True
    )
    
    # 에이전트 상태 표시
    st.markdown("---")
    st.markdown("### 📊 현재 상태")
    st.markdown(f"**질문 수**: {st.session_state['question_count']}")
    st.markdown(f"**스레드 ID**: `{st.session_state['thread_id'][:8]}...`")

def print_messages():
    """대화 기록을 화면에 출력"""
    for chat_message in st.session_state["messages"]:
        if chat_message.role == "user":
            st.chat_message(chat_message.role, avatar="🙎‍♂️").write(chat_message.content)
        else:
            st.chat_message(chat_message.role, avatar="🤖").write(chat_message.content)

def add_message(role, message):
    """새로운 메시지를 대화 기록에 추가"""
    st.session_state["messages"].append(ChatMessage(role=role, content=message))
    
def get_message_history():
    """대화 기록을 LangChain 메시지 형식으로 변환"""
    ret = []
    for chat_message in st.session_state["messages"]:
        if chat_message.role == "user":
            ret.append(HumanMessage(content=chat_message.content))
        else:
            ret.append(AIMessage(content=chat_message.content))
    return ret

# 피드백 관련 상태값
if "feedback" not in st.session_state:
    st.session_state.feedback = {}

if "open_feedback" not in st.session_state:
    st.session_state["open_feedback"] = False

def add_conversation_to_buffer(user_message: str, ai_response: str, used_tools: list = None):
    """대화를 thread_id별로 같은 파일에 저장"""
    thread_id = st.session_state.get("thread_id", str(uuid4()))
    question_count = st.session_state.get("question_count", 0)
    
    conversation_data = {
        "thread_id": thread_id,
        "question_count": question_count,
        "user_message": user_message,
        "ai_response": ai_response,
        "used_tools": used_tools or [],
        "timestamp": datetime.now().isoformat()
    }
    
    # thread_id별로 같은 파일에 저장
    submit_conversation_by_thread_async(conversation_data)

def submit_conversation_by_thread_async(conversation_data):
    """thread_id별로 같은 파일에 대화를 저장"""
    def _send_by_thread():
        try:
            response = requests.post(
                f"{FASTAPI_SERVER_URL}/conversation/thread",
                json=conversation_data,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"thread_id별 저장 성공: thread_id={conversation_data['thread_id']}, question_count={conversation_data['question_count']}")
            else:
                print(f"thread_id별 저장 실패: {response.status_code}")
                
        except Exception as e:
            print(f"thread_id별 저장 오류: {e}")
    
    # 비동기로 실행
    st.session_state["thread_pool"].submit(_send_by_thread)

def submit_feedback_to_fastapi_async(feedback_data):
    """비동기로 피드백 데이터를 FastAPI 서버에 전송"""
    # 메인 스레드에서 세션 상태 값을 가져옴
    thread_id = st.session_state.get("thread_id", str(uuid4()))
    question_count = st.session_state.get("question_count", 0)
    
    def _send_feedback():
        try:
            # feedback_scores에서 "의견" 키를 제거하고 별도로 처리
            feedback_scores = {k: v for k, v in feedback_data.items() if k != "의견"}
            
            payload = {
                "thread_id": thread_id,
                "question_count": question_count,
                "feedback_scores": feedback_scores,
                "timestamp": datetime.now().isoformat()
            }
            
            # 의견이 있으면 추가
            if "의견" in feedback_data and feedback_data["의견"]:
                payload["comment"] = feedback_data["의견"]
            
            print(f"전송할 피드백 데이터: {payload}")  # 디버깅용
            
            response = requests.post(
                f"{FASTAPI_SERVER_URL}/feedback",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 200:
                print("FastAPI 서버로 피드백이 성공적으로 전송되었습니다.")
            else:
                print(f"FastAPI 서버 전송 실패: {response.status_code}")
                print(f"응답 내용: {response.text}")
                
        except Exception as e:
            print(f"피드백 전송 오류: {e}")
    
    # 비동기로 실행
    st.session_state["thread_pool"].submit(_send_feedback)

def submit_session_summary_async():
    """세션 전체 요약을 FastAPI 서버에 전송"""
    if not st.session_state.get("messages", []):
        return
    
    thread_id = st.session_state.get("thread_id", str(uuid4()))
    question_count = st.session_state.get("question_count", 0)
    
    def _send_summary():
        try:
            # 전체 대화 내용 요약
            conversation_summary = {
                "thread_id": thread_id,
                "total_questions": question_count,
                "session_duration": 0,  # 세션 지속 시간 계산 로직 추가 가능
                "conversation_count": len(st.session_state.get("messages", [])),
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{FASTAPI_SERVER_URL}/session/summary",
                json=conversation_summary,
                timeout=10
            )
            
            if response.status_code == 200:
                print("세션 요약 전송 성공")
            else:
                print(f"세션 요약 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"세션 요약 전송 오류: {e}")
    
    # 비동기로 실행
    st.session_state["thread_pool"].submit(_send_summary)

def submit_feedback():
    """피드백을 LangSmith와 FastAPI에 제출"""
    client = st.session_state["langsmith_client"]
    feedback = st.session_state.feedback
    
    # LangSmith로 피드백 전송 (동기)
    if client:
        try:
            run = next(iter(client.list_runs(project_name=LANGSMITH_PROJECT, limit=1)))
            parent_run_id = run.parent_run_ids[0]
            
            for key, value in feedback.items():
                if key in ["올바른 답변", "도움됨", "구체성"]:
                    client.create_feedback(parent_run_id, key, score=value)
                elif key == "의견":
                    if value:
                        client.create_feedback(parent_run_id, key, comment=value)
        except Exception as e:
            st.error(f"LangSmith 피드백 전송 오류: {str(e)}")
    
    # FastAPI 서버로 피드백 전송 (비동기)
    submit_feedback_to_fastapi_async(feedback)
    st.success("피드백이 제출되었습니다. (비동기 처리 중)")

@st.dialog("📝 답변 평가")
def feedback():
    """피드백 다이얼로그"""
    st.session_state["open_feedback"] = False
    
    st.markdown("### 답변을 평가해주세요 🙏")
    
    eval1 = st.number_input(
        "🎯 **올바른 답변** (1:매우 낮음👎 ~ 5:매우 높음👍)",
        min_value=1,
        max_value=5,
        value=5,
        help="답변의 정확성과 신뢰도"
    )
    eval2 = st.number_input(
        "💡 **도움됨** (1:매우 불만족👎 ~ 5:매우 만족👍)",
        min_value=1,
        max_value=5,
        value=5,
        help="답변이 질문에 얼마나 도움이 되었는지"
    )
    eval3 = st.number_input(
        "📋 **구체성** (1:매우 불만족👎 ~ 5:매우 만족👍)",
        min_value=1,
        max_value=5,
        value=5,
        help="답변의 구체성과 상세함"
    )

    comment = st.text_area(
        "💬 **의견** (선택사항)", 
        value="", 
        placeholder="추가 의견이나 개선사항을 입력해주세요",
        help="자유로운 의견을 남겨주세요"
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ 취소", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("✅ 제출", type="primary", use_container_width=True):
            with st.spinner("평가를 제출하는 중입니다..."):
                st.session_state.feedback = {
                    "올바른 답변": eval1,
                    "도움됨": eval2,
                    "구체성": eval3,
                    "의견": comment,
                }
                submit_feedback()
            st.success("평가가 제출되었습니다! 감사합니다.")
            st.rerun()

# 초기화 버튼을 누르면!
if clear_btn:
    # 세션 종료 시 요약 전송
    submit_session_summary_async()
    
    # 상태 초기화
    st.session_state["messages"] = []
    st.session_state["thread_id"] = str(uuid4())
    st.session_state["open_feedback"] = False
    st.session_state["question_count"] = 0
    st.success("🔄 새로운 대화 세션이 시작되었습니다!")

# 이전 대화 기록 출력
print_messages()

# 사용자의 입력 (입력하는 채팅창)
user_input = st.chat_input("🤔 궁금한 내용을 물어보세요! (SPRI 문서, 웹 검색, 차트 생성 등)")

# 그래프 초기화
if "graph" not in st.session_state:
    with st.spinner("🤖 Agentic RAG 시스템을 초기화하는 중입니다..."):
        st.session_state["graph"] = create_graph()
    st.success("✅ 시스템이 준비되었습니다!")

# 만약에 사용자 입력이 들어오면...
if user_input:
    st.session_state["open_feedback"] = False
    
    # 질문 횟수 증가
    st.session_state["question_count"] += 1
    
    # 사용자의 입력을 화면에 표시
    st.chat_message("user", avatar="🙎‍♂️").write(user_input)
    
    # 사용자 입력을 대화 기록에 먼저 추가
    add_message("user", user_input)
    
    # 세션 상태에서 그래프 객체를 가져옴
    graph = st.session_state["graph"]
    
    # AI답변을 표시
    with st.chat_message("assistant", avatar="🤖"):
        streamlit_container = st.empty()
        
        # 그래프를 호출하여 응답
        response = stream_graph(
            graph,
            user_input,
            streamlit_container,
            thread_id=st.session_state["thread_id"],
            chat_history=get_message_history()
        )
        
        ai_answer = response["answer"]
        used_tools = response.get("used_tools", [])
        
        # 최종 답변 표시
        st.write(ai_answer)
        
        # 사용된 도구 정보 표시
        if used_tools:
            tool_names = {
                "Retriever": "📚 SPRI 문서 검색",
                "Researcher": "🔍 웹 검색 (TavilySearch)",
                "Coder": "📊 Python 차트 생성",
                "General LLM": "💭 일반 대화"
            }
            st.markdown("---")
            st.markdown("**🛠️ 이번 답변에 사용된 도구들:**")
            for tool in used_tools:
                st.markdown(f"• {tool_names.get(tool, tool)}")
        
        # 평가 폼을 위한 빈 컨테이너
        eval_container = st.empty()
    
    # 5번째 질문마다만 평가 폼 생성
    if st.session_state["question_count"] % 5 == 0:
        with eval_container.form("feedback_form"):
            st.markdown("### 📝 답변을 평가해 주세요 🙏")
            st.markdown("5번째 질문입니다. 소중한 피드백을 부탁드립니다!")
            
            # 피드백 창 열기 상태를 True로 설정
            st.session_state["open_feedback"] = True
            
            # 평가 제출 버튼 생성
            submitted = st.form_submit_button("📊 평가하기", type="primary")
            if submitted:
                st.success("평가를 제출하였습니다. 감사합니다!")
    
    # 대화기록을 저장한다.
    add_message("assistant", ai_answer)
    
    # 대화를 thread_id별로 같은 파일에 저장
    add_conversation_to_buffer(user_input, ai_answer, used_tools)
else:
    # 5번째 질문마다만 피드백 다이얼로그 열기
    if st.session_state["open_feedback"] and st.session_state["question_count"] % 5 == 0:
        feedback()

# 하단에 시스템 정보 표시
st.markdown("---")
st.markdown("### 🔧 시스템 정보")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("**프로젝트**: Agentic RAG")
with col2:
    st.markdown("**버전**: 1.0.0")
with col3:
    st.markdown("**상태**: 🟢 정상 작동")
