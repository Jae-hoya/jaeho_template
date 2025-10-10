import streamlit  as st
import asyncio
import nest_asyncio
import json
import os
import platform

# Windows에서 이벤트 루프 정책 설정(호환성용)
if platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# 중첩/재진입 가능한 이벤트 루프 패치
nest_asyncio.apply()

# 세션당 1개의 이벤트 루프 생성·등록
if "event_loop" not in st.session_state:
    loop = asyncio.new_event_loop()
    st.session_state.event_loop = loop
    asyncio.set_event_loop(loop)
    
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mcp_adapters.client import MultiServerMCPClient

from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_core.messages.tool import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

from utils import astream_graph, random_uuid

from dotenv import load_dotenv
load_dotenv(override=True)

# config.json 파일 경로 설정
CONFIG_FILE_PATH = "config.json"

# json 설정 파일 저장 함수
def save_config_to_json(config):
    """
    config.json 파일에 저장합니다.
    
    매개변수:
        config (dict): 저장할 설정
        
    딕셔너리 자료형을 JSON 파일로 생성할 때는 다음처럼 json.dump() 함수를 사용합니다.
    
    dump() 매개변수:
        indent=2: 사람이 보기 좋게 들여쓰기 2칸.
        ensure_ascii=False: 한글을 \\uXXXX로 이스케이프하지 않고 그대로 저장.
    """
    
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            return True
    except Exception as e:
        st.error(f"설정 파일 저장 중 오류 발생: {str(e)}")
        return False

import sys

# json 설정파일 로드 함수
def load_config_from_json():
    """
    config.json 파일에서 설정을 로드합니다.
    파일이 없는 경우, 기본 설정으로 파일을 생성합니다.
    
    반환값:
        dict: 로드된 설정
    
    JSON 파일을 파이썬 딕셔너리로 읽을 때는 다음처럼 json.load() 함수를 사용합니다.
    """
    default_config = {
        "get_current_time": {
            "command": "python",
            "args": ["./mcp_server_time.py"],
            "transport": "stdio"
        },
        "rag_retriever": {
            "command": sys.executable,
            "args": ["./mcp_rag_stdio.py"],
            "transport": "stdio"
        },
        "mcp-rag": {
            "url": "http://localhost:8101/sse",  # 실제 SSE 서버 주소로 변경
            "transport": "sse",
        },
    }
        # SSE 방식도 사용 가능합니다 (먼저 서버 실행 필요):
        # 1. 터미널에서: python mcp_rag_sse.py
        # 2. 위의 rag_retriever를 아래로 교체:
    #     "rag_retriever": {
    #         "url": "http://localhost:8101/sse",
    #         "transport": "sse"
    #     }
    # }
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                # return json.load(f)
                loaded = json.load(f)
                # 파일이 비어있으면 default_config 사용
                if not loaded:
                    save_config_to_json(default_config)
                    return default_config
                return loaded
        else:
            save_config_to_json(default_config)
            return default_config
    except Exception as e:
        st.error(f"설정 파일 로드 중 오류 발생: {str(e)}")
        return default_config
    
# 로그인 세션 변수 초기화 (세션 키 생성)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    
# 로그인 필요 여부 확인
use_login = os.environ.get("USE_LOGIN", "false").lower() == "true"

# 로그인 상태에 따른 페이지 사용
if use_login and not st.session_state.authenticated:
    st.set_page_config(page_title="Agent with MCP Tools", page_icon="🧠") # 로그인 페이지
else:
    st.set_page_config(page_title="Agent with MCP Tools", page_icon="🧠", layout="wide") # 메인 페이지
    
if use_login and not st.session_state.authenticated:
    st.title("🔐 로그인")
    st.markdown("시스템을 사용하려면 로그인이 필요합니다.")
    
    with st.form("login_form"):
        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")
        submit_button = st.form_submit_button("로그인")
        
        if submit_button:
            expected_username = os.environ.get("USER_ID")
            expected_password = os.environ.get("USER_PASSWORD")
            
            if username == expected_username and password == expected_password:
                st.session_state.authenticated = True
                st.success("🆗 로그인 성공! 잠시만 기다려주세요...")
                st.rerun()
            else:
                st.error("🚫 아이디 또는 비밀번호가 올바르지 않습니다.")
                
    st.stop()
    

