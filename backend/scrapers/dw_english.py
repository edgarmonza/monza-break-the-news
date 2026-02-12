"""
Scraper para DW (Deutsche Welle) en Inglés - Noticias sobre Colombia
Fuente: dw.com/en/
"""
from typing import List, Optional
from scrapers.base import BaseScraper
from models.article import ScrapedArticle
import logging
import re

logger = logging.getLogger(__name__)

COLOMBIA_KEYWORDS = [
    'colombia', 'bogota', 'medellin', 'cali', 'colombian', 'petro',
    'farc', 'eln', 'cocaine', 'bogotá', 'medellín', 'cartagena',
    'barranquilla', 'ecopetrol', 'gustavo petro', 'darien',
]


class DWEnglishScraper(BaseScraper):
    """Scraper para Deutsche Welle en inglés"""

    def __init__(self):
        super().__init__(
            source_name="dw_english",
            base_url="https://www.dw.com",
            language='en',
            is_international=True
        )
        self.sections = [
            "/en/latin-america/s-58267484",
            "/en/top-stories/s-9097",
        ]

    async def scrape_frontpage(self) -> List[ScrapedArticle]:
        all_articles = []

        for section in self.sections:
            url = f"{self.base_url}{section}"
            articles = await self._scrape_section(url)
            all_articles.extend(articles)

        unique = {a.url: a for a in all_articles}
        filtered = [a for a in unique.values() if self._is_about_colombia(a)]
        logger.info(f"DW English: {len(filtered)} artículos sobre Colombia (de {len(unique)} total)")
        return filtered

    async def _scrape_section(self, url: str) -> List[ScrapedArticle]:
        html = await self.fetch_html(url)
        if not html:
            return []

        soup = self.parse_html(html)
        articles = []

        # DW uses class="...teaser..." for article cards
        for card in soup.find_all(['div', 'article'], class_=re.compile(r'teaser', re.I), limit=30):
            article = self._extract_from_card(card)
            if article:
                articles.append(article)

        # Fallback: grab any article link with a-NNNNN pattern
        for link in soup.find_all('a', href=re.compile(r'/en/.*a-\d+'), limit=40):
            article = self._extract_article(link)
            if article:
                articles.append(article)

        return articles

    def _extract_from_card(self, card) -> Optional[ScrapedArticle]:
        try:
            link = card.find('a', href=re.compile(r'/en/.*a-\d+'))
            if not link:
                return None

            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            # Skip video/audio-only content
            if any(x in url for x in ['/av-', '/media']):
                return None
            if '/video-' in url:
                return None

            # DW uses class="title ..." or h2/h3 for titles
            title_tag = card.find(['h2', 'h3', 'h4', 'span', 'a'],
                                  class_=re.compile(r'title', re.I))
            title = title_tag.get_text(strip=True) if title_tag else link.get_text(strip=True)

            if not title or len(title) < 15:
                return None

            # DW uses class="teaser-description ..." for preview text
            preview_tag = card.find(['p', 'div'],
                                    class_=re.compile(r'(description|teaser-description)', re.I))
            if not preview_tag:
                preview_tag = card.find('p')
            preview = preview_tag.get_text(strip=True) if preview_tag else None

            img = card.find('img')
            image_url = img.get('src') or img.get('data-src') if img else None

            return ScrapedArticle(
                url=url, title=title, preview=preview,
                image_url=image_url, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"DW English card error: {e}")
            return None

    def _extract_article(self, link) -> Optional[ScrapedArticle]:
        try:
            url = link.get('href', '')
            if not url.startswith('http'):
                url = f"{self.base_url}{url}"

            if any(x in url for x in ['/av-', '/media']):
                return None
            if '/video-' in url:
                return None

            title = link.get_text(strip=True)
            if not title or len(title) < 15:
                return None

            return ScrapedArticle(
                url=url, title=title, preview=None,
                image_url=None, source=self.source_name, published_at=None
            )
        except Exception as e:
            logger.debug(f"DW English link error: {e}")
            return None

    def _is_about_colombia(self, article: ScrapedArticle) -> bool:
        text = f"{article.title} {article.preview or ''} {article.url}".lower()
        if '/colombia/' in article.url.lower():
            return True
        return any(kw in text for kw in COLOMBIA_KEYWORDS)
