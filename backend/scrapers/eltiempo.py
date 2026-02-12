"""
Scraper para El Tiempo (eltiempo.com)
"""
from typing import List, Optional
from datetime import datetime
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)


class ElTiempoScraper(BaseScraper):
    """Scraper específico para El Tiempo"""

    def __init__(self):
        super().__init__(
            source_name="eltiempo",
            base_url="https://www.eltiempo.com"
        )
        self.sections = [
            "/politica",
            "/justicia",
            "/economia",
            "/colombia",
            "/mundo"
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        """
        Scrape artículos de la página principal y secciones principales
        """
        all_articles = []

        # Scrape homepage
        homepage_articles = await self._scrape_section(self.base_url)
        all_articles.extend(homepage_articles)

        # Scrape cada sección
        for section in self.sections:
            section_url = f"{self.base_url}{section}"
            section_articles = await self._scrape_section(section_url)
            all_articles.extend(section_articles)

        # Eliminar duplicados por URL
        unique_articles = {article.url: article for article in all_articles}
        logger.info(f"El Tiempo: {len(unique_articles)} artículos únicos encontrados")

        return list(unique_articles.values())

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        """Scrape una sección específica"""
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # Buscar artículos en diferentes patrones de HTML
        # El Tiempo usa varios patrones: <article>, divs con clases específicas

        # Patrón 1: tags <article>
        for article_tag in soup.find_all('article', limit=30):
            article = self._extract_article_from_tag(article_tag)
            if article:
                articles.append(article)

        # Patrón 2: divs con clase que contenga 'article' o 'story'
        for div in soup.find_all('div', class_=re.compile(r'(article|story|news-item)', re.I), limit=30):
            article = self._extract_article_from_tag(div)
            if article:
                articles.append(article)

        # Patrón 3: enlaces con estructura típica de El Tiempo
        for link in soup.find_all('a', href=re.compile(r'/[a-z\-]+/[a-z0-9\-]+-\d+'), limit=50):
            article = self._extract_article_from_link(link)
            if article:
                articles.append(article)

        return articles

    def _extract_article_from_tag(self, tag) -> Optional[ScrapedArticle]:
        """Extrae información de artículo desde un tag HTML"""
        try:
            # Buscar el enlace principal
            link = tag.find('a', href=re.compile(r'/[a-z\-]+/'))
            if not link or not link.get('href'):
                return None

            url = link['href']
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Buscar título
            title_tag = tag.find(['h2', 'h3', 'h4', 'h1']) or link
            title = title_tag.get_text(strip=True) if title_tag else None

            if not title or len(title) < 10:
                return None

            # Buscar imagen
            img = tag.find('img')
            image_url = None
            if img:
                image_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

            # Buscar preview/descripción
            preview_tag = tag.find(['p', 'span'], class_=re.compile(r'(desc|summary|preview)', re.I))
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            return ScrapedArticle(
                url=url,
                title=title,
                preview=preview,
                image_url=image_url,
                source=self.source_name,
                published_at=None  # Se parseará después con newspaper3k
            )

        except Exception as e:
            logger.debug(f"Error extracting article from tag: {str(e)}")
            return None

    def _extract_article_from_link(self, link) -> Optional[ScrapedArticle]:
        """Extrae información básica desde un enlace"""
        try:
            url = link.get('href')
            if not url:
                return None

            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Filtrar URLs que no son artículos
            if any(x in url for x in ['/autor/', '/etiqueta/', '/seccion/', 'javascript:', '#']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 10:
                return None

            # Buscar imagen cercana
            parent = link.parent
            img = parent.find('img') if parent else None
            image_url = None
            if img:
                image_url = img.get('src') or img.get('data-src')

            return ScrapedArticle(
                url=url,
                title=title,
                preview=None,
                image_url=image_url,
                source=self.source_name,
                published_at=None
            )

        except Exception as e:
            logger.debug(f"Error extracting article from link: {str(e)}")
            return None
