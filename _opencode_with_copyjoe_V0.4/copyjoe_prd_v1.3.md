# Copyjoe PRD v1.3

- 문서 버전: v1.3
- 작성일: 2026-02-18
- 기준 프로젝트: `_opencode_with_copyjoe_V0.3`
- 문서 목적: Copyjoe의 제품 요구사항, API 계약, 품질 기준을 현재 구현 기준으로 명확히 정의한다.

## 1) 제품 한 줄 정의

Copyjoe는 마케팅 브리프, 업로드 문서(RAG), 웹/랜딩 분석 근거를 결합해 전환 중심 카피와 콘티 초안을 빠르게 생성하는 AI 카피 생성 플랫폼이다.

---

## 2) 문제 정의와 목표

### 2.1 문제 정의

- 마케터/기획자는 캠페인별로 카피를 반복 제작해야 하며 제작 리드타임이 길다.
- 카피 품질이 작성자 숙련도에 크게 의존해 일관성이 낮다.
- 내부 문서/랜딩/웹 최신 맥락을 반영하지 못해 설득 근거가 약해진다.
- 자유형 요청과 구조화된 요청을 동시에 다루기 어려워 실무 적용이 불편하다.

### 2.2 제품 목표

- 자연어 한 번 입력으로 실무에서 바로 검토 가능한 카피 초안을 만든다.
- 구조화 입력/자유형 입력 모두에서 안정적인 결과 형식을 제공한다.
- 문서 기반 RAG + 웹/랜딩 분석 기반 근거를 결합해 설명 가능한 카피를 생성한다.
- 대화형 개선 루프를 지원해 재생성 비용을 줄인다.

### 2.3 비목표(Out of Scope)

- 사용자 인증/권한/결제 기능
- 멀티 테넌트 데이터 격리
- 영구 저장 기반 히스토리 DB(현재 히스토리는 인메모리)

---

## 3) 핵심 사용자

- 퍼포먼스 마케터
- 콘텐츠 마케터
- AE/기획자
- 1인 사업자/소상공인

---

## 4) 주요 사용자 시나리오

### 시나리오 A: 자연어 브리프로 즉시 카피 생성

1. 사용자가 스타일만 선택하고 자유형 브리프를 입력한다.
2. 시스템이 목적/채널/언어를 자동 추론하거나 기본값을 적용한다.
3. 생성 결과와 assumptions(가정값)을 함께 제공한다.

### 시나리오 B: 내부 자료 기반 근거 카피 생성

1. 사용자가 문서를 업로드한다.
2. 시스템이 문서를 텍스트로 변환하고 인덱싱한다.
3. 생성 시 업로드 문서 범위로 RAG 검색을 제한해 결과를 만든다.

### 시나리오 C: 랜딩페이지 기반 콘티/카피 보강

1. 사용자가 랜딩 URL(또는 query)로 랜딩 분석을 실행한다.
2. 시스템이 h1/h2/CTA/body를 추출한다.
3. 분석 결과를 컨텍스트로 주입해 storyboard 중심 카피를 생성한다.

### 시나리오 D: 대화형 개선

1. 사용자가 기존 결과에 피드백을 입력한다.
2. 시스템이 이전 맥락을 유지한 채 재생성한다.
3. 개선 버전을 로그로 누적 관리한다.

---

## 5) 기능 요구사항 (Functional Requirements)

### FR-01. 구조화 카피 생성 (`POST /api/v1/copy/generate`)

- 입력된 구조화 필드를 기반으로 `head/body/cta/slogan/sns/description/storyboard_outline/rationale`를 생성해야 한다.
- `styles` 선택값에 따라 선택되지 않은 필드는 빈 문자열로 반환해야 한다.
- `use_rag`, `web_search_mode`, `top_k`, `rag_document_ids`를 반영해야 한다.

### FR-02. 간편 카피 생성 (`POST /api/v1/copy/generate-lite`)

- `prompt` 중심으로 동작하며, 필요 시 필드를 자동 추론해야 한다.
- 응답에 `assumptions`, `normalized_request`, `result`를 포함해야 한다.
- `landing_url` 또는 `landing_query`가 있을 경우 랜딩 렌더링 컨텍스트를 생성에 반영해야 한다.

### FR-03. 파일 업로드 및 변환 (`POST /api/v1/files/upload`)

- 다중 파일 업로드를 받아 파일별 성공/실패를 개별 리포트해야 한다.
- 변환 결과는 `document_id`로 참조 가능해야 한다.
- 파일별 `conversion_engine`, `text_preview`, 에러코드를 반환해야 한다.

### FR-04. OCR 웜업 (`POST /api/v1/files/warmup-ocr`)

- OCR 관련 구성요소 사전 로딩 결과를 반환해야 한다.
- warm-up 성공/실패 컴포넌트 목록과 소요 시간을 제공해야 한다.

### FR-05. RAG 인덱싱/검색/초기화

