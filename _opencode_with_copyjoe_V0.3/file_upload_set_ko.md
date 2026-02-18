# 파일 업로드 설정 (백엔드 + OCR 모델)

이 문서는 현재 구현된 파일 업로드, 문서 변환, OCR, 인덱싱, 타임아웃 처리 방식을 정리합니다.

## 1) 전체 처리 흐름

1. 프론트에서 `POST /api/v1/files/upload`로 파일 업로드
2. 백엔드에서 파일 개수/확장자/크기 검증
3. 파일별 텍스트 변환 수행
4. 성공한 파일은 `DocumentStore`에 `document_id`와 함께 저장
5. 프론트에서 `POST /api/v1/rag/index`로 `document_id` 인덱싱 요청
6. 카피 생성 시 RAG 유사도 검색 결과를 source로 사용

주요 코드 경로:

- `app/flows/file_upload_graph.py`
- `app/integrations/docling_client.py`
- `app/services/document_store.py`
- `app/api/v1/rag.py`

## 2) 업로드 검증 규칙

설정 위치: `app/core/config.py`

- 최대 파일 개수: `max_file_count` (기본 `10`)
- 최대 파일 크기: `max_file_size_mb` (기본 `30`)
- 허용 확장자:
  - `.pdf`, `.doc`, `.docx`, `.txt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.png`, `.jpg`, `.jpeg`, `.webp`

파일 단위 실패 코드:

- `UNSUPPORTED_FILE_TYPE`
- `FILE_TOO_LARGE`
- `DOC_CONVERSION_FAILED`

파일별 성공 확인 필드:

- `conversion_engine` (예: `image_rapidocr`, `image_smoldocling`, `pdf_rapidocr`, `pdf_easyocr`, `pdf_smoldocling`, `pdf_pypdf`)
- `text_length`
- `text_preview` (앞 120자)

## 3) 파일 타입별 변환 전략

구현 위치: `app/integrations/docling_client.py`

### PDF (`.pdf`)

현재는 속도 우선 전략입니다.

1. 먼저 `pypdf`로 빠른 텍스트 추출 시도
2. 추출 텍스트가 짧거나 비어 있으면 OCR 수행 (`pdf_ocr_min_chars` 기준)
3. `pdf_layout_model_strategy`로 SmolDocling VLM 선적용 여부 결정
   - `off`: PDF에서 VLM 미사용
   - `auto`: 그림/표가 감지되면 VLM 우선 사용
   - `smoldocling`: PDF에서 항상 VLM 우선 사용
4. OCR 엔진 순서는 `pdf_ocr_strategy`에 따름
   - `off`: OCR 미사용
   - `rapid`: RapidOCR만 사용
   - `easy`: EasyOCR만 사용
   - `hybrid`: RapidOCR 후 EasyOCR

기본값:

- `pdf_ocr_strategy = "rapid"`
- `pdf_ocr_min_chars = 180`
- `pdf_layout_model_strategy = "off"`
- `pdf_vlm_preset = "smoldocling"`
- `pdf_vlm_device = "auto"`

### 이미지 (`.png`, `.jpg`, `.jpeg`, `.webp`)

- `image_processing_strategy` 정책에 따라 동작
  - `rapid`: RapidOCR만 사용
  - `smoldocling`: SmolDocling VLM만 사용
  - `hybrid`: RapidOCR 우선, 실패 시 SmolDocling fallback
- 선택된 경로가 모두 실패하면 해당 파일은 변환 실패 처리

기본값은 속도/안정성 우선 구성인 `rapid`

### 기타 포맷

- `.txt`, `.md`, `.csv`, `.json`: 직접 텍스트 읽기
- `.docx`: `python-docx`
- `.xlsx`: `openpyxl`
- `.xls`: `xlrd`
- `.ppt`, `.pptx`: `python-pptx`

## 4) 현재 사용 중인 OCR 모델

### RapidOCR 스택

이미지 OCR, 그리고 PDF에서 `rapid` 전략일 때 사용됩니다.

주요 ONNX 모델:

- `ch_PP-OCRv4_det_infer.onnx` (텍스트 영역 검출)
- `ch_ppocr_mobile_v2.0_cls_infer.onnx` (방향/분류)
- `ch_PP-OCRv4_rec_infer.onnx` (텍스트 인식)

### EasyOCR 스택

PDF에서 `easy` 전략일 때 사용됩니다.

주요 모델 파일:

- `craft_mlt_25k.pth`
- `korean_g2.pth`
- `latin_g2.pth`

### 업로드 경로에서 SmolDocling 사용 방식

- picture-description용 SmolVLM 경로는 사용하지 않음
- `image_processing_strategy`에 `smoldocling`이 포함되면 이미지에서 Docling VLM 변환 경로를 사용
- `pdf_layout_model_strategy` 설정에 따라 PDF도 Docling VLM을 선적용할 수 있음

