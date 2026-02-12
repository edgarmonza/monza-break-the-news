"""
Scraper para El Universal - Cartagena / Bolívar
Fuente: eluniversal.com.co
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)


class ElUniversalScraper(BaseScraper):
    """Scraper para El Universal - principal de Cartagena"""

    def __init__(self):
        super().__init__(
            source_name="eluniversal",
            base_url="https://www.eluniversal.com.co",
            language='es',
            is_international=False
        )
        self.sections = [
            "/cartagena/",
            "/colombia/",
            "/politica/",
            "/sucesos/",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        homepage = await self._scrape_section(self.base_url)
        all_articles.extend(homepage)

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        logger.info(f"El Universal: {len(unique)} artículos únicos encontrados")
        return list(unique.values())

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        for tag in soup.find_all('article', limit=30):
            article = self._extract(tag)
            if article:
                articles.append(article)

        for tag in soup.find_all('div', class_=re.compile(r'(article|card|nota|story)', re.I), limit=30):
            article = self._extract(tag)
            if article:
                articles.append(article)

        for link in soup.find_all('a', href=re.compile(r'eluniversal\.com\.co/.+'), limit=40):
            title = link.get_text(strip=True)
            if title and len(title) >= 10:
                url_l = link.get('href', '')
                if not url_l.startswith('http'):
                    url_l = f"{self.base_url}{url_l}"
                if not any(x in url_l for x in ['/autor/', '/tema/', '#']):
                    articles.append(ScrapedArticle(
                        url=url_l, title=title, preview=None,
                        image_url=None, source=self.source_name, published_at=None
                    ))

        return articles

    def _extract(self, tag) -> Optional[ScrapedArticle]:
        try:
            link = tag.find('a', href=True)
            if not link:
                return None
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"
            if any(x in url for x in ['/autor/', '/tema/', '#', 'javascript:']):
                return None

            title_tag = tag.find(['h2', 'h3', 'h1', 'h4'])
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)
            if not title or len(title) < 10:
                return None

            preview_tag = tag.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None
            img = tag.find('img')
            image_url = img.get('data-src') or img.get('src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"El Universal error: {e}")
            return None
