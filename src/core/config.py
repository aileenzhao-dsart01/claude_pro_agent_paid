"""Configuration management for marketing agent system."""

from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import validator, Field


class Settings(BaseSettings):
    """Application settings."""

    # Application
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "change-this-in-production"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/marketing_agents"
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM Providers
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4000

    # Google Ads API
    GOOGLE_ADS_CLIENT_ID: Optional[str] = None
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = None
    GOOGLE_ADS_REFRESH_TOKEN: Optional[str] = None
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = None
    GOOGLE_ADS_CUSTOMER_ID: Optional[str] = None

    # Agent Settings
    AGENT_MAX_CONCURRENT_TASKS: int = 5
    AGENT_TASK_TIMEOUT_SECONDS: int = 300
    AGENT_RETRY_ATTEMPTS: int = 3
    SUPERVISOR_HEARTBEAT_INTERVAL: int = 30  # seconds

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Security
    API_KEY_HEADER: str = "X-API-Key"
    API_KEYS: List[str] = []

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = True

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL."""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        if not v.startswith(("postgresql://", "postgres://")):
            raise ValueError("DATABASE_URL must start with postgresql:// or postgres://")
        return v

    @validator("REDIS_URL")
    def validate_redis_url(cls, v):
        """Validate Redis URL."""
        if not v:
            raise ValueError("REDIS_URL must be set")
        if not v.startswith("redis://"):
            raise ValueError("REDIS_URL must start with redis://")
        return v

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("API_KEYS", pre=True)
    def parse_api_keys(cls, v):
        """Parse API keys from comma-separated string or list."""
        if isinstance(v, str):
            return [key.strip() for key in v.split(",") if key.strip()]
        return v


settings = Settings()