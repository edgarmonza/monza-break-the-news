"""
Scraper para Bloomberg - Noticias financieras sobre Colombia
Fuente: bloomberg.com
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)

COLOMBIA_KEYWORDS = [
    'colombia', 'bogota', 'medellin', 'colombian', 'petro',
    'ecopetrol', 'bancolombia', 'avianca', 'colombian peso',
    'cop currency', 'bogotá', 'medellín', 'grupo aval',
    'andean', 'latam airlines',
]


class BloombergScraper(BaseScraper):
    """Scraper para Bloomberg - ángulo financiero"""

    def __init__(self):
        super().__init__(
            source_name="bloomberg",
            base_url="https://www.bloomberg.com",
            language='en',
            is_international=True
        )
        self.sections = [
            "/latin-america",
            "/markets",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        if len(unique) == 0:
            logger.warning("Bloomberg: 0 artículos - sitio bloquea scrapers (requiere Playwright)")
        else:
            logger.info(f"Bloomberg: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            # Bloomberg often blocks scrapers
            logger.debug(f"Bloomberg: no HTML from {url} (paywall/JS required)")
            return []

        soup = self.parse_html(html)
        articles = []

        # Bloomberg article links
        for link in soup.find_all('a', href=re.compile(r'/news/articles/|/opinion/|/features/'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        # Story cards
        for card in soup.find_all(['article', 'div', 'section'], class_=re.compile(r'(story|article|card)', re.I), limit=30):
            link = card.find('a', href=re.compile(r'/news/|/opinion/'))
            if link:
                article = self._extract_from_card(card, link)
                if article:
                    articles.append(article)

        return articles

    def _extract_article(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/video/', '/audio/', '/graphics/', '/podcasts/']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Bloomberg extract error: {e}")
            return None

    def _extract_from_card(self, card, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h3', 'h2', 'h1'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            preview_tag = card.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Bloomberg card error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''} {article.url}".lower()
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
