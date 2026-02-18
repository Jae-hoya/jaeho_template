# Backend Architecture Map (API -> Service -> Flow -> Integration -> Schema)

기준 코드: `_opencode_with_copyjoe_V0.4` (FastAPI + LangGraph + LangChain)

## 1) 디렉토리 구조

아래는 현재 프로젝트의 구조를 빠르게 이해하기 위한 트리입니다.

### 1.1 루트 구조 (요약)

```text
_opencode_with_copyjoe_V0.4/
├─ .env
├─ .env.example
├─ .gitignore
├─ .venv_rt/
├─ .venv/
├─ ㅁㄴㅇ.md
├─ app/
├─ constraints.txt
├─ copyjoe_md.md
├─ copyjoe_prd_v1.1.md
├─ copyjoe_prd_v1.2.md
├─ data/
├─ datasets/
├─ docs/
├─ fastcampus-code-qa/
├─ file_upload_set_ko.md
├─ file_upload_set.md
├─ frontend/
├─ margeting_agent.md
├─ notebooks/
├─ opencode.json
├─ play_opencode_v0.1.md
├─ play_opencode_v0.3.md
├─ play_opencode.md
├─ play.md
├─ README.md
├─ requirements-dev.txt
├─ requirements.txt
├─ scripts/
└─ tests/
```

### 1.2 `app/` 구조 (백엔드 핵심)

```text
app/
├─ main.py
├─ api/
│  ├─ deps.py
│  └─ v1/
│     ├─ router.py
│     ├─ copy.py
│     ├─ files.py
│     ├─ rag.py
│     ├─ web.py
│     ├─ export.py
│     ├─ meta.py
│     └─ history.py
├─ core/
│  ├─ config.py
│  └─ errors.py
├─ flows/
│  ├─ copy_generation_graph.py
│  ├─ copy_generation/
│  │  ├─ graph.py
│  │  ├─ nodes.py
│  │  ├─ chains.py
│  │  └─ states.py
│  ├─ copy_lite_generation_graph.py
│  ├─ copy_lite_generation/
│  │  ├─ graph.py
│  │  ├─ nodes.py
│  │  └─ states.py
│  ├─ file_upload_graph.py
│  ├─ rag_graph.py
│  ├─ rag_workflow/
│  │  ├─ graph.py
│  │  ├─ nodes.py
│  │  └─ states.py
│  ├─ web_graph.py
│  ├─ web_workflow/
│  │  ├─ graph.py
│  │  ├─ nodes.py
│  │  └─ states.py
│  ├─ export_graph.py
│  ├─ history_graph.py
│  ├─ meta_graph.py
│  └─ graph_registry.py
├─ integrations/
│  ├─ model_factory.py
│  ├─ embeddings_factory.py
│  ├─ milvus_client.py
│  ├─ docling_client.py
│  ├─ landing_page_client.py
│  └─ langfuse_client.py
├─ schemas/
│  ├─ common.py
│  ├─ copy.py
│  ├─ file.py
│  ├─ rag.py
│  ├─ web.py
│  ├─ export.py
│  ├─ meta.py
│  └─ history.py
├─ services/
│  ├─ copy_service.py
│  ├─ file_service.py
│  ├─ rag_service.py
│  ├─ web_search_service.py
│  ├─ document_store.py
│  ├─ export_service.py
│  ├─ meta_service.py
│  └─ history_service.py
└─ static/
```

## 2) 레이어 책임 정리

- API (`app/api/v1/*.py`): 엔드포인트 선언, DI 주입, 요청/응답 타입 지정
- Service (`app/services/*.py`): 유스케이스 단위 조합, Flow 호출, 캐시/후처리
- Flow (`app/flows/**`): LangGraph 기반 단계별 상태 전이(노드 체인)
- Integration (`app/integrations/*.py`): 외부 시스템/모델/벡터DB/OCR 어댑터
- Schema (`app/schemas/*.py`): Pydantic 데이터 계약(Request/Response/도메인 모델)

