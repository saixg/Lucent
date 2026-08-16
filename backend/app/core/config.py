"""
Single responsibility: Load, validate, and expose application configuration and environment variables.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "dev-secret-key"
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: str

    # LLM Providers
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"
    OPENAI_API_KEY: str = ""
    WHISPER_MODEL: str = "whisper-1"

    # Search & Forensics
    TAVILY_API_KEY: str = ""
    SIGHTENGINE_API_USER: str = ""
    SIGHTENGINE_API_SECRET: str = ""

    # Call Caps (rules.md §4)
    MAX_SEARCH_QUERIES_PER_VERIFICATION: int = 5
    MAX_LLM_CALLS_PER_VERIFICATION: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        origins = [self.FRONTEND_URL.rstrip("/")]
        if self.APP_ENV == "development":
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:3001",
            ])
        return list(set(origins))


settings = Settings()
