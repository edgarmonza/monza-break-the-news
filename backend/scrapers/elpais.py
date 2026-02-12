"""
Scraper para El País (España) - Cobertura América / Colombia
Fuente: elpais.com/america/colombia/
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)

COLOMBIA_KEYWORDS = [
    'colombia', 'bogotá', 'bogota', 'medellín', 'medellin', 'cali',
    'barranquilla', 'cartagena', 'petro', 'colombiano', 'colombiana',
    'farc', 'eln', 'peso colombiano', 'ecopetrol',
]


class ElPaisScraper(BaseScraper):
    """Scraper para El País España - desk de América"""

    def __init__(self):
        super().__init__(
            source_name="elpais",
            base_url="https://elpais.com",
            language='es',
            is_international=True
        )
        self.sections = [
            "/america-colombia/",
            "/noticias/colombia/",
            "/internacional/",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"El País: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # El País uses <article> tags with headlines
        for article_tag in soup.find_all('article', limit=30):
            article = self._extract_from_article(article_tag)
            if article:
                articles.append(article)

        # Also direct links to articles
        for link in soup.find_all('a', href=re.compile(r'elpais\.com/.+/\d{4}-\d{2}-\d{2}/'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        return articles

    def _extract_from_article(self, article_tag) -> Optional[ScrapedArticle]:
        try:
            link = article_tag.find('a', href=True)
            if not link:
                return None

            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = article_tag.find(['h2', 'h3', 'h1'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            preview_tag = article_tag.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            img = article_tag.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"El País article error: {e}")
            return None

    def _extract_article(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"El País extract error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''} {article.url}".lower()
        if '/america-colombia/' in article.url.lower() or '/noticias/colombia/' in article.url.lower():
            return True
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
