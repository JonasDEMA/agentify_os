"""Server configuration."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./cpa_server.db"
    
    # Storage
    UPLOAD_DIR: str = "./uploads"
    SCREENSHOT_DIR: str = "./uploads/screenshots"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    API_KEY_LENGTH: int = 64
    
    # Agent
    AGENT_TIMEOUT_SECONDS: int = 300  # 5 minutes


settings = Settings()

