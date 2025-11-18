# 함수로 만들어서 사용

from pydantic import BaseModel, Field
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser



# 라우트 쿼리 체인
class RouteQuery(BaseModel):
    
    binary_score: Literal["yes", "no"] = Field(
        ...,
        description="Given a user question, determine if it needs to be retrieved from vectorstore or not. Return 'yes' if it needs to be retrieved from vectorstore, otherwise return 'no'.",
    )

def create_question_router_chain():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    structured_llm_router = llm.with_structured_output(RouteQuery)

    system = """
    You are an expert at routing a user question. 
    The vectorstore contains documents retrieved using LangChain / LangGraph.
    The vectorstore contains documents related to RAG(Retrieval Augmented Generation) source code and documentation.
    Return 'yes' if the question is related to the source code or documentation, otherwise return 'no'.
    If you can't determine if the question is related to the source code or documentation, return 'yes'.
    If you don't know the answer, return 'yes'.
    """

    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "{question}")
        ]
    )

    question_router = route_prompt | structured_llm_router
    return question_router


# 질문 재작성 체인
def create_question_rewrite_chain():
    llm = ChatOpenAI(model="gpt-4.1-mini")

    system = """
    You a question re-writer that converts an input question to a better version that is optimized for CODE SEARCH(github repository).

    Look at the input and try to reason about the underlying semantic intent / meaning.

    Base Code Repository: 

    https://github.com/langchain-ai/langgraph

    Output should be in English."""

    re_write_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Here is the initial question: \n\n {question} \n Formulate an improved question."),
        ]
    )

    question_rewriter = re_write_prompt | llm | StrOutputParser()
    return question_rewriter

# 문서 관령성 평가 체인
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""
    
    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )
    
def create_retrieval_grader_chain():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)

    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    system = """You are a grader assessing relevance of a retrieved document to a user question. \n 
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
        It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""

    grade_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Retrieved document: \n\n {document} \n\n User question: {question}")
        ]
    )

    retrieval_grader = grade_prompt | structured_llm_grader
    return retrieval_grader

# 답변의 환각 여부 평가 체인
class AnswerGroundedness(BaseModel):
    """Binary score for answer groundedness"""
    
    binary_score: str = Field(
        description="Answer is groundedness in the facts(given context), 'yes' or 'no'"
    )

def create_groundedness_checker_chain():
    llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)    

    structured_llm_grader = llm.with_structured_output(AnswerGroundedness)

    system = """
    You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n 
    Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts.
    """

    groundedness_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "Set of facts: \n\n {documents} \n\n LLM generation: {generation}"),
        ]
    )

    # 답변의 환각 여부 평가기 생성
    groundedness_checker = groundedness_prompt | structured_llm_grader
    return groundedness_checker

class GradeAnswer(BaseModel):
    """Binary scoring to evaluate the appropriateness of answers to questions"""

    binary_score: str = Field(
        description="Indicate 'yes' or 'no' whether the answer solves the question"
    )


def create_relevant_answer_checker_chain():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm_grader = llm.with_structured_output(GradeAnswer)

    # 프롬프트 설정
    system = """You are a grader assessing whether an answer addresses / resolves a question \n 
        Give a binary score 'yes' or 'no'. Yes' means that the answer resolves the question."""
    relevant_answer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "User question: \n\n {question} \n\n LLM generation: {generation}"),
        ]
    )

    # 프롬프트 템플릿과 구조화된 LLM 평가기를 결합하여 답변 평가기 생성
    relevant_answer_checker = relevant_answer_prompt | structured_llm_grader
    return relevant_answer_checker