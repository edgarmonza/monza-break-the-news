"""
Scraper para BBC Mundo - Noticias sobre Colombia
Fuente: bbc.com/mundo/topics/c3lyr3y8z0yt (tag Colombia)
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
    'farc', 'eln', 'peso colombiano', 'congreso colombiano'
]


class BBCMundoScraper(BaseScraper):
    """Scraper para BBC Mundo - cobertura internacional de Colombia"""

    def __init__(self):
        super().__init__(
            source_name="bbc_mundo",
            base_url="https://www.bbc.com",
            language='es',
            is_international=True
        )
        self.colombia_urls = [
            "/mundo",  # Homepage - filter for Colombia
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for path in self.colombia_urls:
            url = f"{self.base_url}{path}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        # Filter for Colombia relevance
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"BBC Mundo: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # BBC uses <a> with article URLs
        for link in soup.find_all('a', href=re.compile(r'/mundo/articles/'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        # Also look for promo cards
        for card in soup.find_all(['div', 'li'], class_=re.compile(r'(promo|card|story)', re.I), limit=30):
            link = card.find('a', href=re.compile(r'/mundo/'))
            if link:
                article = self._extract_article_from_card(card, link)
                if article:
                    articles.append(article)

        return articles

    def _extract_article(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/av/', '/media/', '/live/']):
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
            logger.debug(f"BBC extract error: {e}")
            return None

    def _extract_article_from_card(self, card, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h3', 'h2', 'span'], class_=re.compile(r'(title|headline)', re.I))
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

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
            logger.debug(f"BBC card extract error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        """Check if article is related to Colombia"""
        text = f"{article.title} {article.preview or ''}".lower()
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
