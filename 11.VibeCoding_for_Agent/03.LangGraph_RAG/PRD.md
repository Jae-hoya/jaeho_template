스펙:
- Langgraph, LangChain, langchain-openai
- GPT-5-mini

목표:
Routing 기반 Langgraph RAG CLI 구현

워크플로우:
1. Route: 질문 분석 → search/direct 판단
2. Retrieve: Hybrid Search로 top-3 검색
3. Generate: 답변 생성

핵심 구현:
- StateGraph로 노드 정의 (route, retrieve, generate)
- conditional_edges로 routing

CLI:
uv run python langgraph_rag.py "질문" [--debug]

참고:
- langgraph 구현할 때에는 context7으로 최신 개발 문서 확인
- 필요에 따라 langchain-docs 도구 사용