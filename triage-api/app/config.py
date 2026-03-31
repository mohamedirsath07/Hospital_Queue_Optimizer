"""Application configuration using pydantic-settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Groq API
    groq_api_key: str
    groq_model: str = "llama-3.1-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Timeouts
    llm_timeout: int = 30
    safety_confidence_threshold: float = 0.75


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
