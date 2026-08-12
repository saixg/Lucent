from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV: str = "development"
    SECRET_KEY: str
    FRONTEND_URL: str = "http://localhost:3000"

    # Supabase / DB
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    DATABASE_URL: str

    # AI
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash"
    OPENAI_API_KEY: str
    WHISPER_MODEL: str = "whisper-1"
    ANTHROPIC_API_KEY: str = ""

    # Search
    SERPER_API_KEY: str = ""
    TAVILY_API_KEY: str = ""

    # Media Forensics
    HIVE_API_KEY: str = ""
    SIGHTENGINE_API_USER: str = ""
    SIGHTENGINE_API_SECRET: str = ""

    # YouTube Bot
    YOUTUBE_API_KEY: str = ""
    YOUTUBE_CLIENT_ID: str = ""
    YOUTUBE_CLIENT_SECRET: str = ""
    YOUTUBE_REFRESH_TOKEN: str = ""

    # Jobs
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_BUCKET_MEDIA: str = "verilens-media"
    STORAGE_BUCKET_ARTIFACTS: str = "verilens-artifacts"

    # Monitoring
    SENTRY_DSN: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
