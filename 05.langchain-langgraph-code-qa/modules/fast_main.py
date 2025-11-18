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

LANGSMITH_PROJECT = "Github-Code-QA-RAG"
FASTAPI_SERVER_URL = "http://localhost:8000"  # FastAPI 서버 URL

logging.langsmith(LANGSMITH_PROJECT)

NAMESPACE = "langchain"

# 비동기 처리를 위한 스레드 풀
if "thread_pool" not in st.session_state:
    st.session_state["thread_pool"] = ThreadPoolExecutor(max_workers=5)

if "langsmith_client" not in st.session_state:
    st.session_state["langsmith_client"] = Client()
    
st.set_page_config(
    page_title="LangGraph 코드 어시스턴트",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)   

st.title("LangGraph 코드 어시스턴트")
st.markdown("**`LangChain`**,**`LangGraph`** 문서 기반으로 답변하는 봇입니다.")

with st.sidebar:
    st.markdown("제작자: 김재호")
    st.markdown("[LangChain][LangGraph] 도큐먼트를 기반으로 답변합니다.")

# 대화기록을 저장하기 위한 상태값
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 스레드 ID를저장하기 위한 상태값    
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid4())

# 질문 횟수를 추적하기 위한 상태값
if "question_count" not in st.session_state:
    st.session_state["question_count"] = 0

# 배치 처리를 위한 대화 임시 저장소
if "conversation_buffer" not in st.session_state:
    st.session_state["conversation_buffer"] = []

# 마지막 전송 시간
if "last_send_time" not in st.session_state:
    st.session_state["last_send_time"] = datetime.now()


# SIDE BAR생성
with st.sidebar:
    st.markdown("---")
    st.markdown("**대화 초기화**")
    
    # 초기화 버튼 생성
    clear_btn = st.button(
        "새로운 주제로 질문", type="primary", use_container_width=True # secondary tertiary primary
    )
    

def print_messages():
    for chat_message in st.session_state["messages"]:
        if chat_message.role == "user":
            st.chat_message(chat_message.role, avatar="🙎‍♂️").write(chat_message.content)
        else:
            st.chat_message(chat_message.role, avatar="😊").write(chat_message.content)

# 새로운 메시지를 추가
def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))
    
# 메시지 저장. user이면 HumanMessage, 아니면 AIMessage
def get_message_history():
    ret = []
    for chat_message in st.session_state["messages"]:
        if chat_message.role =="user":
            ret.append(HumanMessage(content=chat_message.content))
        else:
            ret.append(AIMessage(content=chat_message.content))
            
    return ret

if "feedback" not in st.session_state:
    st.session_state.feedback = {}

# open feedback은 일단 닫아야 한다.    
if "open_feedback" not in st.session_state:
    st.session_state["open_feedback"] = False
    

# 피드백 제출 폼

# client.list_runs(project_name=..., limit=...)는 LangSmith API를 통해 특정 프로젝트 내의 실행(runs)을 순회 가능한 이터레이터 형태로 가져오는 메서드입니다.
# next(iter(...))는 왜 쓰였나요? 결과적으로 위 코드는 "가장 최근 실행(run)을 하나만 받아오기" 위한 패턴입니다.
# iter(...)는 이터러블(iterable)을 이터레이터(iterator)로 변환합니다.
# next(...)는 그 이터레이터에서 첫 번째 요소를 꺼내옵니다.

def add_conversation_to_buffer(user_message: str, ai_response: str):
    """대화를 버퍼에 추가하고 조건에 따라 전송"""
    thread_id = st.session_state.get("thread_id", str(uuid4()))
    question_count = st.session_state.get("question_count", 0)
    
    conversation_data = {
        "thread_id": thread_id,
        "question_count": question_count,
        "user_message": user_message,
        "ai_response": ai_response,
        "timestamp": datetime.now().isoformat()
    }
    
    # 버퍼에 추가
    st.session_state["conversation_buffer"].append(conversation_data)
    
    # 전송 조건 확인 (5개 대화마다 또는 5분마다)
    should_send = (
        len(st.session_state["conversation_buffer"]) >= 5 or
        (datetime.now() - st.session_state["last_send_time"]).seconds >= 300
    )
    
    if should_send:
        submit_conversation_batch_async()

