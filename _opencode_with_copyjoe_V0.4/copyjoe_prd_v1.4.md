# Copyjoe PRD v1.4

빠른 요약: `copyjoe_prd_v1.4_onepager.md`

작성일: 2026-02-18  
문서 목적: 현재 구현 기준의 제품 요구사항과 API/아키텍처 계약을 v1.4로 고정

---

## 1) 제품 한 줄 정의

Copyjoe는 마케팅 팀이 **근거 기반(RAG + 웹 컨텍스트)**으로 전환형 카피를 빠르게 생성하고, 반복 개선까지 수행할 수 있게 돕는 카피 생성 플랫폼이다.

---

## 2) 배경과 문제

- 카피 작성은 빠른 실험 사이클이 중요하지만, 사람이 매번 새 문안을 만들기에는 시간이 오래 걸린다.
- 카피 품질이 작성자 역량에 크게 의존해 팀 단위 일관성이 떨어진다.
- 실제 운영 근거(내부 문서, 랜딩페이지 컨텍스트, 웹 정보)가 반영되지 않으면 설득력이 낮아진다.
- 기존 구조화 입력과 자유형 입력이 이원화되면 프론트/백엔드 운영 복잡도가 증가한다.

---

## 3) v1.4 핵심 방향

1. **생성 API 단일화**: `/api/v1/copy/generate` 하나로 통합
2. **서비스 단일화**: `CopyService` 하나에서 structured/prompt mode 모두 처리
3. **프롬프트 품질 안정화**: LLM 지시문 영어 중심 정비(특히 `qwen3:8b` 대응)
4. **근거 강화 유지**: 업로드 문서 RAG + 랜딩/웹 컨텍스트 결합
5. **계약 명확화**: 입력 모드별 스키마와 응답 타입을 명시적으로 관리

---

## 4) 핵심 사용자 / JTBD

- 퍼포먼스 마케터: CTR/전환 개선 문구를 짧은 주기로 실험하고 싶다.
- 콘텐츠 마케터: 채널별 톤과 구조를 유지하면서 대량 변형 카피를 만들고 싶다.
- AE/기획자: 고객 도메인 문서 근거를 반영해 설득 논리를 빠르게 제시하고 싶다.
- 소상공인/1인팀: 프롬프트 한 번으로 쓸 수 있는 결과를 얻고 싶다.

---

## 5) 범위 (In Scope)

### 5.1 카피 생성
- 목적(Objective): `brand_memory`, `click`, `add_to_cart`, `consultation`
- 스타일(Style): `head`, `body`, `cta`, `slogan`, `sns`, `description`
- 결과: 카피 본문 + `storyboard_outline` + `rationale` + `sources`

### 5.2 생성 모드
- Structured mode: 명시 필드 기반 생성 (`CopyGenerateRequest`)
- Prompt mode: 자유형 프롬프트 기반 생성/추론 (`CopyLiteRequest`)

### 5.3 근거 확장
- 문서 업로드 -> 인덱싱 -> RAG 검색
- 웹 검색(Tavily) + 랜딩 분석(Playwright/폴백)

### 5.4 협업 기능
- 결과 복사/내보내기(`.docx`, `.doc`, `.md`)
- 쓰레드 기반 히스토리 관리

---

## 6) 비범위 (Out of Scope)

- 자동 광고 집행/예산 최적화
- 이미지/영상 생성
- 다중 워크스페이스 권한 체계(조직/역할 기반)
- 실시간 동시편집(collaborative editing)

---

## 7) 도메인 데이터 계약

### 7.1 단일 생성 엔드포인트의 입력 계약

`POST /api/v1/copy/generate`는 아래 두 타입 중 하나를 받는다.

#### A) Structured mode (`CopyGenerateRequest`)
- `product_name`, `target_audience`, `pain_point`, `differentiator`, `tone`
- `objective`, `styles`, `channel`, `language`
- `web_search_mode`, `use_rag`, `top_k`, `rag_document_ids`

#### B) Prompt mode (`CopyLiteRequest`)
- `prompt` (최대 8000자)
- `styles`, `language`, `objective?`, `channel?`
- `landing_url?`, `landing_query?`
- `web_search_mode`, `use_rag`, `top_k`, `rag_document_ids?`
- `base_request?` (리파인 시 파싱 생략용)

### 7.2 생성 응답 계약

#### Structured response (`CopyGenerateResponse`)
- `head`, `body`, `cta`, `slogan`, `sns`, `description`
- `storyboard_outline`, `rationale`, `sources`

#### Prompt response (`CopyLiteResponse`)
- `assistant_message`
- `assumptions`
- `normalized_request` (구조화 요청으로 정규화된 결과)
- `result` (`CopyGenerateResponse`)

### 7.3 언어 코드

지원 코드:  
`ko`, `en`, `ja`, `zh-CN`, `zh-TW`, `es`, `fr`, `de`, `pt-BR`, `vi`, `id`, `th`

별칭 입력 허용(예: `english`, `korean`, `ja-jp`, `pt-br`).

