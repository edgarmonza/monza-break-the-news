"""
Scraper para France24 en Español - Noticias sobre Colombia
Fuente: france24.com/es/tag/colombia/
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


class France24Scraper(BaseScraper):
    """Scraper para France24 en Español"""

    def __init__(self):
        super().__init__(
            source_name="france24",
            base_url="https://www.france24.com",
            language='es',
            is_international=True
        )
        self.sections = [
            "/es/tag/colombia/",
            "/es/am%C3%A9rica-latina/",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"France24: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # France24 uses article tags with o-teaser class
        for article_tag in soup.find_all('article', limit=30):
            article = self._extract_from_article(article_tag)
            if article:
                articles.append(article)

        # Also div-based cards
        for card in soup.find_all('div', class_=re.compile(r'(teaser|article|card)', re.I), limit=30):
            link = card.find('a', href=re.compile(r'/es/'))
            if link:
                article = self._extract_from_card(card, link)
                if article:
                    articles.append(article)

        return articles

    def _extract_from_article(self, tag) -> Optional[ScrapedArticle]:
        try:
            link = tag.find('a', href=re.compile(r'/es/'))
            if not link:
                return None

            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = tag.find(['h2', 'h3', 'h4'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            img = tag.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            preview_tag = tag.find('p')
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
            logger.debug(f"France24 article error: {e}")
            return None

    def _extract_from_card(self, card, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h2', 'h3', 'h4'])
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
            logger.debug(f"France24 card error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''}".lower()
        if '/colombia/' in article.url.lower():
            return True
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
