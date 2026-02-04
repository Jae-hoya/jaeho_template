from __future__ import annotations

from dataclasses import dataclass
import os

from dotenv import load_dotenv

DEFAULT_BASE_URL = "http://openapi.seoul.go.kr:8088"
DEFAULT_SERVICE_NAME = "culturalEventInfo"
DEFAULT_RESPONSE_TYPE = "json"
DEFAULT_TIMEOUT_SECONDS = 10.0


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    service_name: str
    response_type: str
    timeout_seconds: float


_settings: Settings | None = None


def load_settings() -> Settings:
    load_dotenv(override=False)
    api_key = os.getenv("SEOUL_API_KEY", "").strip()
    base_url = os.getenv("SEOUL_API_BASE_URL", DEFAULT_BASE_URL).strip()
    response_type = (
        os.getenv("SEOUL_API_TYPE")
        or os.getenv("SEOUL_RESPONSE_TYPE")
        or DEFAULT_RESPONSE_TYPE
    )
    service_name = (
        os.getenv("SEOUL_API_SERVICE")
        or os.getenv("SEOUL_SERVICE_NAME")
        or DEFAULT_SERVICE_NAME
    )
    timeout_raw = os.getenv("SEOUL_API_TIMEOUT_SECONDS")
    if timeout_raw:
        try:
            timeout_seconds = float(timeout_raw)
        except ValueError:
            timeout_seconds = DEFAULT_TIMEOUT_SECONDS
    else:
        timeout_seconds = DEFAULT_TIMEOUT_SECONDS
    return Settings(
        api_key=api_key,
        base_url=base_url,
        service_name=service_name,
        response_type=response_type,
        timeout_seconds=timeout_seconds,
    )


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings
