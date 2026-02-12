"""
Configuración de la aplicación usando Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # API Keys
    openai_api_key: str
    anthropic_api_key: str
    unsplash_access_key: Optional[str] = None

    # Supabase
    supabase_url: str
    supabase_key: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App Config
    environment: str = "development"
    log_level: str = "INFO"
    scrape_interval_minutes: int = 15

    # Scraping Config
    max_articles_per_source: int = 50
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    # Embedding Config
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    # Clustering Config
    clustering_eps: float = 0.3
    clustering_min_samples: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Singleton instance
settings = Settings()