## 5) 적용된 성능 최적화

1. Docling 컨버터 지연 초기화
2. PDF `pypdf` 선처리 후 조건부 OCR
3. OCR 파이프라인에서 불필요한 enrichment 비활성화
4. 이미지 경로 RapidOCR/SmolDocling 전략 선택 지원
5. 프론트 업로드 요청 타임아웃 10분으로 확장

관련 프론트 설정:

- `frontend/src/copyjoe/models-service/service.ts` 업로드 timeout `600000` ms

웜업 엔드포인트:

- `POST /api/v1/files/warmup-ocr`
- 서버 시작 직후 1회 호출하면 첫 업로드의 모델 로딩 지연을 줄일 수 있음

## 6) 의존성/버전 관리

고정 의존성:

- `requirements.txt`에 `docling[easyocr,rapidocr]==2.73.1` 명시

OCR 스택 고정 파일:

- `constraints.txt`
  - `docling==2.73.1`
  - `easyocr==1.7.2`
  - `rapidocr==3.6.0`
  - `onnxruntime==1.24.1`

개발 설치 시 constraints 적용:

- `requirements-dev.txt`에 `-c constraints.txt` 포함

## 7) 런타임 튜닝 권장값

`.env`에서 설정 가능:

```env
PDF_OCR_STRATEGY=rapid
PDF_OCR_MIN_CHARS=180
PDF_LAYOUT_MODEL_STRATEGY=off
PDF_VLM_PRESET=smoldocling
PDF_VLM_DEVICE=auto
IMAGE_PROCESSING_STRATEGY=hybrid
IMAGE_VLM_PRESET=smoldocling
IMAGE_VLM_DEVICE=auto
```

권장 프리셋:

- 가장 빠름: `PDF_OCR_STRATEGY=off`
- 균형형: `PDF_OCR_STRATEGY=rapid` (기본)
- 품질 우선: `PDF_OCR_STRATEGY=hybrid`
- 이미지 속도 우선: `IMAGE_PROCESSING_STRATEGY=rapid`
- 이미지 안정 우선: `IMAGE_PROCESSING_STRATEGY=hybrid` (RapidOCR 우선)
- 이미지 품질 우선(선택, GPU): `IMAGE_PROCESSING_STRATEGY=smoldocling` + `IMAGE_VLM_DEVICE=cuda`

참고:

- SmolDocling을 실제 GPU 가속으로 사용하려면 CUDA 지원 PyTorch 런타임이 설치되어 있어야 합니다.

## 8) 인덱싱 후 source가 그대로처럼 보이는 이유

RAG 인덱싱은 누적(additive) 방식이라 기존 청크가 남아 있습니다.

영향:

- 새 문서를 올려도 기존 문서 점수가 높으면 top source가 기존 문서로 보일 수 있음
- 새 문서 반영 여부는 해당 문서 고유 키워드로 검색해 `metadata.file_name`으로 확인 권장

## 9) 코드 배치 맵

API 계층:

- 업로드 엔드포인트: `app/api/v1/files.py` (`POST /files/upload`)
- OCR 웜업 엔드포인트: `app/api/v1/files.py` (`POST /files/warmup-ocr`)

의존성 연결:

- settings + 서비스 싱글톤: `app/api/deps.py`
- OCR/파일 런타임 설정 키: `app/core/config.py`

업로드 오케스트레이션:

- 업로드 그래프(검증 -> 저장 -> 변환 -> 저장소 반영): `app/flows/file_upload_graph.py`
- 라우트에서 사용하는 파일 서비스: `app/services/file_service.py`
- 변환 텍스트/document_id 저장소: `app/services/document_store.py`

변환/OCR 엔진:

- 파서 + OCR + VLM 라우팅 로직: `app/integrations/docling_client.py`
- 파일 업로드 응답 스키마: `app/schemas/file.py`

업로드 이후 RAG 인덱싱/검색 경로:

- 인덱싱/검색 API: `app/api/v1/rag.py`
- 리셋 API: `app/api/v1/rag.py` (`POST /rag/reset`)
- RAG 그래프 워크플로우: `app/flows/rag_workflow/graph.py`
- RAG 노드(인덱싱/청크/컨텍스트): `app/flows/rag_workflow/nodes.py`
- 벡터DB 연동: `app/integrations/milvus_client.py`

프론트 업로드 호출 및 타임아웃:

- 업로드 API 호출 + timeout(600000ms): `frontend/src/copyjoe/models-service/service.ts`

관련 테스트/문서:

- docling 변환 테스트: `tests/test_docling_client.py`
- 운영 문서(영문): `file_upload_set.md`
- 운영 문서(국문): `file_upload_set_ko.md`
