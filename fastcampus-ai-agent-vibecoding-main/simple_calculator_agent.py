"""
Simple Calculator Agent - LangGraph 첫 번째 실습
Phase 1: 기초 설정 및 학습
"""

from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import os
from dotenv import load_dotenv

load_dotenv()

# State 정의
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# Tool 정의
def calculator(operation: Literal["add", "subtract", "multiply", "divide"], a: float, b: float) -> float:
    """간단한 계산기 도구

    Args:
        operation: 수행할 연산 (add, subtract, multiply, divide)
        a: 첫 번째 숫자
        b: 두 번째 숫자

    Returns:
        계산 결과
    """
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero"
        return a / b
    else:
        return "Error: Unknown operation"

# LLM 설정 (Tool 바인딩)
model = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    temperature=0
)

tools = [calculator]
model_with_tools = model.bind_tools(tools)

# Agent 노드 정의
def call_model(state: AgentState) -> dict:
    """LLM을 호출하여 응답 생성"""
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", END]:
    """Tool을 호출할지 종료할지 결정"""
    messages = state["messages"]
    last_message = messages[-1]

    # Tool call이 있으면 tools 노드로, 없으면 종료
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

def call_tools(state: AgentState) -> dict:
    """Tool 실행"""
    messages = state["messages"]
    last_message = messages[-1]

    tool_messages = []
    for tool_call in last_message.tool_calls:
        # calculator tool 실행
        result = calculator(
            operation=tool_call["args"]["operation"],
            a=tool_call["args"]["a"],
            b=tool_call["args"]["b"]
        )

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": tool_messages}

# Graph 구축
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)

# Edge 추가
workflow.add_edge(START, "agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")

# Graph 컴파일
app = workflow.compile()

# 실행 함수
def run_agent(question: str):
    """Agent 실행 및 결과 출력"""
    print(f"\n{'='*60}")
    print(f"질문: {question}")
    print(f"{'='*60}\n")

    inputs = {"messages": [HumanMessage(content=question)]}

    for output in app.stream(inputs, stream_mode="values"):
        last_message = output["messages"][-1]

        if isinstance(last_message, AIMessage):
            if last_message.content:
                print(f"🤖 Agent: {last_message.content}")
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                for tool_call in last_message.tool_calls:
                    print(f"🔧 Tool Call: {tool_call['name']}({tool_call['args']})")

        elif isinstance(last_message, ToolMessage):
            print(f"✅ Tool Result: {last_message.content}")

    print(f"\n{'='*60}\n")

if __name__ == "__main__":
    # 테스트 실행
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║         Simple Calculator Agent - LangGraph Demo         ║
    ║                  Phase 1 실습 프로젝트                     ║
    ╚══════════════════════════════════════════════════════════╝
    """)

    # 예제 질문들
    questions = [
        "123과 456을 더하면 얼마야?",
        "1000에서 234를 빼면?",
        "12 곱하기 15는?",
        "144를 12로 나누면?",
    ]

    for question in questions:
        run_agent(question)

