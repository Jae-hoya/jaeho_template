from dotenv import load_dotenv
load_dotenv()

# node에서 받지 않은것들: retriever, rag_chain, llm(general_answer_node)

from retrievers import create_qdrant_retriever, create_compression_retriever
from rag import create_rag_chain
from state import GraphState
from nodes import *

from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

import streamlit as st

def create_graph():
    retriever = create_qdrant_retriever()
    rag_chain = create_rag_chain()

    # 그래프 상태 초기화
    workflow = StateGraph(GraphState)

    # 노드 정의
    workflow.add_node("query_expand", QueryRewriteNode())  # 질문 재작성
    workflow.add_node("query_rewrite", QueryRewriteNode())  # 질문 재작성
    workflow.add_node("web_search", WebSearchNode())  # 웹 검색
    workflow.add_node("retrieve", RetrieveNode(retriever))  # 문서 검색
    workflow.add_node("grade_documents", FilteringDocumentsNode())  # 문서 평가
    workflow.add_node(
        "general_answer", GeneralAnswerNode(ChatOpenAI(model="gpt-4.1-mini", temperature=0))
    )  # 일반 답변 생성
    workflow.add_node("rag_answer", RagAnswerNode(rag_chain))  # RAG 답변 생성

    # 엣지 추가
    workflow.add_conditional_edges(
        START,
        RouteQuestionNode(),
        {
            "query_expansion": "query_expand",  # 웹 검색으로 라우팅
            "general_answer": "general_answer",  # 벡터스토어로 라우팅
        },
    )

    workflow.add_edge("query_expand", "retrieve")
    workflow.add_edge("retrieve", "grade_documents")

    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_web_search_node,
        {
            "web_search": "web_search",  # 웹 검색 필요
            "rag_answer": "rag_answer",  # RAG 답변 생성 가능
        },
    )

    workflow.add_edge("query_rewrite", "rag_answer")

    workflow.add_conditional_edges(
        "rag_answer",
        AnswerGroundednessCheckNode(),
        {
            "relevant": END,
            "not relevant": "web_search",
            "not grounded": "query_rewrite",
        },
    )

    workflow.add_edge("web_search", "rag_answer")


    # 그래프 컴파일
    app = workflow.compile(checkpointer=MemorySaver())
    return app

from langchain_core.runnables import RunnableConfig
from langgraph.errors import GraphRecursionError

def stream_graph(app, query, streamlit_container, thread_id):
    config = RunnableConfig(recursion_limit=30, configurable={"thread_id": thread_id})
    
    inputs = GraphState(question=query)
    
    # 노드와 작성하고 싶은 글
    actions = {
        "retrieve": "문서를 조회하는 중입니다.",
        "grade_documents": "문서를 평가하는 중입니다.",
        "rag_answer": "문서를 기반으로 답변을 생성하는 중입니다.",
        "general_answer": "일반 답변을 하는 중입니다.",
        "web_search": "웹 검색을 하는 중입니다.",
        }
    
    try:
        #streamlit_container
        with streamlit_container.status(
            "생각하는 중입니다...", expanded=True
        ) as status:
            for output in app.stream(inputs, config=config):
                
                for key, value in output.items():
                    if key in actions:
                        st.write(actions[key])
                        
                status.update(label="답변 중...", state="complete", expanded=False)
    except GraphRecursionError as e:
        print(f"Recursion limit reached: {e}")
    return app.get_state(config={"configurable": {"thread_id": thread_id}}).values
    
