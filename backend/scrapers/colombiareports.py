"""
Scraper para Colombia Reports - Medio en inglés 100% sobre Colombia
Fuente: colombiareports.com
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)


class ColombiaReportsScraper(BaseScraper):
    """Scraper para Colombia Reports - English-language Colombia news"""

    def __init__(self):
        super().__init__(
            source_name="colombiareports",
            base_url="https://colombiareports.com",
            language='en',
            is_international=True
        )

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        """Everything on this site is about Colombia - no filtering needed"""
        html = await self.fetch_html(self.base_url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # Article tags
        for article_tag in soup.find_all('article', limit=30):
            article = self._extract_from_article(article_tag)
            if article:
                articles.append(article)

        # WordPress-style links
        for link in soup.find_all('a', href=re.compile(r'colombiareports\.com/[a-z]'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        unique = {a.url: a for a in articles}

        if len(unique) == 0:
            logger.warning("Colombia Reports: 0 artículos encontrados")

        logger.info(f"Colombia Reports: {len(unique)} artículos únicos encontrados")
        return list(unique.values())

    def _extract_from_article(self, article_tag) -> Optional[ScrapedArticle]:
        try:
            link = article_tag.find('a', href=True)
            if not link:
                return None

            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/category/', '/tag/', '/author/', '/page/', '#']):
                return None

            title_tag = article_tag.find(['h2', 'h3', 'h1'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            preview_tag = article_tag.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            img = article_tag.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Colombia Reports article error: {e}")
            return None

    def _extract_article(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/category/', '/tag/', '/author/', '/page/', '#', 'javascript:']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Colombia Reports extract error: {e}")
            return None
