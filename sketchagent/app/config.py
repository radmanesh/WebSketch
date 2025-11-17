"""Configuration management"""

from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_parse_none_str="",
        extra="ignore",  # Ignore extra fields from env vars
    )
    """Application settings"""

    # API
    api_key: str = Field(default="")
    api_title: str = "WebSketch Agent API"
    api_version: str = "0.1.0"

    # OpenAI
    openai_api_key: str = Field(default="")
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.3

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Logging
    log_level: str = "INFO"
    log_json: bool = False
    debug_mode: bool = Field(default=False, description="Enable debug mode with additional logging and endpoints")

    # CORS - stored as comma-separated string in env
    cors_origins_str: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        """Parse comma-separated CORS origins string to list"""
        if not self.cors_origins_str:
            return ["http://localhost:3000"]
        origins = [origin.strip() for origin in self.cors_origins_str.split(",") if origin.strip()]
        return origins if origins else ["http://localhost:3000"]

    @field_validator("api_key", "openai_api_key", "cors_origins_str", mode="before")
    @classmethod
    def parse_str_fields(cls, v):
        """Handle None values for string fields"""
        if v is None:
            return ""
        return v

    @field_validator("log_json", mode="before")
    @classmethod
    def parse_log_json(cls, v):
        """Parse log_json from string to bool"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "on")
        if v is None:
            return False
        return False


settings = Settings()

