"""
Agentic RAG 시스템의 에이전트 정의
각 에이전트를 생성하는 함수들을 정의합니다.
"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from base import make_system_prompt
from tools import create_retriever_tool_wrapper, create_python_repl_tool, create_tavily_search_tool


def create_retriever_agent(retriever, llm=None):
    """
    Retriever 에이전트 생성
    
    Args:
        retriever: 검색기 객체
        llm: 언어 모델 (기본값: gpt-4.1-mini)
        
    Returns:
        retriever_agent: Retriever 에이전트
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    
    retriever_tool = create_retriever_tool_wrapper(retriever)
    tools = [retriever_tool]
    
    return create_react_agent(
        llm, 
        tools=tools,
        state_modifier=make_system_prompt(
            """You are a specialized research agent focused on retrieving and analyzing information from SPRI AI Brief documents.
            
            Your primary responsibilities:
            1. Search through SPRI AI Brief PDF documents using the retriever tool
            2. Find relevant, authoritative information about AI trends, technologies, and industry developments
            3. Provide detailed, well-sourced answers based on the retrieved documents
            4. Always cite your sources and provide context for the information you share
            
            You work collaboratively with other agents:
            - Researcher agent: Handles web-based research and current information
            - Coder agent: Creates visualizations and charts based on your findings
            
            When retrieving information:
            - Use specific, targeted search queries
            - Look for the most relevant and recent information
            - Provide comprehensive answers with proper context
            - Always mention the source of your information
            
            Remember: You can ONLY use the retriever tool to search SPRI documents. For other types of research, coordinate with the Researcher agent."""
        ), 
        checkpointer=MemorySaver()
    )


def create_research_agent(llm=None):
    """
    Research 에이전트 생성 (TavilySearch 사용)
    
    Args:
        llm: 언어 모델 (기본값: gpt-4.1-mini)
        
    Returns:
        research_agent: Research 에이전트
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    
    tavily_tool = create_tavily_search_tool(max_results=5)
    
    return create_react_agent(
        llm, 
        tools=[tavily_tool],
        state_modifier=make_system_prompt(
            "You can only do research. You are working with a chart generator colleague."
        ),
        checkpointer=MemorySaver()
    )


def create_coder_agent(llm=None):
    """
    Coder 에이전트 생성 (Python REPL 사용)
    
    Args:
        llm: 언어 모델 (기본값: gpt-4.1-mini)
        
    Returns:
        coder_agent: Coder 에이전트
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    
    code_system_prompt = """
Be sure to use the following font in your code for visualization.

##### 폰트 설정 #####
import platform

# OS 판단
current_os = platform.system()

if current_os == "Windows":
    # Windows 환경 폰트 설정
    font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트 경로
    fontprop = fm.FontProperties(fname=font_path, size=12)
    plt.rc("font", family=fontprop.get_name())
elif current_os == "Darwin":  # macOS
    # Mac 환경 폰트 설정
    plt.rcParams["font.family"] = "AppleGothic"
else:  # Linux 등 기타 OS
    # 기본 한글 폰트 설정 시도
    try:
        plt.rcParams["font.family"] = "NanumGothic"
    except:
        print("한글 폰트를 찾을 수 없습니다. 시스템 기본 폰트를 사용합니다.")

##### 마이너스 폰트 깨짐 방지 #####
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 폰트 깨짐 방지
"""
    
    python_repl_tool = create_python_repl_tool()
    
    return create_react_agent(
        llm,
        [python_repl_tool],
        state_modifier=code_system_prompt,
        checkpointer=MemorySaver()
    )


def create_general_agent(llm=None):
    """
    General 에이전트 생성 (일반 대화용)
    
    Args:
        llm: 언어 모델 (기본값: gpt-4.1-mini)
        
    Returns:
        general_agent: General 에이전트
    """
    if llm is None:
        llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
    
    return create_react_agent(
        llm, 
        tools=[],  # 도구 없음 (일반적인 대화만)
        state_modifier=make_system_prompt(
            "You are a helpful general assistant. You can answer general questions, "
            "have conversations, and provide information. You work with other specialized agents: "
            "- Retriever agent: For searching SPRI documents "
            "- Researcher agent: For web research "
            "- Coder agent: For creating charts and visualizations "
            "If you need specialized information, coordinate with the appropriate agent."
        ),
        checkpointer=MemorySaver()
    )
