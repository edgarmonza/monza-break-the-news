"""
Scraper base abstracto para medios de noticias
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
import logging
from newspaper import Article as NewspaperArticle
from models.article import ScrapedArticle, ArticleBase
import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Clase base para todos los scrapers de medios"""

    def __init__(self, source_name: str, base_url: str, language: str = 'es', is_international: bool = False):
        self.source_name = source_name
        self.base_url = base_url
        self.language = language
        self.is_international = is_international
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

    @abstractmethod
    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        """
        Scrape la página principal y retorna lista de artículos
        Debe ser implementado por cada scraper específico
        """
        pass

    async def scrape_article_content(self, url: str) -> Optional[ArticleBase]:
        """
        Extrae el contenido completo de un artículo usando newspaper3k
        Este método puede ser usado por todos los scrapers
        """
        try:
            article = NewspaperArticle(url, language=self.language)
            article.download()
            article.parse()

            # Validar que tenemos contenido mínimo
            if not article.text or len(article.text) < 100:
                logger.warning(f"Contenido muy corto o vacío: {url}")
                return None

            return ArticleBase(
                url=url,
                title=article.title or "Sin título",
                content=article.text,
                source=self.source_name,
                author=article.authors[0] if article.authors else None,
                published_at=article.publish_date,
                image_url=article.top_image if article.top_image else None
            )

        except Exception as e:
            logger.error(f"Error scraping article {url}: {str(e)}")
            return None

    async def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML de una URL con manejo de errores"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"User-Agent": self.user_agent}
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML con BeautifulSoup"""
        return BeautifulSoup(html, 'lxml')
