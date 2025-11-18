from typing import Annotated, TypedDict,Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

class GraphState(TypedDict):
    question: Annotated[str, "Question"]
    context: Annotated[str, "Context"]
    answer: Annotated[str, "Answer"]
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    
