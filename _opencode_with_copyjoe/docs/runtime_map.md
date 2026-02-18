# LangChain / LangGraph 실행 위치

아래 파일을 보면, 어디서 무엇이 실행되는지 바로 파악할 수 있습니다.

## 1) API 진입점

- `app/api/v1/copy.py`: `POST /api/v1/copy/generate`
- `app/api/v1/copy.py`: `POST /api/v1/copy/generate-lite` (prompt + style 중심)
- `app/services/copy_service.py`: 카피 생성 서비스 시작점

간편 생성은 `app/services/copy_lite_service.py`에서
prompt를 구조화 입력으로 자동 보정한 뒤 `copy_service`로 전달합니다.

## 2) LangGraph 워크플로우

- `app/flows/copy_generation_graph.py`
  - `prepare` 노드: 질의 문자열 생성
  - `rag` 노드: RAG 컨텍스트 수집
  - `web` 노드: Tavily 검색 컨텍스트 수집
  - `generate` 노드: 최종 생성 호출

즉, **LangGraph는 컨텍스트 수집/분기 순서를 담당**합니다.

## 3) LangChain 실행 지점

- `app/services/copy_service.py`의 `_run_chain_or_fallback`
  - `ChatPromptTemplate`
  - `model.with_structured_output(CopyStructuredOutput)`
  - `chain.invoke(...)`

즉, **LangChain은 실제 모델 프롬프트/구조화 출력 생성을 담당**합니다.

## 4) 대화형 예시

- Python CLI: `scripts/interactive_copy_chat.py`
- Notebook: `notebooks/interactive_chat_test.ipynb`
