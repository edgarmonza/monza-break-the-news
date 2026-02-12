"""
Scraper para Semana (semana.com)
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)


class SemanaScraper(BaseScraper):
    """Scraper específico para Revista Semana"""

    def __init__(self):
        super().__init__(
            source_name="semana",
            base_url="https://www.semana.com"
        )
        self.sections = [
            "/nacion",
            "/economia",
            "/mundo",
            "/politica"
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        """Scrape artículos de la página principal y secciones"""
        all_articles = []

        # Homepage
        homepage_articles = await self._scrape_section(self.base_url)
        all_articles.extend(homepage_articles)

        # Secciones
        for section in self.sections:
            section_url = f"{self.base_url}{section}"
            section_articles = await self._scrape_section(section_url)
            all_articles.extend(section_articles)

        # Eliminar duplicados
        unique_articles = {article.url: article for article in all_articles}
        logger.info(f"Semana: {len(unique_articles)} artículos únicos encontrados")

        return list(unique_articles.values())

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        """Scrape una sección específica"""
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # Patrón 1: Tags article
        for article_tag in soup.find_all('article', limit=30):
            article = self._extract_article(article_tag)
            if article:
                articles.append(article)

        # Patrón 2: Divs con clases típicas de Semana
        for div in soup.find_all('div', class_=re.compile(r'(article|nota|story)', re.I), limit=30):
            article = self._extract_article(div)
            if article:
                articles.append(article)

        # Patrón 3: Enlaces a artículos (patrón URL de Semana)
        for link in soup.find_all('a', href=re.compile(r'/[a-z\-]+/articulo/')):
            article = self._extract_from_link(link)
            if article:
                articles.append(article)

        return articles

    def _extract_article(self, tag) -> Optional[ScrapedArticle]:
        """Extrae información de artículo desde un tag"""
        try:
            # Buscar enlace
            link = tag.find('a', href=True)
            if not link or not link.get('href'):
                return None

            url = link['href']

            # Validar que sea un artículo de Semana
            if 'articulo/' not in url and '/nacion/' not in url:
                return None

            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Título
            title_tag = tag.find(['h1', 'h2', 'h3', 'h4'])
            if not title_tag:
                # Buscar en el enlace mismo
                title_tag = link.find(['h1', 'h2', 'h3', 'h4']) or link

            title = title_tag.get_text(strip=True) if title_tag else None

            if not title or len(title) < 10:
                return None

            # Imagen
            img = tag.find('img')
            image_url = None
            if img:
                image_url = (
                    img.get('data-src') or
                    img.get('src') or
                    img.get('data-lazy') or
                    img.get('data-original')
                )

            # Preview/Descripción
            preview_tag = tag.find(['p', 'div', 'span'], class_=re.compile(r'(summ|desc|excerpt)', re.I))
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            return ScrapedArticle(
                url=url,
                title=title,
                preview=preview,
                image_url=image_url,
                source=self.source_name,
                published_at=None
            )

        except Exception as e:
            logger.debug(f"Error extracting article: {str(e)}")
            return None

    def _extract_from_link(self, link) -> Optional[ScrapedArticle]:
        """Extrae información básica desde un enlace"""
        try:
            url = link.get('href')
            if not url:
                return None

            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Filtrar URLs no deseadas
            if any(x in url for x in ['/autor/', '/tag/', '/video/', 'javascript:', '#']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 10:
                return None

            # Buscar imagen en el parent container
            parent = link.parent
            img = None
            if parent:
                img = parent.find('img')

            image_url = None
            if img:
                image_url = img.get('data-src') or img.get('src')

            return ScrapedArticle(
                url=url,
                title=title,
                preview=None,
                image_url=image_url,
                source=self.source_name,
                published_at=None
            )

        except Exception as e:
            logger.debug(f"Error extracting from link: {str(e)}")
            return None
