"""
Scraper para DW (Deutsche Welle) en Español - Noticias sobre Colombia
Fuente: dw.com/es/
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


class DWEspanolScraper(BaseScraper):
    """Scraper para DW en Español"""

    def __init__(self):
        super().__init__(
            source_name="dw_espanol",
            base_url="https://www.dw.com",
            language='es',
            is_international=True
        )
        self.sections = [
            "/es/américa-latina/s-42464457",
            "/es",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"DW Español: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # DW uses a variety of card patterns
        for card in soup.find_all(['div', 'article'], class_=re.compile(r'(teaser|content-item|story|card)', re.I), limit=30):
            article = self._extract_from_card(card)
            if article:
                articles.append(article)

        # Direct links to articles
        for link in soup.find_all('a', href=re.compile(r'/es/.*a-\d+'), limit=40):
            article = self._extract_from_link(link)
            if article:
                articles.append(article)

        return articles

    def _extract_from_card(self, card) -> Optional[ScrapedArticle]:
        try:
            link = card.find('a', href=re.compile(r'/es/'))
            if not link:
                return None

            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Skip non-article URLs
            if any(x in url for x in ['/av-', '/media', '/video']):
                return None

            title_tag = card.find(['h2', 'h3', 'h4', 'span'], class_=re.compile(r'(title|headline)', re.I))
            title = title_tag.get_text(strip=True) if title_tag else None

            if not title:
                title = link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            img = card.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            preview_tag = card.find('p')
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
            logger.debug(f"DW card error: {e}")
            return None

    def _extract_from_link(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/av-', '/media', '/video']):
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
            logger.debug(f"DW link error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''}".lower()
        if '/colombia/' in article.url.lower():
            return True
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
