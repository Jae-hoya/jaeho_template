# LangGraph 구현 상세 (코드 레벨)

이 문서는 이 저장소의 LangGraph 기반 RAG 구현을 코드 흐름/구성요소 단위로 풀어 설명합니다.
주요 파일은 `langgraph_rag.py`, `search_app/hybrid_search.py`, `search_app/database.py`, `streamlit_app.py` 입니다.

## 1) 상태 정의 (`langgraph_rag.py`)

`RAGState`는 그래프 노드들이 주고받는 상태 스키마입니다.

```python
class RAGState(TypedDict):
    question: str
    route_decision: str  # "search" or "direct"
    search_results: List[Dict[str, Any]]
    answer: str
    debug: bool
```

- `question`: 사용자 질문 원문
- `route_decision`: 라우팅 결과 (`search`/`direct`)
- `search_results`: 검색 결과 리스트(딕셔너리)
- `answer`: LLM 최종 답변
- `debug`: 디버그 모드 플래그

## 2) 그래프 구성 (`langgraph_rag.py`)

그래프는 `LangGraphRAG._build_graph()`에서 구성됩니다.

```python
workflow = StateGraph(RAGState)
workflow.add_node("route", self.route_node)
workflow.add_node("retrieve", self.retrieve_node)
workflow.add_node("generate", self.generate_node)

workflow.add_edge(START, "route")
workflow.add_conditional_edges(
    "route",
    self.decide_next_step,
    {"search": "retrieve", "direct": "generate"}
)
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)
```

그래프 흐름 요약:

- `START -> route`
- `route -> retrieve` 또는 `route -> generate`
- `retrieve -> generate`
- `generate -> END`

분기 로직은 `decide_next_step()`이 `state["route_decision"]`을 그대로 반환하는 방식으로 동작합니다.

## 3) 라우팅 노드 (`route_node`)

`route_node()`는 질문을 분석해 `search`/`direct` 중 하나를 선택합니다.

- 프롬프트는 반드시 `search` 또는 `direct` 한 단어만 출력하도록 강하게 제한합니다.
- 응답 문자열에서 `search`/`direct` 포함 여부를 검사해 결정합니다.
- 둘 다 아니면 기본값으로 `search`를 선택합니다(모호할 때 검색 우선).

핵심 부분:

```python
response = self.llm.invoke(prompt)
decision = response.content.strip().lower()

if "search" in decision:
    route_decision = "search"
elif "direct" in decision:
    route_decision = "direct"
else:
    route_decision = "search"
```

## 4) 검색 노드 (`retrieve_node`)

`retrieve_node()`는 하이브리드 검색을 수행하고 결과를 상태에 저장합니다.

```python
results = self.hybrid_search.search(question, limit=3, search_limit=20)
return {"search_results": results}
```

- 검색 로직은 `search_app/hybrid_search.py`에 분리되어 있습니다.
- 최종 결과는 최대 3개(`limit=3`)만 사용합니다.

## 5) 생성 노드 (`generate_node`)

`route_decision`에 따라 프롬프트가 달라집니다.

### 5-1) 검색 기반 답변

- `_format_search_results()`로 검색 결과를 텍스트 컨텍스트로 변환
- 검색 결과에 없는 정보는 추측하지 않도록 프롬프트에서 강제
- 출력 형식(요약, 상품 후보, 추가 질문)을 고정

```python
context = self._format_search_results(search_results)
prompt = f"""[System]
... (검색 결과만 사용, 형식 고정) ...
[Context]
<context>
{context}
</context>
[User]
질문: {question}
답변:"""
```

### 5-2) 직접 답변

- 검색 없이 2~4문장으로 간단 응답
- 검색이 필요한 요청이면 추가 질문 유도

```python
prompt = f"""[System]
... (간단 응답 규칙) ...
[User]
질문: {question}
답변:"""
```

## 6) 그래프 실행 (`run` / Streamlit 연동)

### CLI 실행

`LangGraphRAG.run()`이 초기 상태를 만들고 `graph.invoke()`를 호출합니다.

```python
initial_state: RAGState = {
    "question": question,
    "route_decision": "",
    "search_results": [],
    "answer": "",
    "debug": self.debug
}
final_state = self.graph.invoke(initial_state)
return final_state["answer"]
```

### Streamlit 실행

`streamlit_app.py`에서 `process_question()`이 동일하게 `rag.graph.invoke()`를 호출합니다.

```python
final_state = st.session_state.rag.graph.invoke(initial_state)
answer = final_state["answer"]
route = final_state.get("route_decision", "unknown")
search_results = final_state.get("search_results", [])
```

## 7) 하이브리드 검색 상세 (`search_app/hybrid_search.py`)

### 7-1) 쿼리 임베딩

```python
response = self.client.embeddings.create(
    model=Config.EMBEDDING_MODEL,
    input=query,
    encoding_format="float"
)
return response.data[0].embedding
```

### 7-2) BM25 검색

`BM25_MODE=paradedb`일 때 `@@@` + `paradedb.score()` 사용:

```sql
SELECT id, paradedb.score(id) AS score
FROM loan_products
WHERE cleaned_searchable_text @@@ %s
ORDER BY paradedb.score(id) DESC
LIMIT %s
```

`BM25_MODE=fts`일 때 Postgres FTS 사용:

```sql
SELECT id, ts_rank(
    to_tsvector('english', cleaned_searchable_text),
    plainto_tsquery('english', %s)
) AS score
FROM loan_products
WHERE to_tsvector('english', cleaned_searchable_text) @@ plainto_tsquery('english', %s)
ORDER BY score DESC
LIMIT %s
```

### 7-3) 벡터 검색

```sql
SELECT id, 1 - (searchable_text_embedding <=> %s::vector) as score
FROM loan_products
ORDER BY searchable_text_embedding <=> %s::vector
LIMIT %s
```

### 7-4) RRF 결합

`reciprocal_rank_fusion()`이 BM25/벡터 결과를 다음 공식으로 합산합니다.

```
RRF_score(d) = sum(1 / (k + rank(d)))
```

### 7-5) 상세 조회

RRF 상위 id를 이용해 실제 필드들을 조회하고 `rrf_score`를 붙여 반환합니다.

## 8) DB 레이어 (`search_app/database.py`)

- `Database.connect()`가 `psycopg.connect()`로 연결 생성
- `create_vector_index()`는 ivfflat + cosine ops 인덱스 생성
- `get_vector_db_info()`는 전체 row 수/임베딩 존재 row 수를 집계

```sql
SELECT COUNT(*) AS total,
       COUNT(searchable_text_embedding) AS embeddings
FROM loan_products
```

## 9) 핵심 요약

- LangGraph는 `route -> retrieve -> generate`의 단일 분기 구조
- `route_decision` 값 하나로 검색 여부가 결정됨
- 검색 결과 컨텍스트를 엄격하게 통제해서 hallucination을 줄임
- 하이브리드 검색은 BM25 + 벡터 + RRF 결합으로 결과 정렬
