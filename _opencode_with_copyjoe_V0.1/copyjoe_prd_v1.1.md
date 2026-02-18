# Copyjoe PRD v1.1

## 1) 제품 한 줄 정의
카피조(Copyjoe)는 고객의 행동(기억, 클릭, 장바구니, 상담 신청)을 유도하는 설득 문장을 생성하는 마케팅 카피 생성 도구다.

## 2) 문제 정의와 목표
- 마케터/기획자는 매번 새로운 카피를 빠르게 만들기 어렵다.
- 카피 품질이 작성자 역량에 따라 편차가 크다.
- 문서 기반 근거(RAG)와 웹 최신 정보가 반영되지 않는 경우가 많다.

### 목표
- 카피 생성 시간을 단축한다.
- 카피 품질을 구조화된 입력으로 표준화한다.
- 파일 업로드 기반 RAG와 웹 서치(Tavily)를 통해 근거 기반 카피를 만든다.

## 3) 핵심 사용자
- 퍼포먼스 마케터
- 콘텐츠 마케터
- AE/기획자
- 1인 사업자/소상공인

## 4) 핵심 기능 (필수)
1. 설득 문장 생성
   - 목적: `brand_memory`, `click`, `add_to_cart`, `consultation`
   - 스타일: `head`, `body`, `cta`, `slogan`, `sns`, `description`
2. 스토리보드용 콘티 초안 자동 생성
3. 복사 버튼 동작
4. Word(.docx) 내보내기
5. 파일 업로드
   - 지원 형식: `docx`, `doc`, `ppt`, `pdf`, `png`, `jpg`, `jpeg`, `webp`
6. 업로드 파일 문서 변환: Docling 사용
7. 임베딩: `qwen3-embedding`
8. 벡터 DB: Milvus
9. 웹 서치 모드: Tavily ON/OFF 선택

## 5) 입력/출력 스키마 (필수 추가)

### 입력 스키마
- `product_name`: string
- `target_audience`: string
- `pain_point`: string
- `differentiator`: string
- `tone`: string (예: 신뢰형, 도전형, 친근형)
- `objective`: enum (`brand_memory` | `click` | `add_to_cart` | `consultation`)
- `styles`: enum array (`head` | `body` | `cta` | `slogan` | `sns` | `description`)
- `channel`: string (예: 상세페이지, 인스타, 검색광고)
- `language`: string (기본 `ko`)
- `web_search_mode`: boolean
- `use_rag`: boolean
- `top_k`: number (기본 5)

### 출력 스키마
- `head`: string
- `body`: string
- `cta`: string
- `slogan`: string
- `sns`: string
- `description`: string
- `storyboard_outline`: string[]
- `rationale`: string
- `sources`: array (웹/RAG 사용 시 출처)

## 6) OpenAPI 기반 FE/BE 연동
FastAPI를 사용해 OpenAPI를 단일 계약으로 사용한다.

### 엔드포인트 초안
- `POST /api/v1/copy/generate`
  - 설명: 카피 생성 및 콘티 초안 생성
- `POST /api/v1/files/upload`
  - 설명: 파일 업로드 및 변환 텍스트 저장
- `POST /api/v1/rag/index`
  - 설명: 문서 chunk 임베딩 후 Milvus 인덱싱
- `POST /api/v1/rag/search`
  - 설명: 관련 컨텍스트 검색
- `POST /api/v1/web/search`
  - 설명: Tavily 검색
- `POST /api/v1/export/docx`
  - 설명: 생성 결과를 Word로 내보내기
- `GET /health`
  - 설명: 헬스체크

### 계약/개발 규칙
- FE는 OpenAPI로 타입/클라이언트를 자동 생성한다.
- FE는 수기 타입 정의 대신 생성 타입을 우선 사용한다.
- 에러 포맷은 공통 스키마로 통일한다.

## 7) RAG 처리 파이프라인
1. 업로드 수신
2. Docling 변환
3. 텍스트 정제
4. Chunking
5. qwen3-embedding 임베딩
6. Milvus 저장
7. 질의 시 top-k 검색
8. 검색 결과를 생성 프롬프트에 주입

## 8) 파일 업로드 정책 (필수 추가)
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

## 9) 프론트엔드 구조 (Vue3)

### 페이지
- `IndexPage.vue` (메인 화면)

### copyjoe 폴더
- `sections/PromptSection.vue`
- `sections/GenerationSection.vue`
- `models-service/types.ts`
- `models-service/service.ts`
- `models-service/WebAgentService.ts`
- `components/PromptOption.vue`
- `components/LoadingSpinner.vue`
- `components/GenerateResult.vue`
- `components/ExportDialog.vue`

### FE 기능 요구
- PromptSection
  - 목적/스타일/톤/채널 선택
  - Tavily 모드 토글
  - 파일 업로드
- GenerationSection
  - 결과 렌더링
  - 복사 버튼
  - Word export 버튼

## 10) 백엔드 구조 (Python)
- `app/main.py` (FastAPI entry)
- `app/api/v1/*.py` (라우터)
- `app/schemas/*.py` (Pydantic)
- `app/services/copy_service.py`
- `app/services/rag_service.py`
- `app/services/web_search_service.py`
- `app/services/export_service.py`
- `app/integrations/docling_client.py`
- `app/integrations/milvus_client.py`
- `app/integrations/langfuse_client.py`

## 11) 기술 스택

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
- qwen3-vl:32b (예정)
- qwen3-vl:8b (예정)
- gpt-oss (예정)

### Frontend
- vue
- vue-router
- vue-i18n
- typescript
- vite-svg-loader
- axios
- pinia

## 12) 수용 기준 (Definition of Done)
- 카피 생성 요청 시 선택한 스타일별 결과가 반환된다.
- 복사 버튼이 모든 결과 블록에서 동작한다.
- Word(.docx) export가 정상 다운로드된다.
- 업로드 파일이 Docling으로 변환되고, RAG 인덱싱이 완료된다.
- Milvus 검색 결과가 생성 품질에 반영된다.
- Tavily 모드 ON/OFF가 실제 생성 결과에 반영된다.
- OpenAPI 문서(`/docs`, `/openapi.json`)가 노출된다.

## 13) 버전 메모
- v1.1에서 용어/오타를 정리하고, 입력/출력 스키마, 업로드 정책, 에러 코드, OpenAPI 계약 섹션을 추가했다.
