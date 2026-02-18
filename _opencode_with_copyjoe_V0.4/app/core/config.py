from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


COPY_GENERATION_TEMPERATURE = 0.7
COPY_GENERATION_MAX_TOKENS = 4000
COPY_GENERATION_MIN_TOKENS = 900
COPY_GENERATION_TOKENS_PER_STYLE = 420
COPY_PARSER_TEMPERATURE = 0.4
COPY_PARSER_MAX_TOKENS = 1000
COPY_CONTEXT_BASE_CHARS = 1400
COPY_CONTEXT_CHARS_PER_STYLE = 900
COPY_CONTEXT_MAX_CHARS = 9000
COPY_REFINEMENT_CONTEXT_MAX_CHARS = 2400


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Copyjoe API"
    app_version: str = "1.1.0"
    environment: str = "local"
    api_v1_prefix: str = "/api/v1"

    llm_provider: str = "openai"
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "qwen3:8b"
    ollama_embedding_model: str = "qwen3-embedding:4b"

    tavily_api_key: str | None = None

    milvus_uri: str | None = None
    milvus_collection: str = "copyjoe_docs"

    force_mock_mode: bool = False

    max_file_size_mb: int = 30
    max_file_count: int = 10

    upload_dir: str = "data/uploads"
    converted_dir: str = "data/converted"

    landing_request_timeout_sec: int = 18
    landing_subprocess_timeout_buffer_sec: int = 4
    landing_network_idle_wait_ms: int = 700
    landing_fallback_timeout_sec: int = 8
    landing_cache_ttl_sec: int = 300
    pdf_ocr_strategy: str = "rapid"
    pdf_ocr_min_chars: int = 180
    pdf_layout_model_strategy: str = "off"
    pdf_vlm_preset: str = "smoldocling"
    pdf_vlm_device: str = "auto"
    image_processing_strategy: str = "rapid"
    image_vlm_preset: str = "smoldocling"
    image_vlm_device: str = "auto"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_extensions(self) -> tuple[str, ...]:
        return (
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".png",
            ".jpg",
            ".jpeg",
            ".webp",
        )

    @property
    def copy_generation_temperature(self) -> float:
        return COPY_GENERATION_TEMPERATURE

    @property
    def copy_generation_max_tokens(self) -> int:
        return COPY_GENERATION_MAX_TOKENS

    @property
    def copy_generation_min_tokens(self) -> int:
        return COPY_GENERATION_MIN_TOKENS

    @property
    def copy_generation_tokens_per_style(self) -> int:
        return COPY_GENERATION_TOKENS_PER_STYLE

    @property
    def copy_parser_temperature(self) -> float:
        return COPY_PARSER_TEMPERATURE

    @property
    def copy_parser_max_tokens(self) -> int:
        return COPY_PARSER_MAX_TOKENS

    @property
    def copy_context_base_chars(self) -> int:
        return COPY_CONTEXT_BASE_CHARS

    @property
    def copy_context_chars_per_style(self) -> int:
        return COPY_CONTEXT_CHARS_PER_STYLE

    @property
    def copy_context_max_chars(self) -> int:
        return COPY_CONTEXT_MAX_CHARS

    @property
    def copy_refinement_context_max_chars(self) -> int:
        return COPY_REFINEMENT_CONTEXT_MAX_CHARS

    @property
    def should_mock(self) -> bool:
        if self.force_mock_mode:
            return True
        if self.llm_provider.lower() == "openai" and not self.openai_api_key:
            return True
        return False

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def converted_path(self) -> Path:
        return Path(self.converted_dir)


@lru_cache
def get_settings() -> Settings:
    return Settings()
