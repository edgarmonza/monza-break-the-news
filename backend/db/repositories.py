"""
Repositorios para acceso a datos (Repository Pattern)
"""
from typing import List, Optional, Dict
from uuid import UUID
import logging
from datetime import datetime
from supabase import Client
from models.article import Article, Thread, ArticleBase
from db.database import Database

logger = logging.getLogger(__name__)


class ArticleRepository:
    """Repository para operaciones con artículos"""

    def __init__(self, db: Database):
        self.db = db
        self.client: Client = db.client

    async def create(self, article: Article) -> Optional[Article]:
        """Crea un nuevo artículo en la BD"""
        try:
            data = {
                'id': str(article.id),
                'url': article.url,
                'title': article.title,
                'content': article.content,
                'source': article.source,
                'author': article.author,
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'image_url': article.image_url,
                'embedding': article.embedding,
                'scraped_at': article.scraped_at.isoformat()
            }

            result = self.client.table('articles').insert(data).execute()

            if result.data:
                logger.info(f"Article created: {article.id}")
                return article
            return None

        except Exception as e:
            logger.error(f"Error creating article: {e}")
            return None

    async def get_by_id(self, article_id: UUID) -> Optional[Article]:
        """Obtiene un artículo por ID"""
        try:
            result = self.client.table('articles')\
                .select('*')\
                .eq('id', str(article_id))\
                .single()\
                .execute()

            if result.data:
                return self._map_to_article(result.data)
            return None

        except Exception as e:
            logger.error(f"Error getting article {article_id}: {e}")
            return None

    async def get_by_url(self, url: str) -> Optional[Article]:
        """Obtiene un artículo por URL"""
        try:
            result = self.client.table('articles')\
                .select('*')\
                .eq('url', url)\
                .single()\
                .execute()

            if result.data:
                return self._map_to_article(result.data)
            return None

        except Exception as e:
            logger.debug(f"Article not found by URL: {url}")
            return None

    async def vector_search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Article]:
        """
        Búsqueda por similitud vectorial

        Args:
            query_embedding: Vector de la query
            limit: Máximo de resultados
            threshold: Umbral de similitud (0-1)

        Returns:
            Lista de artículos similares
        """
        try:
            # Supabase usa la función de similitud coseno
            # 1 - (embedding <=> query_embedding) AS similarity
            result = self.client.rpc(
                'match_articles',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()

            if result.data:
                return [self._map_to_article(row) for row in result.data]
            return []

        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return []

    async def get_recent(
        self,
        limit: int = 50,
        source: Optional[str] = None
    ) -> List[Article]:
        """Obtiene artículos recientes"""
        try:
            query = self.client.table('articles')\
                .select('*')\
                .order('scraped_at', desc=True)\
                .limit(limit)

            if source:
                query = query.eq('source', source)

            result = query.execute()

            if result.data:
                return [self._map_to_article(row) for row in result.data]
            return []

        except Exception as e:
            logger.error(f"Error getting recent articles: {e}")
            return []

    def _map_to_article(self, data: Dict) -> Article:
        """Mapea dict de BD a Article model"""
        return Article(
            id=UUID(data['id']),
            url=data['url'],
            title=data['title'],
            content=data['content'],
            source=data['source'],
            author=data.get('author'),
            published_at=datetime.fromisoformat(data['published_at']) if data.get('published_at') else None,
            image_url=data.get('image_url'),
            embedding=data.get('embedding'),
            scraped_at=datetime.fromisoformat(data['scraped_at'])
        )


class ThreadRepository:
    """Repository para operaciones con threads"""

    def __init__(self, db: Database):
        self.db = db
        self.client: Client = db.client

    async def create(self, thread: Thread) -> Optional[Thread]:
        """Crea un nuevo thread con artículos y preguntas"""
        try:
            # 1. Crear thread
            thread_data = {
                'id': str(thread.id),
                'title_id': thread.title_id,
                'display_title': thread.display_title,
                'summary': thread.summary,
                'trending_score': thread.trending_score,
                'article_count': len(thread.article_ids)
            }

            result = self.client.table('threads').insert(thread_data).execute()

            if not result.data:
                logger.error("Failed to create thread")
                return None

            # 2. Asociar artículos
            for position, article_id in enumerate(thread.article_ids):
                self.client.table('thread_articles').insert({
                    'thread_id': str(thread.id),
                    'article_id': str(article_id),
                    'position': position
                }).execute()

            # 3. Agregar preguntas sugeridas
            for position, question in enumerate(thread.suggested_questions):
                self.client.table('thread_questions').insert({
                    'thread_id': str(thread.id),
                    'question': question,
                    'position': position
                }).execute()

            logger.info(f"Thread created: {thread.title_id}")
            return thread

        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            return None

    async def get_by_id(
        self,
        thread_id: UUID,
        include_articles: bool = True
    ) -> Optional[Thread]:
        """Obtiene un thread por ID con sus artículos"""
        try:
            # 1. Obtener thread
            thread_result = self.client.table('threads')\
                .select('*')\
                .eq('id', str(thread_id))\
                .single()\
                .execute()

            if not thread_result.data:
                return None

            # 2. Obtener preguntas
            questions_result = self.client.table('thread_questions')\
                .select('question')\
                .eq('thread_id', str(thread_id))\
                .order('position')\
                .execute()

            questions = [q['question'] for q in questions_result.data] if questions_result.data else []

            # 3. Obtener article_ids
            articles_result = self.client.table('thread_articles')\
                .select('article_id')\
                .eq('thread_id', str(thread_id))\
                .order('position')\
                .execute()

            article_ids = [UUID(a['article_id']) for a in articles_result.data] if articles_result.data else []

            # 4. Cargar artículos completos si se solicita
            articles = []
            if include_articles and article_ids:
                article_repo = ArticleRepository(self.db)
                for aid in article_ids:
                    article = await article_repo.get_by_id(aid)
                    if article:
                        articles.append(article)

            return Thread(
                id=UUID(thread_result.data['id']),
                title_id=thread_result.data['title_id'],
                display_title=thread_result.data['display_title'],
                summary=thread_result.data['summary'],
                trending_score=thread_result.data['trending_score'],
                article_ids=article_ids,
                articles=articles if include_articles else None,
                suggested_questions=questions,
                image_url=thread_result.data.get('image_url'),
                created_at=datetime.fromisoformat(thread_result.data['created_at']),
                updated_at=datetime.fromisoformat(thread_result.data['updated_at'])
            )

        except Exception as e:
            logger.error(f"Error getting thread {thread_id}: {e}")
            return None

    async def get_feed(
        self,
        limit: int = 20,
        offset: int = 0,
        min_score: float = 0.0
    ) -> List[Thread]:
        """
        Obtiene feed de threads ordenados por trending_score

        Args:
            limit: Máximo de threads
            offset: Offset para paginación
            min_score: Score mínimo para incluir

        Returns:
            Lista de threads ordenados
        """
        try:
            result = self.client.table('threads')\
                .select('*')\
                .gte('trending_score', min_score)\
                .order('trending_score', desc=True)\
                .order('created_at', desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()

            if not result.data:
                return []

            threads = []
            for thread_data in result.data:
                thread = await self.get_by_id(
                    UUID(thread_data['id']),
                    include_articles=False  # No cargar artículos en el feed
                )
                if thread:
                    threads.append(thread)

            return threads

        except Exception as e:
            logger.error(f"Error getting feed: {e}")
            return []

    async def update_trending_score(
        self,
        thread_id: UUID,
        new_score: float
    ) -> bool:
        """Actualiza el trending score de un thread"""
        try:
            result = self.client.table('threads')\
                .update({'trending_score': new_score})\
                .eq('id', str(thread_id))\
                .execute()

            return bool(result.data)

        except Exception as e:
            logger.error(f"Error updating score for {thread_id}: {e}")
            return False

    async def delete(self, thread_id: UUID) -> bool:
        """Elimina un thread (cascade a relaciones)"""
        try:
            result = self.client.table('threads')\
                .delete()\
                .eq('id', str(thread_id))\
                .execute()

            logger.info(f"Thread deleted: {thread_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting thread {thread_id}: {e}")
            return False
