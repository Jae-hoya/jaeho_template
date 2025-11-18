from abc import ABC, abstractmethod
from states import GraphState

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
    
    
class RetrieveNode(BaseNode):
    def __init__(self, retriever, **kwargs):
        super().__init__(**kwargs)
        self.name = "RetrieveNode"
        self.retriever = retriever

    def execute(self, state: GraphState) -> GraphState:
        question = state["question"]
        retrieved_docs = self.retriever.invoke(question)
        
        return {"context": retrieved_docs}

class LLMAnswerNode(BaseNode):
    def __init__(self, chain, **kwargs):
        super().__init__(**kwargs)
        self.name = "LLMAnswerNode"
        self.chain = chain

    def execute(self, state: GraphState) -> GraphState:
        from langchain_teddynote.messages import messages_to_history
        
        question = state["question"]
        context = state["context"]
        
        # 이전 대화 기록을 포함하여 RAG 체인 호출
        response = self.chain.invoke({
            "question": question, 
            "context": context,
            "chat_history": messages_to_history(state["messages"]), # 이전 내용을 기억해서 대화하는 멀티턴 기능을 위함.
        })
        
        return GraphState(
            answer=response, messages=[("user", question), ("assistant", response)]
        )
  
        
       
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
