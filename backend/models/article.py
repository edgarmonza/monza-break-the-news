"""
Modelos Pydantic para artículos y threads
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID, uuid4


class ArticleBase(BaseModel):
    """Artículo base scraped de medios colombianos"""
    url: str
    title: str
    content: str
    source: str  # 'eltiempo', 'elespectador', 'semana', etc.
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None


class Article(ArticleBase):
    """Artículo con ID y embedding"""
    id: UUID = Field(default_factory=uuid4)
    embedding: Optional[List[float]] = None
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "url": "https://www.eltiempo.com/politica/...",
                "title": "Nuevo anuncio del gobierno sobre reforma tributaria",
                "content": "El gobierno colombiano anunció hoy...",
                "source": "eltiempo",
                "author": "Juan Pérez",
                "published_at": "2024-02-01T10:30:00Z"
            }
        }


class ThreadMetadata(BaseModel):
    """Metadata generada por LLM para un thread"""
    title_id: str  # '@ReformaTributaria'
    display_title: str
    summary: str
    suggested_questions: List[str] = Field(max_length=5)


class Thread(BaseModel):
    """Thread/Historia que agrupa múltiples artículos relacionados"""
    id: UUID = Field(default_factory=uuid4)
    title_id: str  # '@ReformaTributaria'
    display_title: str
    summary: str
    article_ids: List[UUID]
    articles: Optional[List[Article]] = None
    suggested_questions: List[str] = []
    trending_score: float = 0.0
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "223e4567-e89b-12d3-a456-426614174001",
                "title_id": "@ReformaTributaria",
                "display_title": "Debate sobre reforma tributaria en Colombia",
                "summary": "El gobierno presenta nueva propuesta...",
                "article_ids": ["123e4567-e89b-12d3-a456-426614174000"],
                "trending_score": 0.85
            }
        }


class ScrapedArticle(BaseModel):
    """Artículo recién scraped (sin procesar)"""
    url: str
    title: str
    preview: Optional[str] = None
    image_url: Optional[str] = None
    source: str
    published_at: Optional[datetime] = None