- `POST /api/v1/rag/index`: 문서 청크 인덱싱
- `POST /api/v1/rag/search`: 질의 기반 top-k 검색
- `POST /api/v1/rag/reset`: 문서 저장소/벡터 인덱스 초기화

### FR-06. 웹 검색 및 랜딩 분석

- `POST /api/v1/web/search`: Tavily 기반 웹 검색 결과 제공
- `POST /api/v1/web/landing/analyze`: URL 또는 query 기반 랜딩 분석 결과 제공
- 랜딩 분석은 Playwright 렌더링 분석 우선, 실패 시 requests 파서 폴백을 지원해야 한다.

### FR-07. 결과 내보내기

- `POST /api/v1/export/docx`
- `POST /api/v1/export/doc`
- `POST /api/v1/export/md`
- 동일한 생성 결과를 포맷별 파일로 다운로드할 수 있어야 한다.

### FR-08. 메타 가이드 및 히스토리

- `GET /api/v1/meta/copy-form-guide`: 입력 필드 작성 가이드 제공
- 히스토리 API:
  - `POST /api/v1/history/threads`
  - `GET /api/v1/history/threads`
  - `GET /api/v1/history/threads/{thread_id}`
  - `POST /api/v1/history/threads/{thread_id}/messages`

### FR-09. 상태 및 계약 노출

- `GET /health`로 provider/rag_backend 포함 헬스 상태를 확인할 수 있어야 한다.
- `GET /docs`, `GET /openapi.json`을 통해 OpenAPI 계약이 노출되어야 한다.

---

## 6) 입력/출력 스키마

### 6.1 구조화 입력 (`CopyGenerateRequest`)

| 필드 | 타입 | 필수 | 규칙 |
|---|---|---|---|
| `product_name` | string | Y | 1~200 |
| `target_audience` | string | Y | 1~200 |
| `pain_point` | string | Y | 1~500 |
| `differentiator` | string | Y | 1~500 |
| `tone` | string | Y | 기본 `신뢰형`, 1~100 |
| `objective` | enum | Y | `brand_memory`/`click`/`add_to_cart`/`consultation` |
| `styles` | enum[] | Y | `head/body/cta/slogan/sns/description`, 중복 제거 |
| `channel` | string | Y | 기본 `상세페이지` |
| `language` | string | Y | 기본 `ko`, 별칭 정규화 지원 |
| `web_search_mode` | boolean | Y | 기본 `false` |
| `use_rag` | boolean | Y | 기본 `true` |
| `top_k` | number | Y | 1~20, 기본 5 |
| `rag_document_ids` | string[] \| null | N | RAG 검색 문서 범위 제한 |

### 6.2 간편 입력 (`CopyLiteRequest`)

| 필드 | 타입 | 필수 | 규칙 |
|---|---|---|---|
| `prompt` | string | Y | 5~8000 |
| `styles` | enum[] | Y | 기본 `head/body/cta` |
| `language` | string | N | 미입력 시 추론 또는 `ko` |
| `objective` | enum \| null | N | 미입력 시 추론 또는 `click` |
| `channel` | string \| null | N | 미입력 시 추론 또는 `상세페이지` |
| `landing_url` | string \| null | N | 입력 시 렌더링 랜딩 컨텍스트 사용 |
| `landing_query` | string \| null | N | URL 없을 때 후보 검색 후 분석 |
| `web_search_mode` | boolean | N | 기본 `false` |
| `use_rag` | boolean | N | 기본 `true` |
| `top_k` | number | N | 1~20, 기본 5 |
| `rag_document_ids` | string[] \| null | N | RAG 문서 제한 |

### 6.3 카피 출력 (`CopyGenerateResponse`)

- `head`, `body`, `cta`, `slogan`, `sns`, `description`: string
- `storyboard_outline`: string[]
- `rationale`: string
- `sources`: `SourceItem[]`
  - `source_type`: `rag` \| `web`
  - `title`, `url`, `snippet`

### 6.4 간편 생성 출력 (`CopyLiteResponse`)

- `assistant_message`: 처리 요약
- `assumptions`: 자동 보정/추론 로그
- `normalized_request`: 최종 구조화 요청
- `result`: `CopyGenerateResponse`

---

## 7) API 계약 (OpenAPI 기준)

### 7.1 Copy

- `POST /api/v1/copy/generate`
- `POST /api/v1/copy/generate-lite`

### 7.2 Files / OCR

- `POST /api/v1/files/upload`
- `POST /api/v1/files/warmup-ocr`

### 7.3 RAG

- `POST /api/v1/rag/index`
- `POST /api/v1/rag/search`
- `POST /api/v1/rag/reset`

### 7.4 Web / Landing

- `POST /api/v1/web/search`
- `POST /api/v1/web/landing/analyze`

### 7.5 Export

- `POST /api/v1/export/docx`
- `POST /api/v1/export/md`
- `POST /api/v1/export/doc`

### 7.6 Meta / History / Health

