"""Application settings using pydantic-settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="cpa-scheduler", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_key: str = Field(default="dev-api-key", alias="API_KEY")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_max_connections: int = Field(default=10, alias="REDIS_MAX_CONNECTIONS")

    # Database
    database_url: str = Field(default="sqlite:///./data/scheduler.db", alias="DATABASE_URL")
    database_echo: bool = Field(default=False, alias="DATABASE_ECHO")

    # OpenAI
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo-preview", alias="OPENAI_MODEL")
    openai_max_retries: int = Field(default=3, alias="OPENAI_MAX_RETRIES")
    openai_timeout: int = Field(default=30, alias="OPENAI_TIMEOUT")

    # LLM Provider
    llm_provider: str = Field(default="openai", alias="LLM_PROVIDER")
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, alias="LLM_MAX_TOKENS")

    # Job Queue
    job_queue_max_retries: int = Field(default=3, alias="JOB_QUEUE_MAX_RETRIES")
    job_queue_retry_delay: int = Field(default=5, alias="JOB_QUEUE_RETRY_DELAY")

    # Task Execution
    task_default_timeout: int = Field(default=30, alias="TASK_DEFAULT_TIMEOUT")
    task_max_parallel: int = Field(default=5, alias="TASK_MAX_PARALLEL")

    # Security
    jwt_secret_key: str = Field(default="dev-secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expiration_minutes: int = Field(default=60, alias="JWT_EXPIRATION_MINUTES")

    # CORS
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8080", alias="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(
        default="GET,POST,PUT,DELETE,OPTIONS", alias="CORS_ALLOW_METHODS"
    )
    cors_allow_headers: str = Field(default="*", alias="CORS_ALLOW_HEADERS")

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_methods_list(self) -> list[str]:
        """Get CORS methods as list."""
        return [method.strip() for method in self.cors_allow_methods.split(",")]


# Global settings instance
settings = Settings()

