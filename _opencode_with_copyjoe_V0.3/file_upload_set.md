# File Upload Setup (Backend + OCR Models)

This document summarizes what is currently implemented for file upload, conversion, OCR, indexing, and timeout behavior.

## 1) End-to-end flow

1. Frontend uploads files to `POST /api/v1/files/upload`.
2. Backend validates count, extension, and size.
3. Each file is converted to text.
4. Successful conversions are stored in `DocumentStore` with a generated `document_id`.
5. Frontend then calls `POST /api/v1/rag/index` using those `document_id` values.
6. Copy generation reads RAG context via similarity search.

Primary code paths:

- `app/flows/file_upload_graph.py`
- `app/integrations/docling_client.py`
- `app/services/document_store.py`
- `app/api/v1/rag.py`

## 2) Upload validation rules

Defined in `Settings` (`app/core/config.py`):

- max file count: `max_file_count` (default `10`)
- max file size: `max_file_size_mb` (default `30`)
- allowed extensions:
  - `.pdf`, `.doc`, `.docx`, `.txt`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.png`, `.jpg`, `.jpeg`, `.webp`

Failure codes returned per file:

- `UNSUPPORTED_FILE_TYPE`
- `FILE_TOO_LARGE`
- `DOC_CONVERSION_FAILED`

Per-file success visibility fields:

- `conversion_engine` (e.g. `image_rapidocr`, `image_smoldocling`, `pdf_rapidocr`, `pdf_easyocr`, `pdf_smoldocling`, `pdf_pypdf`)
- `text_length`
- `text_preview` (first 120 chars)

## 3) Conversion strategy by file type

Implemented in `app/integrations/docling_client.py`.

### PDF (`.pdf`)

Current strategy is performance-first:

1. Try fast extraction with `pypdf` first.
2. Run OCR only when extracted text is too short (`pdf_ocr_min_chars`) or empty.
3. Decide whether to run SmolDocling VLM first using `pdf_layout_model_strategy`:
   - `off`: do not use VLM for PDF
   - `auto`: use VLM when image/table-heavy layout is detected
   - `smoldocling`: always try VLM first for PDF
4. OCR engine order depends on `pdf_ocr_strategy`:
   - `off`: no OCR
   - `rapid`: RapidOCR only
   - `easy`: EasyOCR only
   - `hybrid`: RapidOCR then EasyOCR

Default values:

- `pdf_ocr_strategy = "rapid"`
- `pdf_ocr_min_chars = 180`
- `pdf_layout_model_strategy = "off"`
- `pdf_vlm_preset = "smoldocling"`
- `pdf_vlm_device = "auto"`

### Images (`.png`, `.jpg`, `.jpeg`, `.webp`)

- Uses `image_processing_strategy` policy:
  - `rapid`: RapidOCR only
  - `smoldocling`: SmolDocling VLM only
  - `hybrid`: RapidOCR first, then SmolDocling fallback
- If all selected paths fail, upload returns conversion failure for that file.

Default is `rapid` (fast/stable setup).

### Other formats

- `.txt`, `.md`, `.csv`, `.json`: direct text read
- `.docx`: `python-docx`
- `.xlsx`: `openpyxl`
- `.xls`: `xlrd`
- `.ppt`, `.pptx`: `python-pptx`

## 4) OCR models currently used

### RapidOCR stack

Used for image OCR and for PDF OCR when strategy includes `rapid`.

Main ONNX models:

- `ch_PP-OCRv4_det_infer.onnx` (text detection)
- `ch_ppocr_mobile_v2.0_cls_infer.onnx` (orientation/classification)
- `ch_PP-OCRv4_rec_infer.onnx` (text recognition)

### EasyOCR stack

Used for PDF OCR when strategy includes `easy`.

Typical model files:

- `craft_mlt_25k.pth`
- `korean_g2.pth`
- `latin_g2.pth`

### SmolDocling VLM usage in upload flow

- Picture-description SmolVLM path is not used.
- Docling VLM conversion path is used when `image_processing_strategy` includes `smoldocling`.
- PDF path can also use SmolDocling VLM first when `pdf_layout_model_strategy` allows it.

## 5) Performance controls already applied

1. Lazy initialization of Docling converters.
2. Fast PDF first-pass with `pypdf` before OCR.
3. Fast OCR pipeline options disable non-essential enrichments.
4. Image path supports RapidOCR/SmolDocling strategy selection.
5. Frontend upload request timeout increased to 10 minutes.

Related frontend setting:

- `frontend/src/copyjoe/models-service/service.ts` -> upload request timeout `600000` ms.

Warm-up endpoint:

- `POST /api/v1/files/warmup-ocr`
- Recommended once after server start to reduce first-request latency.

## 6) Dependency and version management

Pinned dependencies:

- `requirements.txt` includes `docling[easyocr,rapidocr]==2.73.1`

Constraint file for deterministic OCR stack:

- `constraints.txt`
  - `docling==2.73.1`
  - `easyocr==1.7.2`
  - `rapidocr==3.6.0`
  - `onnxruntime==1.24.1`

Dev install uses constraints via:

- `requirements-dev.txt` includes `-c constraints.txt`

## 7) Runtime tuning (recommended)

Configure in `.env`:

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

Suggested presets:

- fastest: `PDF_OCR_STRATEGY=off`
- balanced: `PDF_OCR_STRATEGY=rapid` (default)
- quality-first: `PDF_OCR_STRATEGY=hybrid`
- image fast: `IMAGE_PROCESSING_STRATEGY=rapid`
- image fallback-safe: `IMAGE_PROCESSING_STRATEGY=hybrid` (RapidOCR first)
- image quality-first (optional): `IMAGE_PROCESSING_STRATEGY=smoldocling` + `IMAGE_VLM_DEVICE=cuda`

Note:

- For real GPU acceleration with SmolDocling, install a CUDA-enabled PyTorch runtime.

## 8) Why source may look unchanged after re-index

RAG indexing is additive. Previously indexed chunks remain unless storage is reset.

Effects:

- New uploads may not always appear as top source if old chunks score higher.
- To verify new data is searchable, test with a query that uniquely matches the new file.

## 9) Code placement map

API layer:

- upload endpoint: `app/api/v1/files.py` (`POST /files/upload`)
- OCR warm-up endpoint: `app/api/v1/files.py` (`POST /files/warmup-ocr`)

Dependency wiring:

- settings + service singletons: `app/api/deps.py`
- OCR/file runtime config keys: `app/core/config.py`

Upload orchestration:

- upload graph (validation -> save -> convert -> store): `app/flows/file_upload_graph.py`
- file service facade used by routes: `app/services/file_service.py`
- converted text/document-id storage: `app/services/document_store.py`

Conversion/OCR engines:

- all parser + OCR + VLM routing logic: `app/integrations/docling_client.py`
- per-file upload response schema: `app/schemas/file.py`

RAG indexing/search path (after upload):

- index/search APIs: `app/api/v1/rag.py`
- reset API: `app/api/v1/rag.py` (`POST /rag/reset`)
- RAG graph workflow: `app/flows/rag_workflow/graph.py`
- RAG nodes (index/chunk/context): `app/flows/rag_workflow/nodes.py`
- vector DB integration: `app/integrations/milvus_client.py`

Frontend upload call and timeout:

- upload API call + timeout(600000ms): `frontend/src/copyjoe/models-service/service.ts`

Related tests/docs:

- docling conversion tests: `tests/test_docling_client.py`
- ops documentation (EN): `file_upload_set.md`
- ops documentation (KO): `file_upload_set_ko.md`
