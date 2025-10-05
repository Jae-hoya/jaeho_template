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
        }
    }
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
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
            await st.session_state.mcp_client.__aexit__(None, None, None)
            st.session_state.mcp_client = None
        except Exception as e:
            import traceback
            st.warning(f"MCP 클라이언트 종료 중 오류: {str(e)}")
            
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
            st.chat_message("user", avater="👤").markdown(message["content"])
            i += 1
        elif message["role"] == "assistant":
            with st.chat_message("assistant", avater="🤖"):
                st.markdown(message["content"])
                
                # 다음 메시지가 도구 호출 정보인지 확인
                if (
                    i + 1 < len(st.session_state.history)
                    and st.session_state.history[i+1]["role"] == "asstant_tool"
                ):
                    with st.exapnder("🔧 도구 호출 정보", expanded=False): # 도구 호출 정보를 컨테이너에 표시
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
                    "도구호출 정보: 유효하지 않음", expander=True
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
                    "도구호출 정보", expander=True
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
                    "도구호출 정보", expander=True
                ):
                    st.markdown("".join(accumulated_tool))
                    
        # 도구 메시지인 경우 처리 (도구의 응답)
        elif isinstance(message_content, ToolMessage):
            accumulated_tool.append(
                "\n```json\n" + str(message_content.content) + "\n```\n"
            )
            with tool_placeholder.expander(
                "도구호출 정보", expander=True
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
                                  {"message": [HumanMessage(content=query)]},
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
            
        client = MultiServerMCPClient(mcp_config)
        await client.__aenter__()
        tools = client.get_tools()
        
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
            "⚠️ 모델이 변경되었습니다. '설정 적용하기' 버튼을 눌러 변경사항을 적용하세요."
        )
        
        
# 궁금한점?
# mesasge_content에 invalid_tool_calls랑 message_chunk["type"] == "tool_use": 
# tool_calls 속성이 있는 경우 처리 하는 부분이 있는데 왜 그런지 궁금합니다. 따로 설정해준게 없는데, 어디에 있는거지?
# isinstance: 객체의 타입을 확인하는 함수
# hasattr 속성 존재 판별하는 함수
# json.dump

