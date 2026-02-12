"""
Scraper para Las2Orillas - Medio digital independiente colombiano
Fuente: las2orillas.co
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)


class Las2OrillasScraper(BaseScraper):
    """Scraper para Las2Orillas - perspectiva independiente"""

    def __init__(self):
        super().__init__(
            source_name="las2orillas",
            base_url="https://www.las2orillas.co",
            language='es',
            is_international=False
        )

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        homepage_articles = await self._scrape_section(self.base_url)
        all_articles.extend(homepage_articles)

        # Note: Las2Orillas section URLs redirect to random articles,
        # so we only scrape the homepage which has all recent content

        unique = {a.url: a for a in all_articles}
        logger.info(f"Las2Orillas: {len(unique)} artículos únicos encontrados")
        return list(unique.values())

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        for article_tag in soup.find_all('article', limit=30):
            article = self._extract_from_tag(article_tag)
            if article:
                articles.append(article)

        for div in soup.find_all('div', class_=re.compile(r'(post|entry|article|card)', re.I), limit=30):
            article = self._extract_from_tag(div)
            if article:
                articles.append(article)

        # WordPress-style links
        for link in soup.find_all('a', href=re.compile(r'las2orillas\.co/[a-z]'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        return articles

    def _extract_from_tag(self, tag) -> Optional[ScrapedArticle]:
        try:
            link = tag.find('a', href=True)
            if not link:
                return None

            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/category/', '/tag/', '/author/', '#', 'javascript:']):
                return None

            title_tag = tag.find(['h2', 'h3', 'h1', 'h4'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 10:
                return None

            preview_tag = tag.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            img = tag.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Las2Orillas extract error: {e}")
            return None

    def _extract_article(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/category/', '/tag/', '/author/', '/page/', '#']):
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 10:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"Las2Orillas article error: {e}")
            return None
