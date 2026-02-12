"""
Servicio de embeddings usando OpenAI
"""
from typing import List, Optional
import logging
from openai import AsyncOpenAI
from config.settings import settings
from models.article import Article, ArticleBase
import asyncio

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Servicio para generar embeddings de artículos"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """
        Genera embedding de un texto
        Trunca a 8000 chars para evitar límites de tokens
        """
        try:
            # Truncar texto si es muy largo
            text = text[:8000] if len(text) > 8000 else text

            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float"
            )

            return response.data[0].embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    async def embed_article(self, article: ArticleBase) -> Optional[Article]:
        """
        Genera embedding para un artículo completo
        Combina título + contenido para mejor contexto semántico
        """
        try:
            # Crear texto combinado para embedding
            # El título tiene más peso (se incluye 2 veces)
            embedding_text = f"{article.title}. {article.title}. {article.content[:2000]}"

            embedding = await self.embed_text(embedding_text)

            if not embedding:
                logger.warning(f"No se pudo generar embedding para: {article.url}")
                return None

            # Convertir ArticleBase a Article con embedding
            return Article(
                **article.model_dump(),
                embedding=embedding
            )

        except Exception as e:
            logger.error(f"Error embedding article {article.url}: {str(e)}")
            return None

    async def embed_articles_batch(
        self,
        articles: List[ArticleBase],
        batch_size: int = 10
    ) -> List[Article]:
        """
        Procesa múltiples artículos en batches para eficiencia
        Retorna solo los artículos que se pudieron embedizar
        """
        embedded_articles = []

        # Procesar en batches para no sobrecargar la API
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]

            logger.info(f"Processing embedding batch {i//batch_size + 1}/{(len(articles)-1)//batch_size + 1}")

            # Procesar batch en paralelo
            tasks = [self.embed_article(article) for article in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Filtrar resultados exitosos
            for result in results:
                if isinstance(result, Article):
                    embedded_articles.append(result)
                elif isinstance(result, Exception):
                    logger.error(f"Error in batch processing: {str(result)}")

            # Rate limiting: pequeña pausa entre batches
            if i + batch_size < len(articles):
                await asyncio.sleep(0.5)

        logger.info(f"Successfully embedded {len(embedded_articles)}/{len(articles)} articles")
        return embedded_articles

    async def embed_query(self, query: str) -> Optional[List[float]]:
        """
        Genera embedding para una query de búsqueda
        Útil para búsquedas semánticas y RAG
        """
        return await self.embed_text(query)

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calcula similitud coseno entre dos vectores
        Retorna valor entre -1 y 1 (1 = idénticos)
        """
        import numpy as np

        v1 = np.array(vec1)
        v2 = np.array(vec2)

        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)

        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0

        return float(dot_product / (norm_v1 * norm_v2))
