"""
Pydantic models para API requests y responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


# ==================== RESPONSES ====================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    database: Optional[str] = None


class ThreadResponse(BaseModel):
    """Thread summary for feed"""
    id: str
    title_id: str  # '@ReformaTributaria'
    display_title: str
    summary: str
    trending_score: float
    article_count: int
    suggested_questions: List[str]
    image_url: Optional[str] = None
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title_id": "@ReformaTributaria",
                "display_title": "Gobierno presenta nueva reforma tributaria",
                "summary": "El gobierno colombiano anunció...",
                "trending_score": 0.847,
                "article_count": 7,
                "suggested_questions": [
                    "¿Por qué es importante esto?",
                    "¿Cuál es el contexto histórico?"
                ],
                "created_at": "2024-02-01T10:30:00Z"
            }
        }


class ArticleResponse(BaseModel):
    """Article summary"""
    id: str
    title: str
    url: str
    source: str
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None


class ThreadDetailResponse(ThreadResponse):
    """Detailed thread with articles"""
    articles: List[ArticleResponse]
    updated_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title_id": "@ReformaTributaria",
                "display_title": "Gobierno presenta nueva reforma tributaria",
                "summary": "El gobierno colombiano anunció...",
                "trending_score": 0.847,
                "article_count": 7,
                "suggested_questions": ["..."],
                "articles": [
                    {
                        "id": "...",
                        "title": "Gobierno anuncia...",
                        "url": "https://...",
                        "source": "eltiempo"
                    }
                ],
                "created_at": "2024-02-01T10:30:00Z",
                "updated_at": "2024-02-01T10:30:00Z"
            }
        }


class FeedResponse(BaseModel):
    """Feed with multiple threads"""
    threads: List[ThreadResponse]
    total: int
    limit: int
    offset: int


class ChatSourceResponse(BaseModel):
    """Source article for chat response"""
    title: str
    source: str
    url: str


class ChatResponse(BaseModel):
    """Chat AI response"""
    answer: str
    sources: List[ChatSourceResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "La reforma tributaria propuesta busca...",
                "sources": [
                    {
                        "title": "Gobierno anuncia...",
                        "source": "eltiempo",
                        "url": "https://..."
                    }
                ]
            }
        }


# ==================== REQUESTS ====================

class ChatRequest(BaseModel):
    """Chat request"""
    question: str = Field(..., min_length=3, max_length=500)
    thread_id: Optional[str] = None  # If provided, chat about specific thread

    class Config:
        json_schema_extra = {
            "example": {
                "question": "¿Por qué es importante esta reforma?",
                "thread_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
