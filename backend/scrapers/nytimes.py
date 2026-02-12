"""
Scraper para The New York Times - Noticias sobre Colombia
Fuente: nytimes.com
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)

COLOMBIA_KEYWORDS = [
    'colombia', 'bogota', 'medellin', 'cali', 'colombian', 'petro',
    'farc', 'eln', 'cocaine', 'bogotá', 'medellín', 'cartagena',
    'barranquilla', 'ecopetrol', 'gustavo petro',
]


class NYTimesScraper(BaseScraper):
    """Scraper para The New York Times"""

    def __init__(self):
        super().__init__(
            source_name="nytimes",
            base_url="https://www.nytimes.com",
            language='en',
            is_international=True
        )
        self.sections = [
            "/section/world/americas",
            "/topic/destination/colombia",
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
            logger.warning("NYT: 0 artículos - sitio puede bloquear scrapers o requerir JS")
        else:
            logger.info(f"NYT: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # NYT uses <a> links to article paths
        for link in soup.find_all('a', href=re.compile(r'/\d{4}/\d{2}/\d{2}/'), limit=50):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        # Also story wrapper cards
        for card in soup.find_all(['li', 'div', 'article'], class_=re.compile(r'(story|css-)', re.I), limit=30):
            link = card.find('a', href=re.compile(r'/\d{4}/\d{2}/\d{2}/'))
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

            if any(x in url for x in ['/video/', '/interactive/', '/slideshow/', '/live/']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"NYT extract error: {e}")
            return None

    def _extract_from_card(self, card, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h2', 'h3', 'h1'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            preview_tag = card.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            img = card.find('img')
            image_url = img.get('src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"NYT card error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''} {article.url}".lower()
        if '/colombia' in article.url.lower():
            return True
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
