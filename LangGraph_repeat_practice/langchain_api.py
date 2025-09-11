from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

import re

import matplotlib.pyplot as plt
import seaborn as sns

from langchain import hub
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain.tools import tool
from langchain.tools.retriever import create_retriever_tool

from langchain_community.vectorstores import FAISS

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.utils.function_calling import convert_to_openai_function

from langgraph.graph import START, MessageGraph, END, StateGraph

embedding = OllamaEmbeddings(model="bge-m3")
vector_store = FAISS.load_local("FAISS_SPRI_202312", embeddings=embedding, allow_dangerous_deserialization=True)
retriever = vector_store.as_retriever()

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = hub.pull("rlm/rag-prompt")

chain = RunnableParallel({"context": retriever, "question": RunnablePassthrough})\
    | prompt \
    | llm \
    | StrOutputParser()