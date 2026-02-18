# LangChain / LangGraph 실행 위치

아래 맵은 백엔드가 "API -> Service Facade -> LangGraph Flow -> Integrations" 순서로 실행되는 위치를 정리합니다.

## 1) API 진입점

- `app/api/v1/copy.py`
- `app/api/v1/files.py`
- `app/api/v1/rag.py`
- `app/api/v1/web.py`
- `app/api/v1/history.py`
- `app/api/v1/export.py`
- `app/api/v1/meta.py`

각 라우터는 I/O 스키마와 DI만 담당하고, 실제 흐름은 서비스/그래프에서 처리합니다.

## 2) Service Facade 계층

- `app/services/copy_service.py`
- `app/services/copy_lite_service.py`
- `app/services/file_service.py`
- `app/services/rag_service.py`
- `app/services/web_search_service.py`
- `app/services/history_service.py`
- `app/services/export_service.py`
- `app/services/meta_service.py`

서비스는 도메인별 진입 메서드만 제공하며, 비즈니스 분기와 오케스트레이션은 LangGraph로 위임합니다.

## 3) LangGraph 워크플로우

- `app/flows/copy_generation_graph.py`
  - copy 생성 컨텍스트 수집(RAG/web) + 생성 호출
- `app/flows/copy_lite_generation_graph.py`
  - prompt 파싱 -> 랜딩 컨텍스트 수집 -> objective/channel/language 추론 -> 생성
- `app/flows/file_upload_graph.py`
  - 업로드 배치 검증 -> 파일별 변환/저장 -> 응답 집계
- `app/flows/rag_graph.py`
  - 인덱싱/검색/컨텍스트 생성 워크플로우
- `app/flows/web_graph.py`
  - Tavily 검색 / 랜딩 분석 / 검색 후 랜딩 분석 워크플로우
- `app/flows/history_graph.py`
  - thread 생성/목록/상세/메시지 append 워크플로우
- `app/flows/export_graph.py`
  - docx/md/doc 액션 라우팅 및 결과 생성 워크플로우
- `app/flows/meta_graph.py`
  - copy form guide 구성 워크플로우

테스트에서 그래프를 한 번에 조합해 쓰려면:

- `app/flows/graph_registry.py`
  - `build_graph_registry()`로 도메인 그래프를 통합 생성

## 4) LangChain/모델 실행 지점

- `app/services/copy_service.py`의 `_run_chain_or_fallback`
  - `ChatPromptTemplate`
  - `model.with_structured_output(CopyStructuredOutput)`
  - `chain.invoke(...)`
- `app/services/copy_lite_service.py`의 `_parse_prompt`
  - `ChatPromptTemplate`
  - `model.with_structured_output(CopyLiteParsedInput)`

벡터 DB(Milvus) 연결 지점:

- `app/integrations/milvus_client.py`
  - `langchain_milvus.Milvus` 어댑터를 사용해 vector store를 생성
  - `MILVUS_URI` 미설정/연결 실패 시 메모리 백엔드로 폴백

즉, LangGraph는 도메인 워크플로우를 담당하고, LangChain은 LLM 프롬프트/구조화 출력을 담당합니다.

## 5) 대화형 예시

- Python CLI: `scripts/interactive_copy_chat.py`
- Notebook: `notebooks/interactive_chat_test.ipynb`
