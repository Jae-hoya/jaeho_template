from dotenv import load_dotenv
load_dotenv()

# node에서 받지 않은것들: retriever, rag_chain, llm(general_answer_node)
from RAG.retriever import QdrantRetrieverFactory
from RAG.rag import rag
from nodes import *
from states import GraphState

qs = QdrantRetrieverFactory()

retriever = qs.retriever(collection_name="RAG_Template")

from langgraph.graph import END, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI

import streamlit as st

def create_graph():
    retriever = qs.retriever(collection_name="RAG_Template")
    chain = rag(retriever)

    # 그래프 상태 초기화
    workflow = StateGraph(GraphState)

    workflow.add_node("retrieve", RetrieveNode(retriever))
    workflow.add_node("rag_answer", LLMAnswerNode(chain))

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "rag_answer")
    workflow.add_edge("rag_answer", END)

    memory = MemorySaver()

    app = workflow.compile(checkpointer=memory)

    return app

from langchain_core.runnables import RunnableConfig
from langgraph.errors import GraphRecursionError

def stream_graph(app, query, streamlit_container, thread_id, chat_history=None):
    config = RunnableConfig(recursion_limit=30, configurable={"thread_id": thread_id})
    
    # chat_history가 None이면 빈 리스트로 초기화
    if chat_history is None:
        chat_history = []
    
    inputs = GraphState(
        question=query,
        chat_history=chat_history,
        thread_id=thread_id
    )
    
    # 노드와 작성하고 싶은 글
    actions = {
        "retrieve": "문서를 조회하는 중입니다.",
        "rag_answer": "문서를 기반으로 답변을 생성하는 중입니다.",
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
    
