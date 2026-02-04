  🎯 Simple Calculator Agent 구조 설명

  사용자 질문: "123과 456을 더하면 얼마야?"
        ↓
  ┌─────────────────────┐
  │   START             │
  └─────────────────────┘
        ↓
  ┌─────────────────────┐
  │   Agent Node        │ ← LLM이 질문 분석
  │ (Claude 3.5 Sonnet) │   "calculator 도구 필요!"
  └─────────────────────┘
        ↓
  ┌─────────────────────┐
  │ Should Continue?    │ ← Tool call 있음?
  └─────────────────────┘
        ↓ Yes
  ┌─────────────────────┐
  │   Tools Node        │ ← calculator("add", 123, 456)
  │   실행: 123 + 456    │   결과: 579
  └─────────────────────┘
        ↓
  ┌─────────────────────┐
  │   Agent Node        │ ← Tool 결과로 최종 답변 생성
  │ "579입니다!"         │
  └─────────────────────┘
        ↓
  ┌─────────────────────┐
  │   END               │
  └─────────────────────┘

  핵심 개념:

  1. State: 메시지 리스트를 관리
  2. Nodes: agent (LLM 호출), tools (도구 실행)
  3. Edges: 노드 간 흐름 제어
  4. Conditional Edge: Tool이 필요한지 판단

  코드 하이라이트:

  # ✅ Tool 정의 (함수로 간단하게)
  def calculator(operation, a, b):
      if operation == "add":
          return a + b
      # ...

  # ✅ LLM에 Tool 바인딩
  model_with_tools = model.bind_tools([calculator])

  # ✅ ReAct 패턴 구현
  workflow.add_conditional_edges(
      "agent",
      should_continue,  # Tool 필요? → tools / 완료? → END
  )
  workflow.add_edge("tools", "agent")  # 결과 → 다시 Agent