# rag_minimal.py
from operator import itemgetter
from typing import List
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import load_prompt
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def _format_docs(docs: List[Document]) -> str:
    return "\n\n".join(
        f"[{i+1}] {d.metadata.get('source', '')}\n{d.page_content}"
        for i, d in enumerate(docs)
    )

def rag(retriever, *, model=None, prompt_name="rag-prompt"):
    """
    사용법:
      chain = rag(retriever)
      chain.invoke({"question": "질문", "chat_history": []})
    """
    model = model or ChatOpenAI(model_name="gpt-4o-mini", temperature=0)
    system_prompt = load_prompt(f"RAG/prompts/{prompt_name}.yaml")
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt.template),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
        ("system", "다음은 검색된 문서입니다:\n{context}"),
    ])

    # 검색 → 포맷
    retrieve_then_format = (
        RunnableLambda(lambda x: retriever.invoke(x["question"]))
        | _format_docs
    )

    # 체인 본체
    chain = (
        {
            "question": itemgetter("question"),
            "context": retrieve_then_format,
            "chat_history": itemgetter("chat_history"),
        }
        | prompt
        | model
        | StrOutputParser()
    )
    
    return chain





