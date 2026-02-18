```md
# Copyjoe PRD v1.2

## 1) 제품 한 줄 정의
카피조(Copyjoe)는 고객의 행동(기억, 클릭, 장바구니, 상담 신청)을 유도하는 설득 문장을 생성하고, RAG 및 웹 기반 근거를 반영하는 마케팅 특화 AI 카피 생성 플랫폼이다.

---

## 2) 문제 정의와 목표

### 문제 정의
- 마케터/기획자는 매번 새로운 카피를 빠르게 만들기 어렵다.
- 카피 품질이 작성자 역량에 따라 편차가 크다.
- 문서 기반 근거(RAG)와 웹 최신 정보가 반영되지 않는 경우가 많다.
- 자유형 질문과 구조화 입력을 동시에 처리하기 어렵다.

### 목표
- 카피 생성 시간을 단축한다.
- 카피 품질을 구조화된 입력으로 표준화한다.
- 파일 업로드 기반 RAG와 웹 서치(Tavily)를 통해 근거 기반 카피를 생성한다.
- 자유형 프롬프트 기반 AI 응답도 지원한다.
- 생성 이력을 쓰레드 단위로 관리한다.

---

## 3) 핵심 사용자
- 퍼포먼스 마케터
- 콘텐츠 마케터
- AE/기획자
- 1인 사업자/소상공인

---

## 4) 핵심 기능

### 4.1 카피 생성
- 목적:
  - `brand_memory`
  - `click`
  - `add_to_cart`
  - `consultation`
- 스타일:
  - `head`
  - `body`
  - `cta`
  - `slogan`
  - `sns`
  - `description`

### 4.2 스토리보드용 콘티 초안 자동 생성

### 4.3 자유형 자연어 프롬프트 지원
- 최대 8,000자
- 구조화 입력 없이 단일 프롬프트로 요청 가능
- 구조화 입력과 함께 사용 가능

### 4.4 랜딩페이지 분석
- 웹 검색 결과 URL 기반 콘텐츠 분석
- 주요 카피, H1/H2 구조, CTA 문구 추출

### 4.5 멀티 포맷 출력
- JSON 응답
- Markdown(.md) 다운로드
- Word(.doc/.docx) 다운로드

### 4.6 사용 이력 관리
- 쓰레드(Thread) 형식 저장
- 프롬프트/결과 히스토리 관리
- 이전 요청 재실행 가능

### 4.7 복사 버튼 동작

---

## 5) 입력 스키마

### 구조화 입력
- `product_name`: string
- `target_audience`: string
- `pain_point`: string
- `differentiator`: string
- `tone`: string
- `objective`: enum
- `styles`: enum array
- `channel`: string
- `language`: string (기본 `ko`)
- `web_search_mode`: boolean
- `use_rag`: boolean
- `top_k`: number (기본 5)

### 자유형 입력
- `free_prompt`: string (최대 8000자)

### 웹 검색
- `web_search_query`: string

### 업로드 파일
지원 형식:
- `pdf`
- `doc`
- `docx`
- `txt`
- `xls`
- `xlsx`
- `ppt`
- `pptx`
- `png`
- `jpg`

---

## 6) 출력 스키마

- `head`: string
- `body`: string
- `cta`: string
- `slogan`: string
- `sns`: string
- `description`: string
- `storyboard_outline`: string[]
- `rationale`: string
- `sources`: array
- `thread_id`: string
- `created_at`: datetime
- `usage_log`:
  - `use_rag`: boolean
  - `use_web`: boolean
  - `retrieved_docs_count`: number
  - `model_name`: string

---

## 7) OpenAPI 기반 FE/BE 연동

FastAPI를 사용해 OpenAPI를 단일 계약으로 사용한다.

### 엔드포인트
- `POST /api/v1/copy/generate`
- `POST /api/v1/files/upload`
- `POST /api/v1/rag/index`
- `POST /api/v1/rag/search`
- `POST /api/v1/web/search`
- `POST /api/v1/export/docx`
- `GET /health`
- `GET /docs`
- `GET /openapi.json`

### 개발 규칙
- FE는 OpenAPI 기반 타입 자동 생성
- 공통 에러 포맷 사용
- JSON structured output 강제

---

## 8) RAG 처리 파이프라인

1. 업로드 수신
2. Docling 변환
3. 텍스트 정제
4. Chunking
5. qwen3-embedding 임베딩
6. Milvus 저장
7. 질의 시 top-k 검색
8. 검색 결과를 생성 프롬프트에 주입

---

## 9) 파일 업로드 정책

- 최대 파일 크기: 30MB
- 최대 파일 수: 10개/요청
- 허용 확장자 외 업로드 시 에러 반환
- 변환 실패 시 파일별 실패 사유 반환

### 에러 코드
- `UNSUPPORTED_FILE_TYPE`
- `FILE_TOO_LARGE`
- `DOC_CONVERSION_FAILED`
- `EMBEDDING_FAILED`
- `VECTOR_DB_ERROR`
- `WEB_SEARCH_ERROR`

---

## 10) 백엔드 구조 (Python)

```

app/
├── main.py
├── api/v1/
├── schemas/
├── services/
│    ├── copy_service.py
│    ├── rag_service.py
│    ├── web_search_service.py
│    ├── export_service.py
├── integrations/
│    ├── docling_client.py
│    ├── milvus_client.py
│    ├── langfuse_client.py

```

---

## 11) 프론트엔드 구조 (Vue3)

```

IndexPage.vue
copyjoe/
├── sections/
│    ├── PromptSection.vue
│    ├── GenerationSection.vue
├── models-service/
│    ├── types.ts
│    ├── service.ts
│    ├── WebAgentService.ts
├── components/
│    ├── PromptOption.vue
│    ├── LoadingSpinner.vue
│    ├── GenerateResult.vue
│    ├── ExportDialog.vue

```

---

## 12) 기술 스택

### Backend
- fastapi
- uvicorn
- pydantic
- python-multipart
- langchain
- langchain-ollama
- langgraph
- docling
- pymilvus
- langchain-milvus
- tavily-python
- python-docx
- langfuse

### Model
- qwen3-embedding
- qwen3-vl:32b
- qwen3-vl:8b
- gpt-oss

### Frontend
- vue
- vue-router
- vue-i18n
- typescript
- vite-svg-loader
- axios
- pinia

---

## 13) 수용 기준 (Definition of Done)

- 선택한 스타일별 결과 반환
- 자유형 프롬프트 정상 처리
- RAG 및 Web 결과가 응답에 반영됨
- 랜딩페이지 분석 결과 추출 가능
- 복사 버튼 정상 동작
- Word(.docx) 다운로드 정상 동작
- 업로드 파일 Docling 변환 완료
- Milvus 인덱싱 및 검색 정상 동작
- Tavily ON/OFF 반영
- `/docs`, `/openapi.json`, `/health` 정상 노출
- 쓰레드 기반 이력 저장 및 조회 가능

---

## 14) 버전 메모
- v1.2: 자유형 프롬프트, 멀티 포맷 출력, 랜딩페이지 분석, 이력 관리 기능 추가
```