공통 라우팅과 DI:

- API prefix: `Settings.api_v1_prefix` 기본값 `/api/v1` (`app/core/config.py`)
- 라우터 집합: `app/api/v1/router.py`
- 의존성 생성: `app/api/deps.py`

## 3) 엔드포인트 상세 맵

요청하신 4개 도메인(카피/파일/RAG/웹) 기준으로 API -> Service -> Flow -> Integration -> Schema를 상세히 정리했습니다.

---

## 4) 카피(Copy) 엔드포인트 맵

### 4.1 `POST /api/v1/copy/generate`

단일 endpoint에서 두 요청 모드를 지원합니다.

- 상세 모드: `CopyGenerateRequest` -> `CopyGenerateResponse`
- 간편 모드: `CopyLiteRequest` -> `CopyLiteResponse`

**API**

- `app/api/v1/copy.py` -> `generate_copy(payload: CopyGenerateRequest | CopyLiteRequest)`
  - payload 타입에 따라 `CopyService.generate(...)` 또는 `CopyService.generate_prompt_mode(...)`를 라우팅

**Service**

- `CopyService.generate()` (`app/services/copy_service.py`)
  - 내부에서 `CopyGenerationGraph.run(...)` 실행
  - 결과를 스타일별로 projection(`_project_styles`) 후 `CopyGenerateResponse` 구성
- `CopyService.generate_prompt_mode()` (`app/services/copy_service.py`)
  - 내부에서 `CopyLiteGenerationGraph.run(...)` 실행
  - 프롬프트 파싱/추론/랜딩 컨텍스트를 통해 `normalized_request` 생성
  - 최종 생성은 `generate()`를 재사용

**Flow**

- `CopyGenerationGraph` (`app/flows/copy_generation/graph.py`)
  - 노드 흐름: `prepare` -> `rag?` -> `web?` -> `generate`
  - 분기 규칙:
    - `use_rag=True`면 RAG 수집
    - `web_search_mode=True`면 웹 검색 컨텍스트 추가
- `CopyLiteGenerationGraph` (`app/flows/copy_lite_generation/graph.py`)
  - 노드 흐름:
    1. `parse_prompt`
    2. `landing_context`
    3. `infer_objective`
    4. `infer_channel`
    5. `infer_language`
    6. `build_request`
    7. `generate_copy`
    8. `build_response`

**Integration**

- LLM: `create_chat_model()` (`app/integrations/model_factory.py`)
  - OpenAI 또는 Ollama(`qwen3:8b` 등)
- RAG: `RagService.build_context()` -> `RagWorkflowGraph` -> `MilvusClient`
- Web: `WebSearchService.search()` -> `WebWorkflowGraph` (Tavily)
- 랜딩 분석: `WebSearchService.analyze_landing_page()` / `search_then_analyze()`
  - 내부적으로 `LandingPageClient` + Tavily 사용 가능

**Schema**

- Request: `CopyGenerateRequest` 또는 `CopyLiteRequest` (`app/schemas/copy.py`)
- Response: `CopyGenerateResponse` 또는 `CopyLiteResponse` (`app/schemas/copy.py`)
- 내부 구조화 출력: `CopyStructuredOutput` (`app/schemas/copy.py`)
- 파싱 중간 모델: `CopyLiteParsedInput` (`app/schemas/copy.py`)
- 출처: `SourceItem` (`app/schemas/common.py`)

---

## 5) 파일(File) 엔드포인트 맵

### 5.1 `POST /api/v1/files/upload`

**API**

- `app/api/v1/files.py` -> `upload_files(files: list[UploadFile])`

**Service**

- `FileService.upload_files()` (`app/services/file_service.py`)
  - `FileUploadGraph.run(...)` 호출

**Flow**

- `FileUploadGraph` (`app/flows/file_upload_graph.py`)
  - 노드 흐름: `validate` -> `process` -> `to_response`
  - 처리 핵심:
    - 배치 개수 제한 검증
    - 확장자/용량 검증
    - 파일 저장 -> 텍스트 변환 -> `DocumentStore` 저장
    - `document_id` 발급 (RAG 인덱싱의 입력 키)

**Integration**

- OCR/문서 변환: `DoclingClient.convert_to_text_with_meta()`
  - PDF/이미지/오피스 문서별 변환 전략 + fallback 포함

**Schema**

- Response: `FileUploadResponse`, `UploadedFileItem` (`app/schemas/file.py`)

### 5.2 `POST /api/v1/files/warmup-ocr`

**API**

- `app/api/v1/files.py` -> `warm_up_ocr()`

**Service**

- `FileService.warm_up_ocr()`

**Flow**

- 별도 LangGraph 없음(서비스에서 integration 직접 호출)

**Integration**

- `DoclingClient.warm_up()` (OCR/VLM 컴포넌트 워밍업)

**Schema**

- Response: `OcrWarmupResponse` (`app/schemas/file.py`)

---

## 6) RAG 엔드포인트 맵

### 6.1 `POST /api/v1/rag/index`

**API**

- `app/api/v1/rag.py` -> `rag_index(payload: RagIndexRequest)`

**Service**

- `RagService.index_documents()` (`app/services/rag_service.py`)

**Flow**

- `RagWorkflowGraph.run_index()` (`app/flows/rag_workflow/graph.py`)
  - 노드 흐름: `validate` -> `index` -> `to_response`
  - `IndexDocumentsNode`:
    - `DocumentStore`에서 문서 로드
    - `RecursiveCharacterTextSplitter`로 chunk 분할
    - 벡터 저장소에 upsert (`MilvusClient.add_documents`)

**Integration**

- 벡터 저장소: `MilvusClient`
  - Milvus 연결 가능 시 Milvus 사용
  - 실패/미설정 시 memory backend fallback
- 임베딩: `create_embeddings()` (`OpenAIEmbeddings` / `OllamaEmbeddings` / `HashEmbeddings`)

**Schema**

- Request: `RagIndexRequest`
- Response: `RagIndexResponse`

### 6.2 `POST /api/v1/rag/search`

**API**

- `app/api/v1/rag.py` -> `rag_search(payload: RagSearchRequest)`

**Service**

- `RagService.search()`

**Flow**

- `RagWorkflowGraph.run_search()`
  - 노드 흐름: `search` -> `to_chunks`
  - `SearchVectorsNode`: 유사도 검색
  - `ToChunksNode`: `RagChunk`로 매핑

**Integration**

- `MilvusClient.similarity_search_with_scores(...)`

**Schema**

- Request: `RagSearchRequest`
- Response: `RagSearchResponse`
- Item: `RagChunk`

### 6.3 `POST /api/v1/rag/reset`

**API**

- `app/api/v1/rag.py` -> `rag_reset()`

**Service**

- `RagService.reset_index()`

**Flow**

- 별도 LangGraph 없음(서비스 단에서 직접 정리)

**Integration**

- `DocumentStore.clear(remove_files=True)`
- `MilvusClient.clear()`

**Schema**

- Response: `RagResetResponse`

---

## 7) 웹(Web) 엔드포인트 맵

### 7.1 `POST /api/v1/web/search`

**API**

- `app/api/v1/web.py` -> `web_search(payload: WebSearchRequest)`

**Service**

- `WebSearchService.search(query, max_results, strict=True)`

**Flow**

- `WebWorkflowGraph.run_search()`
  - 노드 흐름: `prepare` -> `search` -> `to_results`
  - Tavily 클라이언트 미존재 + strict 모드면 에러 반환

**Integration**

- Tavily SDK (`TavilyClient.search`) - API key 있을 때 활성화

**Schema**

- Request: `WebSearchRequest`
- Response: `WebSearchResponse`
- Item: `WebSearchResult`

### 7.2 `POST /api/v1/web/landing/analyze`

**API**