# 사이드바 
st.sidebar.markdown("Made by [Jae.hoya](skyop455@gmail.com)")

# 구분순
st.sidebar.divider()
st.sidebar.markdown(
    "MCP 도구 활용 에이전트"
)

# 기존 페이지 타이틀 및 설명
st.title("MCP 도구 활용 에이전트")
st.markdown("MCP 도구를 활용한 ReAct 에이전트에게 질문해보세요.")

SYSTEM_PROMPT = """<ROLE>
You are a smart agent with an ability to use tools. 
You will be given a question and you will use the tools to answer the question.
Pick the most relevant tool to answer the question. 
If you are failed to answer the question, try different tools to get context.
Your answer should be very polite and professional.
</ROLE>

----

<INSTRUCTIONS>
Step 1: Analyze the question
- Analyze user's question and final goal.
- If the user's question is consist of multiple sub-questions, split them into smaller sub-questions.

Step 2: Pick the most relevant tool
- Pick the most relevant tool to answer the question.
- If you are failed to answer the question, try different tools to get context.

Step 3: Answer the question
- Answer the question in the same language as the question.
- Your answer should be very polite and professional.

Step 4: Provide the source of the answer(if applicable)
- If you've used the tool, provide the source of the answer.
- Valid sources are either a website(URL) or a document(PDF, etc).

Guidelines:
- If you've used the tool, your answer should be based on the tool's output(tool's output is more important than your own knowledge).
- If you've used the tool, and the source is valid URL, provide the source(URL) of the answer.
- Skip providing the source if the source is not URL.
- Answer in the same language as the question.
- Answer should be concise and to the point.
- Avoid response your output with any other information than the answer and the source.  
</INSTRUCTIONS>

----

<OUTPUT_FORMAT>
(concise answer to the question)

**Source**(if applicable)
- (source1: valid URL)
- (source2: valid URL)
- ...
</OUTPUT_FORMAT>
"""

OUTPUT_TOKEN_INFO = {
    "gpt-4.1": {"max_tokens": 32000},
    "gpt-4.1-mini": {"max_tokens": 32000},
    "gpt-4o-mini": {"max_tokens": 16000},
    "gpt-4o": {"max_tokens": 16000},
    # "claude-3-7-sonnet-latest": {"max_tokens": 64000},
    # "claude-3-5-sonnet-latest": {"max_tokens": 8192},
    # "claude-3-5-haiku-latest": {"max_tokens": 8192},
}

# 세션 상태 초기화
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False
    st.session_state.agent = None # ReAct 에이전트 객체공간
    st.session_state.history = [] # 대화 기록 저장 리스트
    st.session_state.mcp_client = None # MCP 클라이언트 객체 저장 공간
    st.session_state.timeout_seconds = 120 # 응답 생성 제한 시간(초), 기본값 120초
    st.session_state.selected_model = "gpt-4.1.mini" # 기본 모델 선택
    st.session_state.recursion_limit = 100 # 재귀 호출 제한, 기본값 100

# 쓰레드 ID 초기화
if "thread_id" not in st.session_state:
    st.session_state.thread_id = random_uuid()

# ------ 함수 정의 부분 --------
# MCP 종료
async def cleanup_mcp_client():
    """
    기존 MCP 클라이언트를 안전하게 종료 합니다.
    기존 클라이언트가 있는경우, 정상적으로 리소스를 해제합니다
    """
    if "mcp_client" in st.session_state and st.session_state.mcp_client is not None:
        try:
            # await st.session_state.mcp_client.__aexit__(None, None, None)
            # langchain-mcp-adapters 0.1.0+에서는 context manager 미지원
            # 단순히 참조를 제거하여 가비지 컬렉션되도록 함
            st.session_state.mcp_client = None
            
        except Exception as e:
            import traceback
            st.warning(f"MCP 클라이언트 종료 중 오류: {str(e)}")

