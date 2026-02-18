from langchain_core.language_models import BaseChatModel
from pydantic import SecretStr

from app.core.config import Settings


def create_chat_model(settings: Settings) -> BaseChatModel | None:
    provider = settings.llm_provider.lower().strip()

    if provider == "openai" and settings.openai_api_key:
        try:
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=settings.openai_model,
                api_key=SecretStr(settings.openai_api_key),
            )
        except Exception:
            return None

    if provider == "ollama":
        try:
            from langchain_ollama import ChatOllama

            return ChatOllama(
                model=settings.ollama_chat_model,
                base_url=settings.ollama_base_url,
            )
        except Exception:
            return None

    return None