- `GET /api/v1/meta/copy-form-guide`
- `POST /api/v1/history/threads`
- `GET /api/v1/history/threads`
- `GET /api/v1/history/threads/{thread_id}`
- `POST /api/v1/history/threads/{thread_id}/messages`
- `GET /health`
- `GET /docs`
- `GET /openapi.json`

---

## 8) 업로드 정책 및 검증

- 최대 파일 크기: 30MB
- 최대 파일 수: 10개/요청
- 허용 확장자: `.pdf`, `.doc`, `.docx`, `.txt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.png`, `.jpg`, `.jpeg`, `.webp`
- 파일 단위 성공/실패를 모두 반환해야 한다.
- 변환 실패 사유는 파일 단위로 명시되어야 한다.

---

## 9) 언어 및 정규화 정책

- 지원 언어 코드: `ko`, `en`, `ja`, `zh-CN`, `zh-TW`, `es`, `fr`, `de`, `pt-BR`, `vi`, `id`, `th`
- 별칭 입력 허용(예: `english`, `korean`, `ja-jp`, `pt-br`) 후 canonical code로 정규화
- 간편 생성 시 language 미입력이면 프롬프트 추론, 실패 시 `ko`

---

## 10) 에러 정책

### 10.1 공통 에러 응답

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "human-readable message",
    "details": {}
  }
}
```

### 10.2 표준 에러 코드

- `UNSUPPORTED_FILE_TYPE`
- `FILE_TOO_LARGE`
- `DOC_CONVERSION_FAILED`
- `EMBEDDING_FAILED`
- `VECTOR_DB_ERROR`
- `WEB_SEARCH_ERROR`
- `VALIDATION_ERROR`
- `TOO_MANY_FILES`
- `NOT_FOUND`
- `INTERNAL_ERROR`

---

## 11) 시스템 아키텍처

```text
Vue FE
  -> FastAPI Router (app/api/v1)
    -> Service Facade (app/services)
      -> LangGraph Flows (app/flows)
        -> Integrations (LLM, Docling, Tavily, Milvus, Playwright)
```

핵심 워크플로우:

- Copy Generation Graph: `prepare -> rag(optional) -> web(optional) -> generate`
- Copy Lite Graph: `parse -> landing_context -> infer objective/channel/language -> build_request -> generate`
- RAG Graph: `index/search/context build`
- Web Graph: `search`, `landing analyze`, `search then analyze`

---

## 12) 비기능 요구사항 (NFR)

- FE/BE 계약은 OpenAPI를 단일 기준으로 유지한다.
- Milvus 연결 실패 시 memory backend로 폴백해 서비스 연속성을 유지한다.
- Landing 분석은 Playwright 실패 시 requests 파서로 폴백한다.
- LLM 미사용/실패 시 mock 또는 heuristic 경로로 최소 기능을 유지한다.
- 중복 실행 방지를 위해 생성/업로드/분석 처리 중 FE 액션을 비활성화한다.

---

## 13) 프론트엔드 UX 요구

- 좌측: 스타일 선택, 파일 업로드+인덱싱, 랜딩 분석
- 우측: 대화형 브리프 입력, 결과 표시, 대화형 개선, 로그 확인
- 생성 결과는 항목별 복사/내보내기 동작을 지원해야 한다.
- 422 검증 에러는 사용자 이해 가능한 필드 단위 메시지로 노출해야 한다.
- reset 동작 시 결과/로그/랜딩/RAG 범위를 함께 초기화해야 한다.

---

## 14) 품질 검증 요구

필수 점검 항목:

- `GET /health`, `GET /docs`, `GET /openapi.json` 정상 응답
- `python -m pytest -q` 통과
- `cd frontend && npm run build` 통과
- 통합 검증 스크립트:
  - `python scripts/run_full_checks.py --provider openai --port 8012`
  - `python scripts/run_full_checks.py --provider ollama --ollama-model qwen3:8b --port 8013`

---

## 15) Definition of Done

- 구조화/간편 생성 API 모두 정상 동작한다.
- `assumptions`와 `normalized_request`가 간편 생성 응답에 포함된다.
- 문서 업로드 -> 인덱싱 -> RAG 검색 -> 생성 반영 경로가 동작한다.
- 랜딩 URL/Query 분석이 정상 동작한다.
- 내보내기(`md/doc/docx`)가 정상 다운로드된다.
- 히스토리 thread 생성/조회/append가 정상 동작한다.
- 공통 에러 포맷과 코드가 일관되게 반환된다.

---

## 16) 버전 메모

- v1.1: 입력/출력 스키마, 업로드 정책, 에러 코드, OpenAPI 계약 명확화
- v1.2: 자유형 프롬프트, 랜딩 분석, 멀티 포맷 출력, 히스토리 개념 확장
- v1.3:
  - 현재 구현 기준으로 API/스키마를 정합화 (`generate-lite`, `rag/reset`, `files/warmup-ocr`, `export/md|doc` 포함)
  - 자동 추론/정규화/assumptions 정책 명문화
  - 폴백 전략(Milvus/landing/LLM)과 검증 시나리오를 DoD에 반영
