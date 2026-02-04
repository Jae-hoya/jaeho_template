"""Configuration for hybrid search application"""

import os
import re
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from parent directory
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, encoding='utf-8')


class Config:
    """Application configuration"""

    # Database connection (ParadeDB on port 5433)
    DATABASE_URL = os.getenv("DATABASE_URL") or "postgresql://postgres:postgres@localhost:5433/postgres"

    # Alternative connection parameters
    NEON_HOST = os.getenv("NEON_HOST")
    NEON_DATABASE = os.getenv("NEON_DATABASE", "neondb")
    NEON_USER = os.getenv("NEON_USER")
    NEON_PASSWORD = os.getenv("NEON_PASSWORD")

    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    EMBEDDING_MODEL = "text-embedding-3-small"
    EMBEDDING_DIMENSIONS = 1536

    # Table configuration
    TABLE_NAME = "loan_products"

    # Search configuration
    RRF_K = 60  # Reciprocal Rank Fusion constant
    BM25_MODE = os.getenv("BM25_MODE", "paradedb").lower()
    BM25_TOKENIZER = os.getenv("BM25_TOKENIZER", "simple").lower()
    KIWI_POS_FILTER = [
        tag.strip()
        for tag in os.getenv(
            "KIWI_POS_FILTER",
            "NNG,NNP,NNB,NR,NP,VV,VA,XR,SL,SN",
        ).split(",")
        if tag.strip()
    ]
    _KIWI = None

    @classmethod
    def get_connection_string(cls) -> str:
        """Get PostgreSQL connection string"""
        if cls.DATABASE_URL:
            return cls.DATABASE_URL

        if all([cls.NEON_HOST, cls.NEON_DATABASE, cls.NEON_USER, cls.NEON_PASSWORD]):
            return (
                f"postgresql://{cls.NEON_USER}:{cls.NEON_PASSWORD}"
                f"@{cls.NEON_HOST}/{cls.NEON_DATABASE}?sslmode=require"
            )

        raise ValueError(
            "Database connection not configured. Please set DATABASE_URL or "
            "NEON_HOST, NEON_DATABASE, NEON_USER, NEON_PASSWORD in .env file"
        )

    @classmethod
    def _simple_tokenize(cls, text: str) -> str:
        cleaned = re.sub(r"[^\w\s가-힣]", " ", text)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    @classmethod
    def _get_kiwi(cls):
        if cls._KIWI is None:
            try:
                from kiwipiepy import Kiwi
            except Exception as exc:
                raise ImportError(
                    "BM25_TOKENIZER=kiwi requires kiwipiepy. "
                    "Install with: pip install kiwipiepy"
                ) from exc
            cls._KIWI = Kiwi()
        return cls._KIWI

    @classmethod
    def tokenize_for_bm25(cls, text: str) -> str:
        if not text:
            return ""
        if cls.BM25_TOKENIZER != "kiwi":
            return cls._simple_tokenize(text)

        kiwi = cls._get_kiwi()
        tokens: List[str] = []
        for token in kiwi.tokenize(text):
            if token.tag in cls.KIWI_POS_FILTER and token.form.strip():
                tokens.append(token.form)

        tokenized = " ".join(tokens).strip()
        return tokenized or cls._simple_tokenize(text)

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        try:
            cls.get_connection_string()
        except ValueError as e:
            raise ValueError(f"Database configuration error: {e}")


# Validate configuration on import
Config.validate()
