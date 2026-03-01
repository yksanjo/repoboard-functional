"""Configuration management for RepoBoard services."""

import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/repoboard")
    
    # Vector DB
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    
    # LLM Provider
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    # GitHub
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    
    # API
    api_port: int = int(os.getenv("API_PORT", "8000"))
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    
    # Jobs
    ingestion_batch_size: int = int(os.getenv("INGESTION_BATCH_SIZE", "50"))
    curation_interval_hours: int = int(os.getenv("CURATION_INTERVAL_HOURS", "24"))
    trending_check_interval_hours: int = int(os.getenv("TRENDING_CHECK_INTERVAL_HOURS", "6"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