- `app/api/v1/web.py` -> `landing_analyze(payload: LandingAnalyzeRequest)`
  - `url` 있으면 direct analyze
  - 없으면 `query`로 검색 후 대표 URL 분석

**Service**

- `WebSearchService.analyze_landing_page(url, from_tavily=False)`
- `WebSearchService.search_then_analyze(query, max_results)`
- URL 기반 캐시(`_landing_cache`) 사용

**Flow**

- Direct URL: `WebWorkflowGraph.run_analyze_landing_page()`
  - 노드 흐름: `analyze` -> `to_response`
- Query 기반: `WebWorkflowGraph.run_search_then_analyze()`
  - 노드 흐름: `search` -> `select` -> `analyze`

**Integration**

- 랜딩 분석: `LandingPageClient`
  - Playwright(subprocess/sync) 우선
  - 실패 시 `requests + BeautifulSoup` fallback
- Query 모드의 후보 URL 탐색은 Tavily 사용

**Schema**

- Request: `LandingAnalyzeRequest` (url/query 중 하나 필수)
- Response: `LandingAnalyzeResponse`

---

## 8) 엔드포인트 간 데이터 연결 관계

- `files/upload` -> `document_id` 생성
- `rag/index`는 위 `document_id`를 받아 chunk/vector 인덱싱
- `copy/generate` 상세 모드는 `use_rag`, `top_k`, `rag_document_ids`로 RAG 컨텍스트를 흡수
- `copy/generate` 간편 모드는 `landing_url` 또는 `landing_query`로 웹 컨텍스트를 먼저 만들고, 그 결과를 최종 카피 생성에 주입

즉, 실무에서 자주 쓰는 흐름은 다음과 같습니다.

1) 파일 업로드 -> 2) RAG 인덱싱 -> 3) 카피 생성(근거 포함)

또는

1) 웹 검색/랜딩 분석 -> 2) 카피 라이트 생성(채널/랜딩 문맥 반영)

## 9) 한 눈에 보는 endpoint-to-layer 요약표

| Endpoint | API | Service | Flow | Integration | Schema |
|---|---|---|---|---|---|
| `POST /api/v1/copy/generate` | `api/v1/copy.py` | `CopyService.generate` + `CopyService.generate_prompt_mode` | `CopyGenerationGraph` + `CopyLiteGenerationGraph` | `model_factory`, `RagService/Milvus`, `WebSearchService`, `LandingPageClient`, Tavily | `CopyGenerateRequest/Response` 또는 `CopyLiteRequest/Response` |
| `POST /api/v1/files/upload` | `api/v1/files.py` | `FileService.upload_files` | `FileUploadGraph` | `DoclingClient`, `DocumentStore` | `FileUploadResponse` |
| `POST /api/v1/files/warmup-ocr` | `api/v1/files.py` | `FileService.warm_up_ocr` | - | `DoclingClient` | `OcrWarmupResponse` |
| `POST /api/v1/rag/index` | `api/v1/rag.py` | `RagService.index_documents` | `RagWorkflowGraph(index)` | `MilvusClient`, embeddings factory | `RagIndexRequest/Response` |
| `POST /api/v1/rag/search` | `api/v1/rag.py` | `RagService.search` | `RagWorkflowGraph(search)` | `MilvusClient` | `RagSearchRequest/Response` |
| `POST /api/v1/rag/reset` | `api/v1/rag.py` | `RagService.reset_index` | - | `DocumentStore`, `MilvusClient` | `RagResetResponse` |
| `POST /api/v1/web/search` | `api/v1/web.py` | `WebSearchService.search` | `WebWorkflowGraph(search)` | Tavily | `WebSearchRequest/Response` |
| `POST /api/v1/web/landing/analyze` | `api/v1/web.py` | `WebSearchService.analyze_landing_page/search_then_analyze` | `WebWorkflowGraph(landing/search_then_analyze)` | `LandingPageClient`, Tavily | `LandingAnalyzeRequest/Response` |
