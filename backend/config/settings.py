"""
Configuración de la aplicación usando Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configuración global de la aplicación"""

    # API Keys
    google_api_key: str  # Gemini — embeddings (free tier)
    anthropic_api_key: str  # Claude — thread generation & chat
    openai_api_key: Optional[str] = None  # No longer required
    unsplash_access_key: Optional[str] = None
    apify_api_token: Optional[str] = None

    # Supabase
    supabase_url: str
    supabase_key: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App Config
    environment: str = "development"
    log_level: str = "INFO"
    scrape_interval_minutes: int = 15

    # Scheduler Config
    scheduler_enabled: bool = True
    scheduler_interval_hours: int = 2
    scheduler_countries: str = "CO,LATAM"  # Comma-separated ISO codes

    # Scraping Config
    max_articles_per_source: int = 50
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    use_apify: bool = True  # Use Apify Google News instead of custom scrapers
    apify_max_items_per_query: int = 50

    # Embedding Config (Google Gemini)
    embedding_model: str = "gemini-embedding-001"
    embedding_dimensions: int = 1536  # Match existing DB column; Gemini supports up to 3072

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
