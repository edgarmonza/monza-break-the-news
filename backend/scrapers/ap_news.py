"""
Scraper para AP News - Noticias sobre Colombia
Fuente: apnews.com
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)

COLOMBIA_KEYWORDS = [
    'colombia', 'bogota', 'medellin', 'cali', 'barranquilla', 'cartagena',
    'petro', 'colombian', 'farc', 'eln', 'colombian peso', 'ecopetrol',
    'cocaine', 'bogotá', 'medellín',
]


class APNewsScraper(BaseScraper):
    """Scraper para Associated Press"""

    def __init__(self):
        super().__init__(
            source_name="ap_news",
            base_url="https://apnews.com",
            language='en',
            is_international=True
        )
        self.sections = [
            "/hub/latin-america",
            "/hub/world-news",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"AP News: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # AP uses <a> links to /article/ paths
        for link in soup.find_all('a', href=re.compile(r'/article/'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        # Card-based extraction
        for card in soup.find_all(['div', 'article'], class_=re.compile(r'(PagePromo|FeedCard|card)', re.I), limit=30):
            link = card.find('a', href=re.compile(r'/article/'))
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

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"AP extract error: {e}")
            return None

    def _extract_from_card(self, card, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h2', 'h3', 'span'], class_=re.compile(r'(headline|title)', re.I))
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            preview_tag = card.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            img = card.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"AP card error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''} {article.url}".lower()
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
