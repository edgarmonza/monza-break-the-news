"""
Scraper para Reuters - Noticias sobre Colombia
Fuente: reuters.com
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
    'bancolombia', 'avianca', 'cocaine', 'bogotá', 'medellín',
]


class ReutersScraper(BaseScraper):
    """Scraper para Reuters - wire service global"""

    def __init__(self):
        super().__init__(
            source_name="reuters",
            base_url="https://www.reuters.com",
            language='en',
            is_international=True
        )
        self.sections = [
            "/world/americas/",
            "/markets/",
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
            logger.warning("Reuters: 0 artículos - sitio bloquea scrapers (requiere Playwright)")
        else:
            logger.info(f"Reuters: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # Reuters uses <a> with data-testid or article links
        for link in soup.find_all('a', href=re.compile(r'^/world/|^/markets/|^/business/'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        # Also look for story cards
        for card in soup.find_all(['div', 'li', 'article'], attrs={'data-testid': re.compile(r'(MediaStory|TextStory|Story)', re.I)}, limit=30):
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

            if any(x in url for x in ['/video/', '/pictures/', '/graphics/']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Reuters extract error: {e}")
            return None

    def _extract_from_card(self, card, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            title_tag = card.find(['h3', 'h2', 'span'], attrs={'data-testid': re.compile(r'Heading', re.I)})
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
            logger.debug(f"Reuters card error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''} {article.url}".lower()
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