def submit_conversation_batch_async():
    """버퍼의 대화들을 배치로 FastAPI 서버에 전송"""
    if not st.session_state["conversation_buffer"]:
        return
    
    # 버퍼 복사 후 초기화
    conversations_to_send = st.session_state["conversation_buffer"].copy()
    st.session_state["conversation_buffer"] = []
    st.session_state["last_send_time"] = datetime.now()
    
    def _send_batch():
        try:
            payload = {
                "conversations": conversations_to_send,
                "batch_timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{FASTAPI_SERVER_URL}/conversation/batch",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"배치 대화 전송 성공: {len(conversations_to_send)}개")
            else:
                print(f"배치 대화 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"배치 대화 전송 오류: {e}")
    
    # 비동기로 실행
    st.session_state["thread_pool"].submit(_send_batch)

def submit_conversation_to_fastapi_async(user_message: str, ai_response: str):
    """단일 대화를 즉시 FastAPI 서버에 전송 (호환성용)"""
    # 메인 스레드에서 세션 상태 값을 가져옴
    thread_id = st.session_state.get("thread_id", str(uuid4()))
    question_count = st.session_state.get("question_count", 0)
    
    def _send_conversation():
        try:
            payload = {
                "thread_id": thread_id,
                "question_count": question_count,
                "user_message": user_message,
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{FASTAPI_SERVER_URL}/conversation",
                json=payload,
                timeout=5
            )
            
            if response.status_code != 200:
                print(f"대화 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"대화 전송 오류: {e}")
    
    # 비동기로 실행
    st.session_state["thread_pool"].submit(_send_conversation)

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

def submit_feedback_to_fastapi(feedback_data):
    """FastAPI 서버로 피드백 데이터 전송 (동기 버전 - 호환성용)"""
    try:
        # feedback_scores에서 "의견" 키를 제거하고 별도로 처리
        feedback_scores = {k: v for k, v in feedback_data.items() if k != "의견"}
        
        payload = {
            "thread_id": st.session_state.get("thread_id", str(uuid4())),
            "question_count": st.session_state.get("question_count", 0),
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
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "FastAPI 서버로 피드백이 성공적으로 전송되었습니다."
        else:
            return False, f"FastAPI 서버 전송 실패: {response.status_code} - {response.text}"
            
    except requests.exceptions.RequestException as e:
        return False, f"FastAPI 서버 연결 오류: {str(e)}"
    except Exception as e:
        return False, f"피드백 전송 중 오류: {str(e)}"

def submit_feedback():
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
                    
# 중복된 feedback 함수 제거



@st.dialog("답변 평가")
def feedback():
    st.session_state["open_feedback"] = False
    eval1 = st.number_input(
        "올바른 답변 (1:매우 낮음👎 ~ 5:매우 높음👍): 답변의 신뢰도",
        min_value=1,
        max_value=5,
        value=5,
    )
    eval2 = st.number_input(
        "도움됨 (1:매우 불만족👎 ~ 5:매우 만족👍): 답변 품질",
        min_value=1,
        max_value=5,
        value=5,
    )
    eval3 = st.number_input(
        "구체성 (1:매우 불만족👎 ~ 5:매우 만족👍): 답변의 구체성",
        min_value=1,
        max_value=5,
        value=5,
    )

    comment = st.text_area(
        "의견(선택)", value="", placeholder="의견을 입력해주세요(선택)"
    )

    if st.button("제출", type="primary"):
        with st.spinner("평가를 제출하는 중입니다..."):
            st.session_state.feedback = {
                "올바른 답변": eval1,
                "도움됨": eval2,
                "구체성": eval3,
                "의견": comment,
            }

            submit_feedback()

        st.rerun()
                   
                    
def submit_session_summary_async():
    """세션 전체 요약을 FastAPI 서버에 전송"""
    if not st.session_state["messages"]:
        return
    
    thread_id = st.session_state.get("thread_id", str(uuid4()))
    
    def _send_summary():
        try:
            # 전체 대화 내용 요약
            conversation_summary = {
                "thread_id": thread_id,
                "total_questions": st.session_state["question_count"],
                "session_duration": (datetime.now() - st.session_state["last_send_time"]).seconds,
                "conversation_count": len(st.session_state["messages"]),
                "timestamp": datetime.now().isoformat()
            }
            
            # 남은 버퍼가 있으면 함께 전송
            if st.session_state["conversation_buffer"]:
                conversation_summary["remaining_conversations"] = st.session_state["conversation_buffer"]
            
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

# 초기화 버튼을 누르면!
if clear_btn:
    # 세션 종료 시 요약 전송
    submit_session_summary_async()
    
    # 상태 초기화
    st.session_state["messages"] = []
    st.session_state["thread_id"] = str(uuid4())
    st.session_state["open_feedback"] = False
    st.session_state["question_count"] = 0
    st.session_state["conversation_buffer"] = []
    st.session_state["last_send_time"] = datetime.now()
    
# 이전 대화 기록 출력
print_messages()

# 사용자의 입력 (입력하는 채팅창)
user_input = st.chat_input("궁금한 내용을 물어보세요!")


if "graph" not in st.session_state:
    st.session_state["graph"] = create_graph()

# 만약에 사용자 입력이 들어오면...
if user_input:
    st.session_state["open_feedback"] = False
    
    # 질문 횟수 증가
    st.session_state["question_count"] += 1
    
    # 사용자의 입력을 화면에 표시
    st.chat_message("user", avatar="🙎‍♂️").write(user_input)
    
    # 세션 상태에서 그래프 객체를 가져옴
    graph = st.session_state["graph"]
    
    # AI답변을 표시
    with st.chat_message("assistant", avatar="😊"):
        streamlit_container = st.empty()
        
        # 그래프를 호출하여 응답
        response = stream_graph(
            graph,
            user_input,
            streamlit_container,
            thread_id=st.session_state["thread_id"],
        )
        
        ai_answer = response["generation"]
        
        st.write(ai_answer)
        
        # 평가 폼을 위한 빈 컨테이너
        eval_container = st.empty()
        
    # 5번째 질문마다만 평가 폼 생성
    if st.session_state["question_count"] % 5 == 0:
        with eval_container.form("my_form"):
            st.write("답변을 평가해 주세요 🙏")
            # 피드백 창 열기 상태를 True로 설정
            st.session_state["open_feedback"] = True
            
            # 평가 제출 버튼 생성
            submitted = st.form_submit_button("평가하기", type="primary")
            if submitted:
                st.write("평가를 제출하였습니다.")
    
    # 대화기록을 저장한다.
    add_message("user", user_input)
    add_message("assistant", ai_answer)
    
    # 대화를 버퍼에 추가하고 조건에 따라 배치 전송
    add_conversation_to_buffer(user_input, ai_answer)
else:
    # 5번째 질문마다만 피드백 다이얼로그 열기
    if st.session_state["open_feedback"] and st.session_state["question_count"] % 5 == 0:
        feedback()