# rag_minimal.py
from operator import itemgetter
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
from langchain_openai import ChatOpenAI  # 원하시면 다른 모델로 교체 가능
from langchain_core.prompts import load_prompt
from pathlib import Path


def _format_docs(docs: List[Document]) -> str:
    # 필요 시 더 간단히: return "\n\n".join(d.page_content for d in docs)
    return "\n\n".join(
        f"[{i+1}] {d.metadata.get('source', '')}\n{d.page_content}"
        for i, d in enumerate(docs)
    )

def chat_history_rag(retriever, *, model=None, prompt_name="rag-prompt-with-chat-history"):
    """
    사용법:
      chain = rag(retriever)
      # chain.invoke({"question": "질문", "chat_history": []})
    """
    model = model or ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)
    prompt = load_prompt(f"prompts/{prompt_name}.yaml")
    # prompt = load_prompt(f"RAG/prompts/{prompt_name}.yaml")
    # prompt = load_prompt(f"prompts/{prompt_name}.yaml")  # chat_history, context, question이 있다.  

    
    retrieve_then_format = (
        RunnableLambda(lambda x: retriever.invoke(x["question"]))  # List[Document]
        | _format_docs                                                  # -> str
    )

    chain = (
        {
            "question": itemgetter("question"),
            "chat_history": itemgetter("chat_history"),
            "context": retrieve_then_format,
        }
        | prompt
        | model
        | StrOutputParser()
    )
    return chain


def rag(retriever, *, model=None, prompt_name="rag-prompt"):
    """
    사용법:
      chain = rag(retriever)
      # chain.invoke({"question": "질문", "chat_history": []})
    """
    model = model or ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)
    prompt = load_prompt(f"prompts/{prompt_name}.yaml")
    # prompt = load_prompt(f"RAG/prompts/{prompt_name}.yaml")
    # prompt = load_prompt(f"prompts/{prompt_name}.yaml")  # chat_history, context, question이 있다.  

    
    retrieve_then_format = (
        RunnableLambda(lambda x: retriever.invoke(x["question"]))  # List[Document]
        | _format_docs                                                  # -> str
    )

    chain = (
        {
            "question": itemgetter("question"),
            "context": retrieve_then_format,
        }
        | prompt
        | model
        | StrOutputParser()
    )
    return chain