from pathlib import Path

import pytest
from pypdf import PdfWriter

from app.integrations.docling_client import DoclingClient


def test_pdf_without_text_layer_reports_ocr_requirement(tmp_path: Path) -> None:
    pdf_path = tmp_path / "blank_scan_like.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with pdf_path.open("wb") as handle:
        writer.write(handle)

    client = DoclingClient()
    client._converter = None
    client._pdf_rapidocr_converter = None
    client._pdf_easyocr_converter = None
    client._converter_initialized = True
    client._pdf_rapidocr_initialized = True
    client._pdf_easyocr_initialized = True

    with pytest.raises(RuntimeError, match="OCR is required"):
        client.convert_to_text(pdf_path)


def test_plain_text_file_uses_fallback_reader(tmp_path: Path) -> None:
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("hello docling", encoding="utf-8")

    client = DoclingClient()
    client._converter = None
    client._pdf_rapidocr_converter = None
    client._pdf_easyocr_converter = None
    client._converter_initialized = True
    client._pdf_rapidocr_initialized = True
    client._pdf_easyocr_initialized = True

    assert client.convert_to_text(txt_path) == "hello docling"


def test_pdf_skips_ocr_when_default_text_is_sufficient(tmp_path: Path) -> None:
    pdf_path = tmp_path / "synthetic.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    client = DoclingClient(
        pdf_ocr_strategy="hybrid",
        pdf_ocr_min_chars=50,
        pdf_layout_model_strategy="off",
    )
    client._extract_pdf_snapshot = lambda _: (  # type: ignore[method-assign]
        "a" * 200,
        {"pages": 1, "image_count": 0, "table_like_lines": 0, "total_lines": 1},
    )

    def fake_convert_with_docling(_: object, __: Path) -> str:
        raise AssertionError("OCR converter should not be called when default text is sufficient")

    client._convert_with_docling = fake_convert_with_docling  # type: ignore[method-assign]

    text = client.convert_to_text(pdf_path)

    assert text == "a" * 200
    assert client._pdf_ocr_engine == "pypdf"


def test_pdf_auto_layout_uses_smoldocling_when_images_detected(tmp_path: Path) -> None:
    pdf_path = tmp_path / "with-image.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    client = DoclingClient(
        pdf_layout_model_strategy="auto",
        pdf_ocr_strategy="rapid",
    )
    client._extract_pdf_snapshot = lambda _: (  # type: ignore[method-assign]
        "plain text",
        {"pages": 1, "image_count": 2, "table_like_lines": 0, "total_lines": 10},
    )
    client._pdf_vlm_converter = object()
    client._pdf_vlm_initialized = True

    def fake_convert_with_docling(converter: object, _: Path) -> str:
        if converter is client._pdf_vlm_converter:
            return "vlm result"
        raise AssertionError("OCR converters should not be used when VLM succeeds")

    client._convert_with_docling = fake_convert_with_docling  # type: ignore[method-assign]

    assert client.convert_to_text(pdf_path) == "vlm result"


def test_pdf_auto_layout_uses_ocr_when_no_images_or_tables(tmp_path: Path) -> None:
    pdf_path = tmp_path / "plain.pdf"
    pdf_path.write_bytes(b"%PDF-1.4")

    client = DoclingClient(
        pdf_layout_model_strategy="auto",
        pdf_ocr_strategy="rapid",
        pdf_ocr_min_chars=180,
    )
    client._extract_pdf_snapshot = lambda _: (  # type: ignore[method-assign]
        "plain text enough" * 30,
        {"pages": 1, "image_count": 0, "table_like_lines": 0, "total_lines": 10},
    )
    client._ensure_pdf_vlm_converter = lambda: (_ for _ in ()).throw(  # type: ignore[method-assign]
        AssertionError("VLM should not be initialized for plain-text PDF")
    )
    client._convert_pdf_with_ocr_policy = lambda text, _path: text  # type: ignore[method-assign]

    output = client.convert_to_text(pdf_path)

    assert output.startswith("plain text enough")


def test_image_hybrid_uses_rapid_first_when_rapid_has_text(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake")

    client = DoclingClient(image_processing_strategy="hybrid")
    client._image_vlm_converter = object()
    client._image_rapidocr_converter = object()
    client._image_vlm_initialized = True
    client._image_rapidocr_initialized = True

    call_order: list[str] = []

    def fake_convert_with_docling(converter: object, _: Path) -> str:
        if converter is client._image_vlm_converter:
            call_order.append("vlm")
            return "vlm text"
        if converter is client._image_rapidocr_converter:
            call_order.append("rapid")
            return "rapid text"
        return ""

    client._convert_with_docling = fake_convert_with_docling  # type: ignore[method-assign]

    assert client.convert_to_text(image_path) == "rapid text"
    assert call_order == ["rapid"]


def test_image_hybrid_falls_back_to_smoldocling_when_rapid_empty(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"fake")

    client = DoclingClient(image_processing_strategy="hybrid")
    client._image_vlm_converter = object()
    client._image_rapidocr_converter = object()
    client._image_vlm_initialized = True
    client._image_rapidocr_initialized = True

    def fake_convert_with_docling(converter: object, _: Path) -> str:
        if converter is client._image_rapidocr_converter:
            return ""
        if converter is client._image_vlm_converter:
            return "vlm text"
        return ""

    client._convert_with_docling = fake_convert_with_docling  # type: ignore[method-assign]

    assert client.convert_to_text(image_path) == "vlm text"


def test_image_smoldocling_strategy_raises_when_vlm_empty(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.jpg"
    image_path.write_bytes(b"fake")

    client = DoclingClient(image_processing_strategy="smoldocling")
    client._image_vlm_converter = object()
    client._image_vlm_initialized = True

    client._convert_with_docling = lambda *_args: ""  # type: ignore[method-assign]

    with pytest.raises(RuntimeError, match="SmolDocling VLM"):
        client.convert_to_text(image_path)


def test_warm_up_returns_success_payload() -> None:
    client = DoclingClient(
        pdf_ocr_strategy="hybrid",
        image_processing_strategy="hybrid",
        pdf_layout_model_strategy="auto",
    )

    client._ensure_converter = lambda: setattr(client, "_converter", object())  # type: ignore[method-assign]
    client._ensure_image_vlm_converter = lambda: setattr(client, "_image_vlm_converter", object())  # type: ignore[method-assign]
    client._ensure_image_rapidocr_converter = lambda: setattr(client, "_image_rapidocr_converter", object())  # type: ignore[method-assign]
    client._ensure_pdf_rapidocr_converter = lambda: setattr(client, "_pdf_rapidocr_converter", object())  # type: ignore[method-assign]
    client._ensure_pdf_easyocr_converter = lambda: setattr(client, "_pdf_easyocr_converter", object())  # type: ignore[method-assign]

    client._create_warmup_image = lambda _: True  # type: ignore[method-assign]
    client._create_warmup_pdf = lambda _: True  # type: ignore[method-assign]
    client._convert_with_docling = lambda *_args: "ok"  # type: ignore[method-assign]

    payload = client.warm_up()

    assert payload["ok"] is True
    assert payload["pdf_layout_model_strategy"] == "auto"
    assert payload["pdf_vlm_preset"] == "smoldocling"
    assert payload["pdf_vlm_device"] == "auto"
    warmed_components = payload["warmed_components"]
    assert isinstance(warmed_components, list)
    assert set(warmed_components) >= {
        "docling_default",
        "image_smoldocling",
        "image_rapidocr",
        "pdf_smoldocling",
        "pdf_rapidocr",
        "pdf_easyocr",
    }
    assert payload["failed_components"] == []
