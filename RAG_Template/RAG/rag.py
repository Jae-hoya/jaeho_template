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

def rag(retriever, *, model=None, prompt_name="rag-prompt"):
    """
    사용법:
      chain = rag(retriever)
      # chain.invoke({"question": "질문", "chat_history": []})
    """
    model = model or ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)
    prompt = load_prompt(f"RAG/prompts/{prompt_name}.yaml")
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

def chat_history_rag(retriever, *, model=None, prompt_name="rag-prompt-with-chat-history"):
    """
    사용법:
      chain = rag(retriever)
      # chain.invoke({"question": "질문", "chat_history": []})
    """
    model = model or ChatOpenAI(model_name="gpt-4.1-mini", temperature=0)
    prompt = load_prompt(f"RAG/prompts/{prompt_name}.yaml")
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

# 편의 함수(선택): 함수형으로 바로 호출하고 싶을 때
# def ask(qs_retriever, question: str, chat_history: Optional[list] = None, **kwargs) -> str:
#     chain = rag(qs_retriever, **kwargs)
#     return chain.invoke({"question": question, "chat_history": chat_history or []})


# # rag_minimal.py (수정 버전)
# from operator import itemgetter
# from typing import List, Optional
# from langchain_core.documents import Document
# from langchain_core.runnables import RunnableLambda
# from langchain_core.output_parsers import StrOutputParser
# from langchain import hub
# from langchain_openai import ChatOpenAI

# def _format_docs(docs: List[Document]) -> str:
#     return "\n\n".join(
#         f"[{i+1}] {d.metadata.get('source', '')}\n{d.page_content}"
#         for i, d in enumerate(docs)
#     )

# def _ensure_retriever(obj, k: int):
#     # 이미 retriever이면 그대로 사용
#     if hasattr(obj, "invoke"):  # VectorStoreRetriever는 Runnable(=invoke 보유)
#         return obj
#     # VectorStore이면 retriever로 변환
#     if hasattr(obj, "as_retriever"):
#         return obj.as_retriever(search_kwargs={"k": k})
#     raise TypeError("qs_retriever 인자로 retriever 또는 vectorstore를 전달하세요.")

# def rag(qs_retriever_or_store, *, model=None, prompt=None, k: int = 5):
#     model = model or ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
#     prompt = prompt or hub.pull("teddynote/rag-prompt-chat-history")

#     retriever = _ensure_retriever(qs_retriever_or_store, k=k)

#     retrieve_then_format = (
#         RunnableLambda(lambda x: retriever.invoke(x["question"]))  # -> List[Document]
#         | _format_docs                                               # -> str
#     )

#     chain = (
#         {
#             "question": itemgetter("question"),
#             "chat_history": itemgetter("chat_history"),
#             "context": retrieve_then_format,
#         }
#         | prompt
#         | model
#         | StrOutputParser()
#     )
#     return chain

