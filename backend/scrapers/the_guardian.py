"""
Scraper para The Guardian - Noticias sobre Colombia
Fuente: theguardian.com/world/colombia
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)

COLOMBIA_KEYWORDS = [
    'colombia', 'bogota', 'medellin', 'cali', 'barranquilla', 'cartagena',
    'petro', 'colombian', 'farc', 'eln', 'cocaine', 'bogotá', 'medellín',
]


class TheGuardianScraper(BaseScraper):
    """Scraper para The Guardian - fuerte cobertura LatAm"""

    def __init__(self):
        super().__init__(
            source_name="the_guardian",
            base_url="https://www.theguardian.com",
            language='en',
            is_international=True
        )
        self.sections = [
            "/world/colombia",
            "/world/americas",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        # /world/colombia section is already filtered, but americas needs filtering
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"The Guardian: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # Guardian uses links with /YYYY/mon/DD/ date patterns
        for link in soup.find_all('a', href=re.compile(r'/\d{4}/[a-z]{3}/\d{2}/'), limit=50):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        # Also card-based extraction
        for card in soup.find_all(['div', 'li', 'section'], attrs={'data-link-name': True}, limit=30):
            link = card.find('a', href=True)
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

            if any(x in url for x in ['/video/', '/gallery/', '/audio/']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Guardian extract error: {e}")
            return None

    def _extract_from_card(self, card, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h3', 'h2', 'span'], class_=re.compile(r'(headline|title|card)', re.I))
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            preview_tag = card.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            img = card.find('img')
            image_url = img.get('src') or img.get('srcset', '').split(' ')[0] if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Guardian card error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''} {article.url}".lower()
        # Articles from /world/colombia are automatically relevant
        if '/world/colombia' in article.url.lower():
            return True
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
