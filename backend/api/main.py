"""
FastAPI Application - Colombia News API
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from uuid import UUID
import logging

from api.models import (
    ThreadResponse,
    ThreadDetailResponse,
    FeedResponse,
    ChatRequest,
    ChatResponse,
    HealthResponse
)
from db import get_db, Database, ThreadRepository, ArticleRepository
from services import LLMThreadService, EmbeddingService
from services.macro_service import MacroDataService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Colombia News API",
    description="API for Break The Web clone - Colombian news aggregator with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:8000",
        "https://yourfrontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection
def get_thread_repo(db: Database = Depends(get_db)) -> ThreadRepository:
    return ThreadRepository(db)


def get_article_repo(db: Database = Depends(get_db)) -> ArticleRepository:
    return ArticleRepository(db)


# ==================== ENDPOINTS ====================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Colombia News API is running",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: Database = Depends(get_db)):
    """Detailed health check with database status"""
    db_healthy = await db.health_check()

    return {
        "status": "ok" if db_healthy else "degraded",
        "message": "API is operational",
        "database": "connected" if db_healthy else "disconnected"
    }


@app.get("/api/feed", response_model=FeedResponse)
async def get_feed(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    min_score: float = Query(default=0.0, ge=0.0, le=1.0),
    thread_repo: ThreadRepository = Depends(get_thread_repo)
):
    """
    Get news feed with threads ordered by trending score

    Args:
        limit: Maximum number of threads to return (1-100)
        offset: Offset for pagination
        min_score: Minimum trending score (0.0-1.0)

    Returns:
        List of threads with metadata
    """
    try:
        threads = await thread_repo.get_feed(
            limit=limit,
            offset=offset,
            min_score=min_score
        )

        return {
            "threads": [
                ThreadResponse(
                    id=str(thread.id),
                    title_id=thread.title_id,
                    display_title=thread.display_title,
                    summary=thread.summary,
                    trending_score=thread.trending_score,
                    article_count=len(thread.article_ids),
                    suggested_questions=thread.suggested_questions,
                    image_url=thread.image_url,
                    created_at=thread.created_at
                )
                for thread in threads
            ],
            "total": len(threads),
            "limit": limit,
            "offset": offset
        }

    except Exception as e:
        logger.error(f"Error getting feed: {e}")
        raise HTTPException(status_code=500, detail="Error fetching feed")


@app.get("/api/thread/{thread_id}", response_model=ThreadDetailResponse)
async def get_thread_detail(
    thread_id: UUID,
    thread_repo: ThreadRepository = Depends(get_thread_repo)
):
    """
    Get detailed information about a specific thread

    Args:
        thread_id: UUID of the thread

    Returns:
        Thread with all articles and metadata
    """
    try:
        thread = await thread_repo.get_by_id(thread_id, include_articles=True)

        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")

        return ThreadDetailResponse(
            id=str(thread.id),
            title_id=thread.title_id,
            display_title=thread.display_title,
            summary=thread.summary,
            trending_score=thread.trending_score,
            article_count=len(thread.article_ids),
            suggested_questions=thread.suggested_questions,
            image_url=thread.image_url,
            articles=[
                {
                    "id": str(article.id),
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "author": article.author,
                    "published_at": article.published_at,
                    "image_url": article.image_url
                }
                for article in (thread.articles or [])
            ],
            created_at=thread.created_at,
            updated_at=thread.updated_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching thread")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    thread_repo: ThreadRepository = Depends(get_thread_repo),
    article_repo: ArticleRepository = Depends(get_article_repo)
):
    """
    Chat with AI about a thread or search globally

    Args:
        request: Chat request with question and optional thread_id

    Returns:
        AI-generated answer based on relevant articles (RAG)
    """
    try:
        llm_service = LLMThreadService()
        embedding_service = EmbeddingService()

        # Obtener artículos relevantes
        if request.thread_id:
            # Chat sobre un thread específico
            thread = await thread_repo.get_by_id(
                UUID(request.thread_id),
                include_articles=True
            )

            if not thread:
                raise HTTPException(status_code=404, detail="Thread not found")

            context_articles = thread.articles or []

        else:
            # Búsqueda global por similitud semántica
            query_embedding = await embedding_service.embed_query(request.question)

            if not query_embedding:
                raise HTTPException(
                    status_code=500,
                    detail="Error generating query embedding"
                )

            context_articles = await article_repo.vector_search(
                query_embedding=query_embedding,
                limit=10,
                threshold=0.6
            )

        if not context_articles:
            return ChatResponse(
                answer="No encontré información relevante sobre esa pregunta en los artículos disponibles.",
                sources=[]
            )

        # Generar respuesta con LLM
        answer = await llm_service.generate_answer_for_question(
            question=request.question,
            articles=context_articles
        )

        if not answer:
            raise HTTPException(
                status_code=500,
                detail="Error generating answer"
            )

        # Extraer fuentes
        sources = [
            {
                "title": article.title,
                "source": article.source,
                "url": article.url
            }
            for article in context_articles[:5]  # Max 5 sources
        ]

        return ChatResponse(
            answer=answer,
            sources=sources
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat request")


@app.get("/api/search")
async def search_articles(
    query: str = Query(..., min_length=3),
    limit: int = Query(default=10, ge=1, le=50),
    article_repo: ArticleRepository = Depends(get_article_repo)
):
    """
    Semantic search for articles

    Args:
        query: Search query
        limit: Maximum number of results

    Returns:
        Relevant articles ranked by similarity
    """
    try:
        embedding_service = EmbeddingService()

        # Generate query embedding
        query_embedding = await embedding_service.embed_query(query)

        if not query_embedding:
            raise HTTPException(
                status_code=500,
                detail="Error generating query embedding"
            )

        # Vector search
        articles = await article_repo.vector_search(
            query_embedding=query_embedding,
            limit=limit,
            threshold=0.5
        )

        return {
            "query": query,
            "results": [
                {
                    "id": str(article.id),
                    "title": article.title,
                    "url": article.url,
                    "source": article.source,
                    "published_at": article.published_at
                }
                for article in articles
            ],
            "count": len(articles)
        }

    except Exception as e:
        logger.error(f"Error in search: {e}")
        raise HTTPException(status_code=500, detail="Error performing search")


# Macro data singleton
_macro_service = MacroDataService()


@app.get("/api/macro")
async def get_macro_data():
    """Get macroeconomic indicators for Colombia"""
    try:
        data = await _macro_service.get_all_indicators()
        return data
    except Exception as e:
        logger.error(f"Error fetching macro data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching macro data")


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
