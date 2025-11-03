"""Settings for Desktop RPA Agent."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Desktop RPA Agent settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Agent Info
    agent_id: str = Field(default="desktop-rpa-001", description="Unique agent ID")
    agent_name: str = Field(default="Desktop RPA Agent", description="Agent name")
    agent_version: str = Field(default="0.1.0", description="Agent version")

    # API Settings
    host: str = Field(default="127.0.0.1", description="API host")
    port: int = Field(default=8001, description="API port")
    log_level: str = Field(default="INFO", description="Logging level")

    # Scheduler Settings (for registration)
    scheduler_url: str = Field(
        default="http://localhost:8000",
        description="Scheduler API URL",
    )
    register_on_startup: bool = Field(
        default=False,
        description="Register with scheduler on startup",
    )
    heartbeat_interval: int = Field(
        default=30,
        description="Heartbeat interval in seconds",
    )

    # Execution Settings
    default_timeout: float = Field(default=30.0, description="Default timeout in seconds")
    screenshot_dir: str = Field(default="./data/screenshots", description="Screenshot directory")
    max_retries: int = Field(default=3, description="Max retries for failed actions")

    # PyAutoGUI Settings
    pyautogui_pause: float = Field(default=0.5, description="Pause between PyAutoGUI actions")
    pyautogui_failsafe: bool = Field(default=True, description="Enable PyAutoGUI failsafe")


# Global settings instance
settings = Settings()

