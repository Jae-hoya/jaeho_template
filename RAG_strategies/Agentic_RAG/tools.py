"""
Agentic RAG 시스템의 도구 정의
각 에이전트에서 사용할 도구들을 생성하는 함수들을 정의합니다.
"""
from typing import Annotated
from langchain_core.tools import tool
from langchain_core.tools.retriever import create_retriever_tool
from langchain.prompts import PromptTemplate
from langchain_tavily import TavilySearch
from langchain_experimental.tools import PythonREPLTool


def create_retriever_tool_wrapper(retriever, name="retriever", 
                                  description="Search and return information about SPRI AI Brief PDF file. It contains useful information on recent AI trends. The document is published on Dec 2025"):
    """
    Retriever를 도구로 변환하는 래퍼 함수
    
    Args:
        retriever: 검색기 객체
        name: 도구 이름
        description: 도구 설명
        
    Returns:
        retriever_tool: 도구화된 retriever
    """
    return create_retriever_tool(
        retriever=retriever, 
        name=name,
        description=description,
        document_prompt=PromptTemplate.from_template(
            "<document><content>{page_content}</content><metadata><source>{source}</source><page></page></metadata></document>"
        )
    )


def create_python_repl_tool():
    """
    Python REPL 도구 생성
    
    Returns:
        python_repl_tool: Python 코드 실행 도구
    """
    python_repl = PythonREPLTool()

    @tool
    def python_repl_tool(
        code: Annotated[str, "The python code to execute to generate your chart."],
    ):
        """Use this to execute python code. If you want to see the output of a value,
        you should print it out with `print(...)`. This is visible to the user."""
        try:
            # 주어진 코드를 Python REPL에서 실행하고 결과 반환
            result = python_repl.run(code)
        except BaseException as e:
            return f"Failed to execute code. Error: {repr(e)}"
        # 실행 성공 시 결과와 함께 성공 메시지 반환
        result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
        return (
            result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
        )
    
    return python_repl_tool


def create_tavily_search_tool(max_results=5):
    """
    TavilySearch 도구 생성
    
    Args:
        max_results: 최대 검색 결과 수 (기본값: 5)
        
    Returns:
        tavily_tool: TavilySearch 도구
    """
    return TavilySearch(max_results=max_results)
