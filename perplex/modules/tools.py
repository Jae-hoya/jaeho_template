from typing import Any, List
# from base import BaseTool
from langchain_tavily.tavily_search import TavilySearch

# modules/tools.py
from typing import Optional, List
from langchain_tavily import TavilySearch

def web_search_tool(
    *,
    topic: str = "general",
    max_results: int = 3,
    include_answer: bool = False,
    include_raw_content: Optional[str | bool] = None,  # "markdown" | "text" | False | None
    include_images: bool = False,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None,
) -> TavilySearch:
    tool = TavilySearch(
        topic=topic,
        max_results=max_results,
        include_answer=include_answer,
        include_raw_content=include_raw_content,
        include_images=include_images,
        include_domains=include_domains or None,   # [] 대신 None 전달
        exclude_domains=exclude_domains or None,
    )
    tool.name = "web_search"
    tool.description = "Use this tool to search on the web"
    return tool


# def web_search_tool(question):
#     web_search = TavilySearch()
#     web_search.name = "web search"
#     web_search.description = "Use this tool to search on the web"
    
#     response = web_search.invoke({"query": question})
    
#     return response


# from typing import Any
# from langchain_tavily.tavily_search import TavilySearch

# class WebSearchTool:
#     """TavilySearch를 래핑한 단순 클래스"""

#     def __init__(self):
#         self.tool = TavilySearch()
#         self.tool.name = "web search"
#         self.tool.description = "Use this tool to search on the web"

#     def __call__(self, question: str) -> Any:
#         return self.tool.invoke({"query": question})
