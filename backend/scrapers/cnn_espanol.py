"""
Scraper para CNN en Español - Noticias sobre Colombia
Fuente: cnnespanol.cnn.com
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
    'farc', 'eln', 'peso colombiano'
]


class CNNEspanolScraper(BaseScraper):
    """Scraper para CNN en Español"""

    def __init__(self):
        super().__init__(
            source_name="cnn_espanol",
            base_url="https://cnnespanol.cnn.com",
            language='es',
            is_international=True
        )
        self.sections = [
            "/tema/colombia/",
            "/category/america-latina/",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"CNN Español: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # CNN uses card__headline pattern
        for card in soup.find_all(['div', 'article'], class_=re.compile(r'(card|post|article)', re.I), limit=30):
            article = self._extract_from_card(card)
            if article:
                articles.append(article)

        # Also try direct article links
        for link in soup.find_all('a', href=re.compile(r'cnnespanol\.cnn\.com/\d{4}/\d{2}/'), limit=40):
            article = self._extract_from_link(link)
            if article:
                articles.append(article)

        return articles

    def _extract_from_card(self, card) -> Optional[ScrapedArticle]:
        try:
            link = card.find('a', href=re.compile(r'https?://'))
            if not link:
                return None

            url = link.get('href', '')
            if 'cnnespanol' not in url and not url.startswith('/'):
                return None
            if url.startswith('/'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'(headline|title)', re.I))
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            img = card.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            return ScrapedArticle(
                url=url,
                title=title,
                preview=None,
                image_url=image_url,
                source=self.source_name,
                published_at=None
            )
        except Exception as e:
            logger.debug(f"CNN card error: {e}")
            return None

    def _extract_from_link(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url or any(x in url for x in ['/video/', '/gallery/', '#']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
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
            logger.debug(f"CNN link error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''}".lower()
        # Articles from the Colombia section are always relevant
        if '/colombia/' in article.url.lower():
            return True
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
