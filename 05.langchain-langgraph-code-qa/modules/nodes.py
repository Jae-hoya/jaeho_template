# chain, tools, states를 받아서 사용.

from abc import ABC, abstractmethod
from chains import (
    create_question_router_chain,
    create_question_rewrite_chain,
    create_retrieval_grader_chain,
    create_groundedness_checker_chain,
    create_relevant_answer_checker_chain
)

from tools import create_web_search_tool
from state import GraphState

from langchain_core.documents import Document

# 함수로 만들어서 써도 되는데, 랭체인의 체인은 외부에서 참조를 하는데, 의존성에서 문제가 생길 수 있다.
# 따라서 기준이 되는 베이스 클래스인 absteact 클래스를 상속을 받아서 사용한다(자식 클래스에서 구현해야 하는 메서드).
# init은 기본 셋업이며, 필요한 chain이 있다면, 체인을 할당하는 용도로 init함수를 사용한다.
# 함수 내용들은 execute에 들어간다. 그래야 함수호출 하듯이 사용할 수 있다(__call__을 통해서 execute를 호출).

# 예시
### 예시 ###
class BaseNode(ABC):
    def __init__(self, **kwargs):
        self.name = "BaseNode"
        self.verbose = False
        if "verbose" in kwargs:
            self.verbose = kwargs["verbose"]

    # 자식 클래스에서 구현해야하는 abstract_method
    @abstractmethod
    def execute(self, state: GraphState) -> GraphState:
        pass

    def logging(self, method_name, **kwargs):
        if self.verbose:
            print(f"[{self.name}] {method_name}")
            for key, value in kwargs.items():
                print(f"{key}: {value}")

    def __call__(self, state: GraphState):
        return self.execute(state)
##########################################################
# ABC를 BaseNode로 바꿔준다.(상속을 받으니까!)
# init과 execute만 사용하는데, 이름은 바꿔주고, super를 사용해줘야한다(상속 받으니까!).
# self로 init에 필요한것을 정의해주고, execute에도 self를 추가 해줘야 한다.
# execute노드를 자식클래스에서 작성할때는, @abstractmethod를 지워주고 사용한다.

# 상태값이 들어가는 값들을 GraphState로 return해줘야 한다.

# 하다보면, 결국에는 답변 생성노드에만 init에 새로운 인자를 넣는다. ex) llm, rag_chain, retriever 

# ```python
# class NodeName(BaseNode):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.name = "BaseNode"
#
#     def execute(self, state: GraphState) -> GraphState:
# ```
##########################################################




# 라우트 쿼리 노드
class RouteQuestionNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "RouteQuestionNode"
        self.question_router = create_question_router_chain()

    # 자식 클래스에서 구현해야하는 abstract_method
    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        evaluation = self.question_router.invoke({"question": question})
        
        if evaluation.binary_score == "yes":
            return "query_expansion"
        else: 
            return "general_answer"    


# 질문 재작성노드
class QueryRewriteNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "QueryRewriteNode"
        self.question_rewriter = create_question_rewrite_chain()

    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        
        better_question = self.question_rewriter.invoke({"question": question})
        
        return GraphState(question=better_question)
        
   
# 문서 검색 노드: init에 retriever가 추가! 
class RetrieveNode(BaseNode):
    def __init__(self, retriever, **kwargs):
        super().__init__(**kwargs)
        self.name = "RetrieveNode"
        self.retriever = retriever

    # 자식 클래스에서 구현해야하는 abstract_method
    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        
        # documents = compression_retriever.invoke(question)
        documents = self.retriever.invoke(question)
        return GraphState(documents=documents)
    
# 일반 답변 생성 노드: init에 llm이 추가!
class GeneralAnswerNode(BaseNode):
    def __init__(self, llm, **kwargs):
        super().__init__(**kwargs)
        self.name = "GeneralAnswerNode"
        self.llm = llm

    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        answer = self.llm.invoke(question)
        return GraphState(generation=answer.content) # llm 답변에서 content를 안하면 다른 상태값들도 같이온다.


# RAG 답변 생성노드: init에 rag_chain이 추가!
class RagAnswerNode(BaseNode):
    def __init__(self, rag_chain, **kwargs):
        super().__init__(**kwargs)
        self.name = "RagAnswerNode"
        self.rag_chain = rag_chain

    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        documents = state["documents"]
        answer = self.rag_chain.invoke({"context": documents, "question": question})
        return GraphState(generation=answer)

    
class FilteringDocumentsNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "FilteringDocumentsNode"
        self.retrieval_grader = create_retrieval_grader_chain()


    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        documents = state["documents"]
        
        filtered_docs = []
        
        for d in documents:
            score = self.retrieval_grader.invoke(
                {"question": question, "document": d.page_content}
            )
            grade = score.binary_score
            if grade == "yes":
                filtered_docs.append(d)
            else:
                continue
            
        return GraphState(documents=filtered_docs)

# class WebSearchNode(BaseNode):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.name = "WebSearchNode"
#         self.tavily_search_tool = create_web_search_tool()

#     # 자식 클래스에서 구현해야하는 abstract_method
#     def execute(self, state: GraphState) -> GraphState:
#         question = state["question"]
        
#         web_results = self.tavily_search_tool.invoke({"query": question})
#         web_results_docs = [
#             Document(
#                 page_content=web_result["content"],
#                 metadata={"source": web_result["url"]},
#             )
#             for web_result in web_results
#         ]
#         return GraphState(documents=web_results_docs)

class WebSearchNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "WebSearchNode"
        self.web_search_tool = create_web_search_tool()

    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        res = self.web_search_tool.invoke({"query": question})  # dict( results=[...] )
        items = res.get("results", [])                          # list[dict]

        web_results_docs = [
            Document(
                page_content=item.get("content", ""),
                metadata={"source": item.get("url", ""), "title": item.get("title", "")},
            )
            for item in items
            if isinstance(item, dict)
        ]
        return GraphState(documents=web_results_docs)


class AnswerGroundednessCheckNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "AnswerGroundednessCheckNode"
        self.groundedness_checker = create_groundedness_checker_chain()
        self.relevant_answer_checker = create_relevant_answer_checker_chain()

    # 자식 클래스에서 구현해야하는 abstract_method
    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]
        
        # Groundedness 평가: 검색과 답변 관련성 비교
        score = self.groundedness_checker.invoke(
            {"documents": documents, "generation": generation}
        )
        
        grade = score.binary_score
        
        # 만약 검색과 답변이 관련이 있다면,
        # Groundedness 평가 결과에 따른 처리: 질문과 답변 관련성 비교
        if grade == "yes":
            score = self.relevant_answer_checker.invoke(
                {"question": question, "generation": generation}
            )
            
            grade = score.binary_score
            
            # 관련성 평가 결과에 따른 처리
            if grade == "yes":
                return "relevant"
            else:
                return "not relevant"
            
        else:
            return "not grounded"
    
# class화 필요없음! 겹칠 이유가 없으니까
def decide_to_web_search_node(state):
    filtered_docs = state["documents"]
    print(len(filtered_docs))
    
    if len(filtered_docs) < 8:
        return "web_search"
    else:
        return "rag_answer"






