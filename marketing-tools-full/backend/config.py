"""
Configuration settings for Marketing Tools Backend
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Model
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "claude-sonnet-4-20250514")
    
    # CORS
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
