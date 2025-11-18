import streamlit as st
from uuid import uuid4

from dotenv import load_dotenv

from streamlit_wrapper import create_graph, stream_graph

from langchain_teddynote import logging
from langsmith import Client
from langchain_core.messages import HumanMessage, AIMessage, ChatMessage

load_dotenv()

LANGSMITH_PROJECT = "RAG Template"

logging.langsmith(LANGSMITH_PROJECT)

NAMESPACE = "rag_template"

if "langsmith_client" not in st.session_state:
    st.session_state["langsmith_client"] = Client()
    
st.set_page_config(
    page_title="RAG Template",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)   

st.title("RAG Template")
st.markdown("**`RAG Template`** 문서 기반으로 답변하는 봇입니다.")

with st.sidebar:
    st.markdown("제작자: 김재호")
    st.markdown("RAG Template, 도큐먼트를 기반으로 답변합니다.")

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

def submit_feedback():
    client = st.session_state["langsmith_client"]
    if client:
        feedback = st.session_state.feedback
        run = next(iter(client.list_runs(project_name=LANGSMITH_PROJECT, limit=1)))
        parent_run_id = run.parent_run_ids[0]
        
        for key, value in feedback.items():
            if key in ["올바른 답변", "도움됨", "구체성"]:
                client.create_feedback(parent_run_id, key, score=value)
            elif key == "의견":
                if value:
                    client.create_feedback(parent_run_id, key, comment=value)
                    


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
                   

# 초기화 버튼을 누르면! (메모리 유지)
if clear_btn:
    st.session_state["messages"] = []
    # thread_id를 새로 생성하여 새로운 대화 세션 시작
    st.session_state["thread_id"] = str(uuid4())
    st.session_state["open_feedback"] = False
    st.session_state["question_count"] = 0
    

    
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
    
    # 이전 대화 기록을 가져옴
    
    
    # AI답변을 표시
    with st.chat_message("assistant", avatar="😊"):
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
else:
    # 5번째 질문마다만 피드백 다이얼로그 열기
    if st.session_state["open_feedback"] and st.session_state["question_count"] % 5 == 0:
        feedback()