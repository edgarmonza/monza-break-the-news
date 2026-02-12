"""
Scraper para Infobae Colombia
Fuente: infobae.com/colombia/
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)


class InfobaeScraper(BaseScraper):
    """Scraper para Infobae - edición Colombia"""

    def __init__(self):
        super().__init__(
            source_name="infobae",
            base_url="https://www.infobae.com",
            language='es',
            is_international=True
        )
        self.sections = [
            "/colombia/",
            "/economia/",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        logger.info(f"Infobae: {len(unique)} artículos únicos encontrados")
        return list(unique.values())

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # Infobae uses <a> with article paths
        for link in soup.find_all('a', href=re.compile(r'/colombia/|/economia/|/america/'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        # Card-based patterns
        for card in soup.find_all(['article', 'div'], class_=re.compile(r'(story-card|feed-list|article)', re.I), limit=30):
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

            if any(x in url for x in ['/video/', '/galeria/', '/podcast/']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Infobae extract error: {e}")
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
            image_url = img.get('src') or img.get('data-src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Infobae card error: {e}")
            return None