# 대화 기록 출력            
def print_message():
    """
    채팅 기록을 화면에 출력합니다.
    
    사용자와 어시스턴트의 메시지를 구분하여 화면에 표시혹,
    도구 호출 정보는 어시스턴트 메시지 컨테이너 내에 표시합니다.
    """
    i = 0
    while i < len(st.session_state.history):
        message = st.session_state.history[i]
        
        if message["role"] == "user":
            st.chat_message("user", avatar="👤").markdown(message["content"])
            i += 1
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])
                
                # 다음 메시지가 도구 호출 정보인지 확인
                if (
                    i + 1 < len(st.session_state.history)
                    and st.session_state.history[i+1]["role"] == "assistant_tool"
                ):
                    with st.expander("🔧 도구 호출 정보", expanded=False): # 도구 호출 정보를 컨테이너에 표시
                        st.markdown(st.session_state.history[i+1]["content"])
                    i += 2 # 두 메시지를 함께 처리했으므로 2 증가
                else:
                    i += 1 # 일반 메시지만 처리했으므로 1 증가
        else:
            # assistant_tool 메시지는 위에서 처리되므로 건너뜀
            i += 1
            
def get_streaming_callback(text_placeholder, tool_placeholder):
    """
    스트리밍 콜백함수 생성
    
    `이 함수는 LLM에서 생성되는 응답을 실시간으로 화면에 표시하기 위한 콜백함수를 생성`
    `텍스트 응답과 도구 호출 정보를 각각 다른영역에 표시`
    
    매개변수:
        text_placeholder: 텍스트 응답을 표시할 Streamlit 컴포넌트
        tool_placeholder: 도구 호출 정보를 표시할 Streamlit 컴포넌트
        
    반환값:
        callback_func: 스트리밍 콜백함수
        accumulated_text: 누적된 텍스트 응답을 저장하는 리스트
        accumulated_tool: 누적된 도구 호출 정보를 저장하는 리스트
    """
    accumulated_text = []
    accumulated_tool = []
    
    def callback_func(message: dict):
        # nonlocal: 바깥 함수 스코프에 있는 변수를 재바인딩(값 다시 할당) 하겠다고 선언하는 키워드입니다.
        nonlocal accumulated_text, accumulated_tool
        message_content = message.get("content", None)
                
        if isinstance(message_content, AIMessageChunk): # isinstance: 객체의 타입을 확인하는 함수
            content = message_content.content
            # 콘텐츠가 리스트 형태인 경우 (LLM 모델 등에서 주로 발생)
            if isinstance(content, list) and len(content) > 0:
                message_chunk = content[0]
                
                # 텍스트 타입인경우
                if message_chunk["type"] == "text":
                    accumulated_text.append(message_chunk["text"])
                    text_placeholder.markdown("".join(accumulated_text)) # "".join(accumulated_text): 리스트를 문자열로! " " 와 같은띄어쓰기 조차도 문자열로 본다
                
                # 도구 사용 타입인 경우
                elif message_chunk["type"] == "tool_use":
                    if "partial_json" in message_chunk:
                        accumulated_tool.append(message_chunk["partial_json"])
                    else:
                        tool_call_chunks = message_content.tool_call_chunks
                        tool_call_chunk = tool_call_chunks[0]
                        accumulated_tool.append(
                            "\n```json\n" + str(tool_call_chunk) + "\n```\n"
                        )
                    with tool_placeholder.expander("도구 호출 정보", expanded=True):
                        st.markdown("".join(accumulated_tool))
            
            # tool_calls 속성이 있는 경우 처리
            elif(
                hasattr(message_content, "tool_calls") # hasattr 속성 존재 판별하는 함수
                and message_content.tool_calls
                and len(message_content.tool_calls[0]["name"]) > 0
            ):
                tool_call_info = message_content.tool_calls[0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander("도구 호출 정보", expanded=True):
                    st.markdown("".join(accumulated_tool))
                    
            # 단순 문자열 처리
            elif isinstance(content, str):
                accumulated_text.append(content)
                text_placeholder.markdown("".join(accumulated_text))
            
            # 유효하지 않은 도구 호출 정보가 있는 경우
            elif (
                hasattr(message_content, "invalid_tool_calls")
                and message_content.invalid_tool_calls
            ):
                tool_call_info = message_content.invalid_tool_calls[0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander(
                    "도구호출 정보: 유효하지 않음", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
                    
            # tool_call_chinks 속성이 있는경우
            elif(
                hasattr(message_content, "tool_call_chunks")
                and message_content.tool_call_chunks
            ):
                tool_call_chunk = message_content.tool_call_chunks[0]
                accumulated_tool.append(
                    "\n```json\n" + str(tool_call_chunk) + "\n```\n"
                )
                with tool_placeholder.expander(
                    "도구호출 정보", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
            
            # additional_kwargs에 tool_calls가 있는 경우 처리 (다양한 모델 처리)
            elif(
                hasattr(message_content, "additional_kwargs")
                and "tool_calls" in message_content.additional_kwargs
            ):
                tool_call_info = message_content.additional_kwargs["tool_calls"][0]
                accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
                with tool_placeholder.expander(
                    "도구호출 정보", expanded=True
                ):
                    st.markdown("".join(accumulated_tool))
                    
        # 도구 메시지인 경우 처리 (도구의 응답)
        elif isinstance(message_content, ToolMessage):
            accumulated_tool.append(
                "\n```json\n" + str(message_content.content) + "\n```\n"
            )
            with tool_placeholder.expander(
                "도구호출 정보", expanded=True
            ):
                st.markdown("".join(accumulated_tool))
        return None
            
    return callback_func, accumulated_text, accumulated_tool
                
async def process_query(query, text_placeholder, tool_placeholder, timeout_seconds=120):
    """
    사용자 질문을 처리하고 응답을 생성합니다.

    이 함수는 사용자의 질문을 에이전트에 전달하고, 응답을 실시간으로 스트리밍하여 표시합니다.
    지정된 시간 내에 응답이 완료되지 않으면 타임아웃 오류를 반환합니다.

    매개변수:
        query: 사용자가 입력한 질문 텍스트
        text_placeholder: 텍스트 응답을 표시할 Streamlit 컴포넌트
        tool_placeholder: 도구 호출 정보를 표시할 Streamlit 컴포넌트
        timeout_seconds: 응답 생성 제한 시간(초)

    반환값:
        response: 에이전트의 응답 객체
        final_text: 최종 텍스트 응답
        final_tool: 최종 도구 호출 정보
    """
    try:
        # get_streaming_callback 함수의 결과가 튜플의 언팩킹으로 streaming_callback, accumulated_text_obj, accumulated_tool_obj에 저장되는 것이다.
        if st.session_state.agent: # st.session_initialized 에서 사용
            streaming_callback, accumulated_text_obj, accumulated_tool_obj = (
                get_streaming_callback(text_placeholder, tool_placeholder)
            )
            # 실행, 스트리밍 하는 트리거: 에이전트가 토큰/툴 로그를 생성할 때마다 콜백이 호출되어 UI를 갱신.
            try:
                response = await asyncio.wait_for(
                    astream_graph(st.session_state.agent,
                                  {"messages": [HumanMessage(content=query)]},
                                  callback = streaming_callback,
                                  config = RunnableConfig(
                                      recursion_limit = st.session_state.recursion_limit,
                                      thread_id = st.session_state.thread_id
                                  ),
                        ),
                    timeout = timeout_seconds
                )            
            # 타임 아웃이 발생했을 때,
            except asyncio.TimeoutError:
                error_msg = f"요청 시간이 {timeout_seconds}초를 초과했습니다. 나중에 다시 시도해 주세요."
                return {"error": error_msg}, error_msg, ""
            # 스트리밍 중 누적된 청크들을 결합하여 최종 문자열 생성
            final_text = "".join(accumulated_text_obj)
            final_tool = "".join(accumulated_tool_obj)
            return response, final_text, final_tool
        # 에이전트가 초기화 되지 않았을 때,
        else:
            return (
                {"error": "에이전트가 초기화되지 않았습니다"},
                "에이전트가 초기화 되지 않았습니다.",
                "",
            )
    # 모든 예외를 감지
    except Exception as e:
        import traceback        
        error_msg = f"쿼리 처리 중 오류 발생 {str(e)}\n{traceback.format_exc()}" # traceback.format_exc(): 스택 트레이스를 문자열로 만들어 디버깅에 활용합니다.
        return {"error": error_msg}, error_msg, "" 
    # get_streaming_callback은 (streaming_callback, accumulated_text_obj, accumulated_tool_obj)
    # 3개의 값을 반환하며, 위에서 언패킹하여 사용합니다.
    # 호출부가 (response, final_text, final_tool)로 3개 언패킹하므로, 본 함수는 정상/에러 모두 (.., .., ..) 3-튜플을 반환한다.
            
            
async def initialize_session(mcp_config=None):
    """
    MCP 세션과 에이전트를 초기화합니다.

    매개변수:
        mcp_config: MCP 도구 설정 정보(JSON). None인 경우 기본 설정 사용

    반환값:
        bool: 초기화 성공 여부
    """
    with st.spinner("MCP 서버에 연결중"):
        await cleanup_mcp_client() # 기존 클라이언트를 안전하게 정리
        
        if mcp_config is None:
            mcp_config = load_config_from_json()
        
        # MCP SERVER를 연결하는 핵심코드
        # client, session_state.mcp_client는 MultiServerMCPClient(mcp_config)
        client = MultiServerMCPClient(mcp_config)
        # await client.__aenter__()
        # tools = client.get_tools()
        # langchain-mcp-adapters 0.1.0+ 버전에서는 __aenter__ 대신 직접 get_tools() 호출
        tools = await client.get_tools()
        
        st.session_state.tool_count = len(tools)
        st.session_state.mcp_client = client
        
        # 선택된 모델에 따라 적절한 모델 초기화
        selected_model = st.session_state.selected_model
        
        if selected_model in [
            "gpt-4.1-mini",
            "gpt-4.1",
            "gpt-4o-mini",
            "gpt-4o",            
        ]:
            model = ChatOpenAI(
                model=selected_model,
                temperature=0.1,
                max_tokens=OUTPUT_TOKEN_INFO[selected_model]['max_tokens']
            )
        else:
            model = ChatAnthropic(
                model=selected_model,
                temperature=0.1,
                max_tokens=OUTPUT_TOKEN_INFO[selected_model]['max_tokens']
            )
        
        agent = create_react_agent(
            model=model,
            tools=tools, # tools = client.get_tools()
            checkpointer=MemorySaver(),
            prompt=SYSTEM_PROMPT,            
        )
        st.session_state.agent = agent
        st.session_state.session_initialized = True
        return True
            
# --- 사이드 바: 시스템 설정 섹션 ---
with st.sidebar:
    st.subheader("⚙️ 시스템 설정")
    st.markdown("현재 Anthropic API는 요금이 부족합니다.")
    # 모델 선택 기능
    available_models = []
    
    has_openai_key = os.environ.get("OPENAI_API_KEY") is not None
    if has_openai_key:
        available_models.extend(
            [
                "gpt-4.1-mini",
                "gpt-4.1",
                "gpt-4o-mini",
                "gpt-4o",  
            ]
        )
    has_anthropic_key = os.environ.get("ANTHROPIC_API_KEY") is not None
    if has_anthropic_key:
        available_models.extend(
            [
                "claude-3-7-sonnet-latest",
                "claude-3-5-sonnet-latest",
                "claude-3-5-haiku-latest",
            ]
        )
        
    if not available_models:
        st.warning(
            "⚠️ API 키가 설정되지 않았습니다. .env 파일에 OPENAI_API_KEY 또는 ANTHROPIC_API_KEY를 추가해주세요."
        )
        available_models = ["gpt-4.1-mini"]
        
    previous_model = st.session_state.selected_model
    
    st.session_state.selected_model = st.selectbox(
        "🤖 모델 선택",
        options=available_models,
        index=(
            available_models.index(st.session_state.selected_model)
            if st.session_state.selected_model in available_models
            else 0
        ),
        help="Anthropic 모델은 ANTHROPIC_API_KEY가, OpenAI 모델은 OPENAI_API_KEY가 환경변수로 설정되어야 합니다.",
    )
    # 모델이 변경되었을 때 세션 초기화 필요 알림
    if (
        previous_model != st.session_state.selected_model
        and st.session_state.session_initialized
    ):
        st.warning(
            "모델이 변경되었습니다. '설정 적용하기' 버튼을 눌러 변경사항을 적용하세요."
        )
        
    # 타임아웃 설정 슬라이더
    st.session_state.timeout_seconds = st.slider(
        "응답 생성 제한 시간(초)",
        min_value=60,
        max_value=300,
        value=st.session_state.timeout_seconds,
        step=10,
        help="에이전트가 응답을 생성하는 최대 시간을 설정합니다. 복잡한 작업은 더 긴 시간이 필요할 수 있습니다.",
    )
    
    st.session_state.recursion_limit = st.slider(
        "재귀 호출 제한(횟수)",
        min_value=10,
        max_value=200,
        value=st.session_state.recursion_limit,
        step=10,
        help="재귀 호출 제한 횟수를 설정합니다. 너무 높은 값을 설정하면 메모리 부족 문제가 발생할 수 있습니다.",
    )
    # 구분선 추가
    st.divider() 
    
    # 도구 섹션 추가
    st.subheader("도구 설정")
    
    # mcp expander 상태를 세션 상태로 관리
    if "mcp_tools_expander" not in st.session_state:
        st.session_state.mcp_tools_expander = False
        
    with st.expander("MCP 도구 추가", expanded=st.session_state.mcp_tools_expander):
        # config.json 파일에서 설정 로드하여 표시
        loaded_config = load_config_from_json()
        default_config_text = json.dumps(loaded_config, indent=2, ensure_ascii=False)
        
        # pending config가 없으면 기존 mcp_config_text 기반으로 생성
        # 항상 default_config를 기본으로 하고, 파일에서 로드한 추가 도구를 병합
        if "pending_mcp_config" not in st.session_state:
            try:
                # default_config를 먼저 로드
                default_config = {
                    "get_current_time": {
                        "command": "python",
                        "args": ["./mcp_server_time.py"],
                        "transport": "stdio"
                    },
                    "rag_retriever": {
                        "command": sys.executable,
                        "args": ["./mcp_rag_stdio.py"],
                        "transport": "stdio"
                    },
                    "mcp-rag": {
                        "url": "http://localhost:8101/sse",  # 실제 SSE 서버 주소로 변경
                        "transport": "sse",
                    },
                }
                # default_config와 loaded_config 병합 (loaded_config가 우선순위)
                st.session_state.pending_mcp_config = {**default_config, **loaded_config}
            except Exception as e:
                st.error(f"초기 pending config 설정 실패: {e}")
                
        # 개별 도구
        st.subheader("도구 추가")
        st.markdown(
            """
            ⚠️ **중요**: JSON을 반드시 중괄호(`{}`)로 감싸야 합니다."""
        )
        
        # 보다 명확한 예시 제공
        example_json = {
            "github": {
                "command": "npx",
                "args": [
                    "-y",
                    "@smithery/cli@latest",
                    "run",
                    "@smithery-ai/github",
                    "--config",
                    '{"githubPersonalAccessToken":"your_token_here"}',
                ],
                "transport": "stdio",
            }
        }
        
        default_text = json.dumps(example_json, indent=2, ensure_ascii=False)
        
        new_tool_json = st.text_area(
            "도구 JSON",
            default_text,
            height=250,
        )
        
        if st.button(
            "도구 추가",
            type="primary",
            key="add_tool_button",
            use_container_width=True,
        ):
            try:
                # 입력값 인증
                if not new_tool_json.strip().startswith(
                    "{"
                ) or not new_tool_json.strip().endswith("}"):
                    st.error("JSON은 중괄호({})로 시작하고 끝나야 합니다.")
                    st.markdown('올바른 형식: `{ "도구이름": { ... } }`')
                else:
                    # JSON 파싱
                    parsed_tool = json.loads(new_tool_json)
                    
                    if "mcpServers" in parsed_tool:
                        parsed_tool = parsed_tool["mcpServers"]
                        st.info(
                            "'mcpServers' 형식이 감지되었습니다. 자동으로 변환합니다."
                        )
                    
                    # 도구가 없다면
                    if len(parsed_tool) == 0:
                        st.error("최소 하나 이상의 도구를 입력해주세요.")
                    
                    # 처리된 모든 도구에 대해서,
                    else:
                        success_tools = []
                        for tool_name, tool_config in parsed_tool.items():
                            if "url" in tool_config:
                                tool_config["transport"] = "sse"
                                st.info(
                                    f"'{tool_name}' 도구에 URL이 감지되어 transport를 'sse'로 설정했습니다."
                                )
                            # URL이 없고 transport도 없는 경우 기본값 "stdio" 설정
                            elif "transport" not in tool_config:
                                tool_config["transport"] = "stdio"
                                
                            # 필수 필드 확인
                            if (
                                "command" not in tool_config
                                and "url" not in tool_config
                            ):
                                st.error(
                                    f"'{tool_name}' 도구 설정에는 'command' 또는 'url' 필드가 필요합니다."
                                )
                            elif "command" in tool_config and "args" not in tool_config:
                                st.error(
                                    f"'{tool_name}' 도구 설정에는 'args' 필드가 필요합니다."
                                )
                            elif "command" in tool_config and not isinstance(
                                tool_config["args"], list
                            ):
                                st.error(
                                    f"'{tool_name}' 도구의 'args' 필드는 반드시 배열([]) 형식이어야 합니다."
                                )
                            else:
                                # pending_mcp_config에 도구 추가
                                st.session_state.pending_mcp_config[tool_name] = (
                            )
                        
                        # 성공 메시지
                        if success_tools:
                            if len(success_tools) == 1:
                                st.success(
                                    f"{success_tools[0]} 도구가 추가되었습니다. 적용하려면 '설정 적용하기' 버튼을 눌러주세요."
                                )
                            else:
                                tool_names = ", ".join(success_tools)
                                st.success(
                                    f"총 {len(success_tools)}개 도구({tool_names})가 추가되었습니다. 적용하려면 '설정 적용하기' 버튼을 눌러주세요."
                                )
                            # 추가되면 expander를 접어줌
                            st.session_state.mcp_tools_expander = False
                            st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"JSON 파싱 에러: {e}")
                st.markdown(
                    f"""
                **수정 방법**:
                1. JSON 형식이 올바른지 확인하세요.
                2. 모든 키는 큰따옴표(")로 감싸야 합니다.
                3. 문자열 값도 큰따옴표(")로 감싸야 합니다.
                4. 문자열 내에서 큰따옴표를 사용할 경우 이스케이프(\\")해야 합니다.
                """
                )
            except Exception as e:
                st.error(f"오류 발생: {e}")
    
    # 도구 목록 표시 및 삭제 버튼 추가
    with st.expander("등록된 도구 목록", expanded=True):
        try:
            pending_config = st.session_state.pending_mcp_config # loaded_config가 저장된 공간
        except Exception as e:
            st.error("유요한 mcp 도구 설정이 아닙니다")
        else:
            for tool_name in list(pending_config.keys()):
                col1, col2 = st.columns([8, 2]) # 비율 조정
                col1.markdown(f"- **{tool_name}**")
                if col2.button("삭제", key=f"delete_{tool_name}"):
                    del st.session_state.pending_mcp_config[tool_name]
                    st.success(
                        f"{tool_name} 도구가 삭제되었습니다. 적용하려면 '설정 적용하기' 버튼을 눌러주세요."
                    )
                    
                    
    st.divider() # 구분선 추가
    
# 시스템 정보 및 작업 버튼 섹션
with st.sidebar:
    st.subheader("시스템 정보")
    st.write(f"MCP 도구 수: {st.session_state.get('tool_count', '초기화 중...')}")
    selected_model_name = st.session_state.selected_model
    st.write(f"현재 모델: {selected_model_name}")
    
    if st.button(
        "설정 적용하기",
        key="apply_button",
        type="primary",
        use_container_width=True,
    ):
        # 적용중 메시지 표시
        apply_status = st.empty()
        with apply_status.container():
            st.warning("변경사항을 적용하고 있습니다. 잠시만 기다려 주세요.")
            progress_bar = st.progress(0)
            
            # 설정 저장
            st.session_state.mcp_config_text = json.dumps(
                st.session_state.pending_mcp_config, indent=2, ensure_ascii=False
            )
            
            # config.json 파일에 저장
            save_result = save_config_to_json(st.session_state.pending_mcp_config)
            if not save_result:
                st.error("설정 파일 저장에 실패했습니다.")
            
            progress_bar.progress(15)
            
            # 세션 초기화 준비
            st.session_state.session_initialized = False
            st.session_state.agent = None
            
            # 진행 상태 업데이트
            progress_bar.progress(30)
            
            # 초기화 실행 
            success = st.session_state.event_loop.run_until_complete(
                initialize_session(st.session_state.pending_mcp_config)
            )
            
            # 진행 상태 업데이트
            progress_bar.progress(100)
            
            if success:
                st.success("변경사항이 적용되었습니다.")
                # 도구 추가 expander 접기
                if "mcp_tools_expander" in st.session_state:
                    st.session_state.mcp_tools_expander = False
                st.rerun()
            else:
                st.error("변경사항 적용에 실패했습니다.")
                
        # 페이지 새로고침
        st.rerun()
    
    st.subheader("작업")
        
    if st.button("대화 초기화", use_container_width=True, type="primary"):
        st.session_state.thread_id = random_uuid()
        st.session_state.history = []
        st.success("대화가 초기화되었습니다.")
        st.rerun()
        
    if use_login and st.session_state.authenticated:
        st.divider()
        if st.button("로그아웃", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.success("로그아웃 되었습니다.")
            st.rerun()
                
# --- 기본 세션 초기화 (초기화되지 않은 경우) ---
if not st.session_state.session_initialized:
    st.info(
        "MCP 서버와 에이전트가 초기화되지 않았습니다. 왼쪽 사이드바의 '설정 적용하기' 버튼을 클릭하여 초기화해주세요."
    )
    
# --- 대화 기록 처리 ---
print_message()

# --- 사용자 입력 및 처리 ---
user_query = st.chat_input("질문을 입력하세요")
if user_query:
    if st.session_state.session_initialized:
        st.chat_message("user", avatar="🧑‍💻").markdown(user_query)
        with st.chat_message("assistant", avatar="🤖"):
            tool_placeholder = st.empty()
            text_placeholder = st.empty()
            resp, final_text, final_tool = (
                st.session_state.event_loop.run_until_complete(
                    # process_query의 return은 response, final_text, final_tool
                    process_query(
                        user_query,
                        text_placeholder,
                        tool_placeholder,
                        st.session_state.timeout_seconds
                    )
                )
            )
            
        if "error" in resp:
            st.error(resp["error"])
        else:
            st.session_state.history.append({"role": "user", "content": user_query})
            st.session_state.history.append({"role": "assistant", "content": final_text})
            if final_tool.strip():
                st.session_state.history.append(
                    {"role": "assistant_tool", "content": final_tool}
                )
            st.rerun()
            
    else:
        st.warning(
            "MCP 서버와 에이전트가 초기화되지 않았습니다. 왼쪽 사이드바의 '설정 적용하기' 버튼을 클릭하여 초기화해주세요."
            )
# 궁금한점?
# mesasge_content에 invalid_tool_calls랑 message_chunk["type"] == "tool_use": 
# tool_calls 속성이 있는 경우 처리 하는 부분이 있는데 왜 그런지 궁금합니다. 따로 설정해준게 없는데, 어디에 있는거지?
# isinstance: 객체의 타입을 확인하는 함수
# hasattr 속성 존재 판별하는 함수
# json.dump
# .strip(): 문자열 양쪽의 공백과 특수문자 제거

