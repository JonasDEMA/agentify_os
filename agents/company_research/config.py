"""
Company Research Agent - Configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Agent configuration settings"""
    
    # Agent Identity
    agent_id: str = "agent.mossler.company_research"
    agent_name: str = "Company Research Agent"
    agent_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", "8001"))
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 4000
    
    # Web Scraping Configuration
    user_agent: str = "CompanyResearchAgent/1.0 (Mossler GmbH; +https://mossler.de)"
    request_timeout: int = 30
    max_retries: int = 3
    rate_limit_requests: int = 10
    rate_limit_period: int = 60  # seconds
    
    # Scraping Ethics
    respect_robots_txt: bool = True
    min_request_delay: float = 1.0  # seconds between requests
    
    # Excel Configuration
    max_file_size_mb: int = 50
    supported_formats: list[str] = ["xlsx", "xls", "csv"]
    
    # Data Extraction Configuration
    default_fields: dict = {
        "managing_directors": True,
        "revenue": True,
        "employees": True,
        "history": False,
        "news": False
    }
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CoreSense IAM
    coresense_url: Optional[str] = "https://iam.meet-harmony.ai"
    coresense_client_id: Optional[str] = None
    coresense_client_secret: Optional[str] = None
    
    # Marketplace
    marketplace_url: str = "https://marketplace.meet-harmony.ai"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()

