"""
Scraper para El Espectador (elespectador.com)
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)


class ElEspectadorScraper(BaseScraper):
    """Scraper específico para El Espectador"""

    def __init__(self):
        super().__init__(
            source_name="elespectador",
            base_url="https://www.elespectador.com"
        )
        self.sections = [
            "/noticias/politica",
            "/noticias/judicial",
            "/noticias/economia",
            "/noticias/nacional",
            "/noticias/el-mundo"
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

        if len(unique_articles) == 0:
            logger.warning("El Espectador: 0 artículos - sitio requiere JavaScript (Playwright)")

        logger.info(f"El Espectador: {len(unique_articles)} artículos únicos encontrados")
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

        # Patrón 2: Divs con clases de artículos
        for div in soup.find_all('div', class_=re.compile(r'(Card|article|noticia)', re.I), limit=30):
            article = self._extract_article(div)
            if article:
                articles.append(article)

        # Patrón 3: Enlaces directos a artículos
        for link in soup.find_all('a', href=re.compile(r'/noticias/[a-z\-]+/[a-z0-9\-]+')):
            article = self._extract_from_link(link)
            if article:
                articles.append(article)

        return articles

    def _extract_article(self, tag) -> Optional[ScrapedArticle]:
        """Extrae información de artículo desde un tag"""
        try:
            # Buscar enlace
            link = tag.find('a', href=re.compile(r'/noticias/'))
            if not link or not link.get('href'):
                return None

            url = link['href']
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Título
            title_tag = tag.find(['h1', 'h2', 'h3', 'h4']) or link
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
                    img.get('data-lazy-src')
                )
                # El Espectador usa a veces picture > source
                if not image_url:
                    picture = tag.find('picture')
                    if picture:
                        source = picture.find('source')
                        if source:
                            image_url = source.get('srcset', '').split(',')[0].split(' ')[0]

            # Preview
            preview_tag = tag.find(['p', 'div'], class_=re.compile(r'(description|excerpt|summary)', re.I))
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
            if any(x in url for x in ['/autor/', '/tema/', 'javascript:', '#']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 10:
                return None

            return ScrapedArticle(
                url=url,
                title=title,
                preview=None,
                image_url=None,
                source=self.source_name,
                published_at=None
            )

        except Exception as e:
            logger.debug(f"Error extracting from link: {str(e)}")
            return None