---

## 8) API 명세 (v1.4)

### 8.1 Copy
- `POST /api/v1/copy/generate` (단일 생성 endpoint, dual-mode)

### 8.2 Files
- `POST /api/v1/files/upload`
- `POST /api/v1/files/warmup-ocr`

### 8.3 RAG
- `POST /api/v1/rag/index`
- `POST /api/v1/rag/search`
- `POST /api/v1/rag/reset`

### 8.4 Web
- `POST /api/v1/web/search`
- `POST /api/v1/web/landing/analyze`

### 8.5 Export
- `POST /api/v1/export/docx`
- `POST /api/v1/export/doc`
- `POST /api/v1/export/md`

### 8.6 Meta / History / Health
- `GET /api/v1/meta/copy-form-guide`
- `POST /api/v1/history/threads`
- `GET /api/v1/history/threads`
- `GET /api/v1/history/threads/{thread_id}`
- `POST /api/v1/history/threads/{thread_id}/messages`
- `GET /health`
- `GET /docs`
- `GET /openapi.json`

---

## 9) 업로드 및 RAG 정책

- 최대 파일 크기: 30MB
- 최대 파일 수: 10개/요청
- 허용 확장자: `.pdf`, `.doc`, `.docx`, `.txt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.png`, `.jpg`, `.jpeg`, `.webp`

대표 에러 코드:
- `UNSUPPORTED_FILE_TYPE`
- `FILE_TOO_LARGE`
- `DOC_CONVERSION_FAILED`
- `EMBEDDING_FAILED`
- `VECTOR_DB_ERROR`
- `WEB_SEARCH_ERROR`

---

## 10) 사용자 플로우

### 10.1 프롬프트 중심 생성(프론트 기본)
1. 사용자가 자연어 브리프 입력
2. 시스템이 objective/channel/language 추론
3. 필요 시 랜딩 컨텍스트/문서 RAG 결합
4. 카피 생성 + assumptions + normalized request 반환

### 10.2 문서 근거 생성
1. 파일 업로드
2. RAG 인덱싱
3. 생성 시 `rag_document_ids`로 검색 범위 제한
4. `sources`로 근거 추적

### 10.3 개선 반복(refine)
1. 이전 결과 + 피드백 입력
2. `base_request` 재사용으로 파싱 비용 절감
3. 개선 버전 재생성

---

## 11) 프론트 요구사항

- 기본 호출은 `/api/v1/copy/generate` 단일 endpoint 사용
- 대화형 입력/개선 입력에서 중복 요청 방지(loading lock)
- 422 필드 에러를 사용자에게 읽을 수 있는 메시지로 표기
- 업로드/인덱싱 결과를 성공/실패 단위로 피드백
- 랜딩 분석 결과를 바로 생성 흐름에 재주입 가능해야 함

---

## 12) 백엔드 아키텍처 원칙

- API는 I/O 계약과 DI 중심
- 서비스는 도메인 facade 역할
- 오케스트레이션은 LangGraph(flow)에서 수행
- 외부 연동은 integration 계층으로 고립
- 스키마는 `app/schemas/*`에서 단일 관리

현재 핵심 구현 포인트:
- 단일 서비스: `app/services/copy_service.py`
- 생성 그래프: `CopyGenerationGraph`, `CopyLiteGenerationGraph`
- 의존성 주입: `app/api/deps.py`

---

## 13) 모델/품질 전략

- Provider: OpenAI 또는 Ollama
- 기본 Ollama 채팅 모델: `qwen3:8b`
- 프롬프트 지시문은 영어 중심으로 정리해 소형 모델 추종성 개선
- Structured output 강제(`with_structured_output`)로 스키마 안정성 확보
- 텍스트 안정화 로직으로 mixed-script/노이즈 출력 억제

---

## 14) 비기능 요구사항

- `/health`, `/docs`, `/openapi.json` 상시 접근 가능
- Milvus 미사용 환경에서도 memory backend로 동작 가능
- 랜딩 분석 실패 시 폴백 경로 제공
- 테스트/빌드 기준:
  - `python -m pytest -q`
  - `cd frontend && npm run build`

---

## 15) 수용 기준 (Definition of Done)

- `/api/v1/copy/generate` 하나로 structured/prompt mode 모두 정상 동작
- 프론트 생성/개선 플로우가 단일 endpoint로 동작
- RAG 업로드/인덱싱/검색/근거 반영이 유지
- 랜딩 분석 기반 생성이 유지
- export(`docx/doc/md`)가 정상 다운로드
- history thread 생성/조회/append가 정상 동작
- OpenAPI 계약 및 스모크 테스트 통과

---

## 16) 버전 메모

- v1.4 변경 핵심
  - 생성 endpoint를 `/api/v1/copy/generate`로 단일화
  - `CopyLiteService`를 제거하고 `CopyService`로 통합
  - 프론트/스크립트/테스트의 `generate-lite` 참조 제거
  - 용어를 `prompt mode` 중심으로 정리
