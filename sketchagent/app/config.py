"""Configuration management"""

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    """Application settings"""

    # API
    api_key: str = os.getenv("API_KEY", "")
    api_title: str = "WebSketch Agent API"
    api_version: str = "0.1.0"

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_json: bool = os.getenv("LOG_JSON", "false").lower() == "true"

    # CORS
    cors_origins: list[str] = Field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    )


settings = Settings()

