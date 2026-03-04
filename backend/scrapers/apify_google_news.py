"""
Google News scraper via Apify — replaces 28 custom scrapers with one cloud-based solution.

Uses the epctex/google-news-scraper actor to fetch articles from Google News,
then newspaper3k for full content extraction (same as before).
"""
import logging
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlparse

from apify_client import ApifyClient
from newspaper import Article as NewspaperArticle
from dateutil import parser as dateparser

from models.article import ScrapedArticle, ArticleBase
from config.settings import settings

logger = logging.getLogger(__name__)

# ── Search queries per country for comprehensive LATAM coverage ──
COUNTRY_QUERIES = {
    "CO": {
        "code": "CO",
        "language": "es",
        "queries": [
            "Colombia noticias hoy",
            "Colombia política gobierno",
            "Colombia economía",
            "Colombia seguridad conflicto",
            "Bogotá noticias",
            "Medellín noticias",
            "Petro Colombia",
            "Colombia deportes",
            "Colombia internacional",
        ],
    },
    "MX": {
        "code": "MX",
        "language": "es",
        "queries": [
            "México noticias hoy",
            "México política gobierno",
            "México economía",
            "México seguridad",
            "Ciudad de México noticias",
            "AMLO Sheinbaum México",
            "México deportes",
        ],
    },
    "AR": {
        "code": "AR",
        "language": "es",
        "queries": [
            "Argentina noticias hoy",
            "Argentina política gobierno",
            "Argentina economía dólar",
            "Argentina seguridad",
            "Buenos Aires noticias",
            "Milei Argentina",
            "Argentina deportes",
        ],
    },
    "CL": {
        "code": "CL",
        "language": "es",
        "queries": [
            "Chile noticias hoy",
            "Chile política gobierno",
            "Chile economía",
            "Santiago Chile noticias",
        ],
    },
    "PE": {
        "code": "PE",
        "language": "es",
        "queries": [
            "Perú noticias hoy",
            "Perú política gobierno",
            "Perú economía",
            "Lima Perú noticias",
        ],
    },
    "EC": {
        "code": "EC",
        "language": "es",
        "queries": [
            "Ecuador noticias hoy",
            "Ecuador política gobierno",
            "Ecuador economía seguridad",
            "Quito Ecuador noticias",
        ],
    },
    "LATAM": {
        "code": "CO",  # Use CO as default Google region for LATAM queries
        "language": "es",
        "queries": [
            "América Latina noticias",
            "Latinoamérica economía",
        ],
    },
}

# Default: Colombia only (backward compatible)
SEARCH_QUERIES = COUNTRY_QUERIES["CO"]["queries"]

# ── Source name normalization (Google News publisher → internal name) ──
SOURCE_MAP = {
    # Colombianos nacionales
    "el tiempo": "eltiempo",
    "el espectador": "elespectador",
    "semana": "semana",
    "revista semana": "semana",
    "la silla vacía": "lasillavacia",
    "portafolio": "portafolio",
    "portafolio.co": "portafolio",
    "caracol radio": "caracol",
    "caracol": "caracol",
    "noticias caracol": "caracol",
    "pulzo": "pulzo",
    "las2orillas": "las2orillas",
    "las 2 orillas": "las2orillas",
    # Colombianos regionales
    "el heraldo": "elheraldo",
    "el colombiano": "elcolombiano",
    "el país": "elpaiscali",
    "elpais.com.co": "elpaiscali",
    "vanguardia": "vanguardia",
    "vanguardia.com": "vanguardia",
    "el universal": "eluniversal",
    "la opinión": "laopinion",
    # Internacionales español
    "bbc mundo": "bbc_mundo",
    "bbc news mundo": "bbc_mundo",
    "cnn en español": "cnn_espanol",
    "cnn español": "cnn_espanol",
    "france 24": "france24",
    "france24": "france24",
    "dw": "dw_espanol",
    "dw (español)": "dw_espanol",
    "deutsche welle": "dw_espanol",
    "infobae": "infobae",
    "infobae américa": "infobae",
    "el país": "elpais",
    "elpais.com": "elpais",
    # Internacionales inglés
    "reuters": "reuters",
    "associated press": "ap_news",
    "ap news": "ap_news",
    "the guardian": "the_guardian",
    "bloomberg": "bloomberg",
    "bloomberg línea": "bloomberg",
    "insight crime": "insightcrime",
    "insightcrime": "insightcrime",
    "colombia reports": "colombiareports",
    "the new york times": "nytimes",
    "new york times": "nytimes",
    "nytimes": "nytimes",
}


class ApifyGoogleNewsScraper:
    """
    Cloud-based news scraper using Apify's Google News actor.
    Replaces 28 custom scrapers with broader, more reliable coverage.
    """

    def __init__(self, api_token: Optional[str] = None):
        self.token = api_token or settings.apify_api_token
        self.client = ApifyClient(self.token)
        self.actor_id = "epctex/google-news-scraper"

    async def scrape_all(
        self,
        queries: Optional[List[str]] = None,
        max_items_per_query: int = 50,
        countries: Optional[List[str]] = None,
    ) -> List[ScrapedArticle]:
        """
        Run Google News scraper on Apify for multiple queries.
        Supports multi-country scraping.
        Returns deduplicated ScrapedArticle list.
        """
        all_articles: List[ScrapedArticle] = []
        seen_urls: set = set()

        # Multi-country mode
        if countries:
            for country_code in countries:
                country_config = COUNTRY_QUERIES.get(country_code)
                if not country_config:
                    logger.warning(f"Unknown country code: {country_code}, skipping")
                    continue

                logger.info(f"Apify: scraping {country_code} ({len(country_config['queries'])} queries)...")

                for query in country_config["queries"]:
                    try:
                        logger.info(f"  [{country_code}] '{query}'...")
                        articles = self._run_actor(
                            query, max_items_per_query,
                            language=country_config["language"],
                            country=country_config["code"],
                        )

                        new_count = 0
                        for article in articles:
                            if article.url not in seen_urls:
                                seen_urls.add(article.url)
                                article.country = country_code
                                all_articles.append(article)
                                new_count += 1

                        logger.info(f"  ✓ [{country_code}] '{query}': {len(articles)} resultados, {new_count} nuevos")
                    except Exception as e:
                        logger.error(f"  ✗ [{country_code}] Error en query '{query}': {e}")
                        continue
        else:
            # Single-country fallback (backward compatible)
            queries = queries or SEARCH_QUERIES
            logger.info(f"Apify: ejecutando {len(queries)} queries...")

            for query in queries:
                try:
                    logger.info(f"  Apify: '{query}'...")
                    articles = self._run_actor(query, max_items_per_query)

                    new_count = 0
                    for article in articles:
                        if article.url not in seen_urls:
                            seen_urls.add(article.url)
                            all_articles.append(article)
                            new_count += 1

                    logger.info(f"  ✓ '{query}': {len(articles)} resultados, {new_count} nuevos")
                except Exception as e:
                    logger.error(f"  ✗ Error en query '{query}': {e}")
                    continue

        logger.info(f"Total Apify: {len(all_articles)} artículos únicos")
        return all_articles

    def _run_actor(
        self, query: str, max_items: int,
        language: str = "es", country: str = "CO",
    ) -> List[ScrapedArticle]:
        """Run Apify actor for a single query."""
        run_input = {
            "searchTerms": [query],
            "language": language,
            "country": country,
            "maxItems": max_items,
        }

        run = self.client.actor(self.actor_id).call(run_input=run_input)
        items = self.client.dataset(run["defaultDatasetId"]).list_items().items

        articles = []
        for item in items:
            article = self._parse_item(item)
            if article:
                articles.append(article)

        return articles

    def _parse_item(self, item: dict) -> Optional[ScrapedArticle]:
        """Convert an Apify dataset item to ScrapedArticle."""
        # URL — try multiple field names, prefer decoded URLs
        url = (
            item.get("decodedUrl")
            or item.get("originalUrl")
            or item.get("link")
            or item.get("url")
            or item.get("articleUrl")
        )
        title = item.get("title") or item.get("headline")

        if not url or not title:
            return None

        # Skip unresolved Google News redirect URLs
        if "news.google.com" in url:
            return None

        # Normalize source
        raw_source = (
            item.get("source") or item.get("publisher") or ""
        )
        source = self._normalize_source(raw_source, url)

        # Parse published date
        published_at = self._parse_date(
            item.get("pubDate")
            or item.get("publishedAt")
            or item.get("date")
        )

        return ScrapedArticle(
            url=url,
            title=title.strip(),
            preview=item.get("snippet") or item.get("description") or "",
            image_url=item.get("image") or item.get("thumbnail") or None,
            source=source,
            published_at=published_at,
        )

    def _normalize_source(self, raw_source: str, url: str = "") -> str:
        """Normalize source name to match internal naming."""
        lower = raw_source.lower().strip()

        # Exact match
        if lower in SOURCE_MAP:
            return SOURCE_MAP[lower]

        # Partial match
        for key, value in SOURCE_MAP.items():
            if key in lower or lower in key:
                return value

        # Try matching by domain
        if url:
            domain = urlparse(url).netloc.replace("www.", "").lower()
            for key, value in SOURCE_MAP.items():
                clean_key = key.replace(" ", "").replace(".", "")
                clean_domain = domain.replace(".", "")
                if clean_key in clean_domain or clean_domain.startswith(clean_key):
                    return value

        # Unknown source — clean up the name
        return lower.replace(" ", "_").replace(".", "") or "other"

    def _parse_date(self, date_value) -> Optional[datetime]:
        """Parse date from various formats."""
        if not date_value:
            return None
        try:
            if isinstance(date_value, str):
                return dateparser.parse(date_value)
            if isinstance(date_value, (int, float)):
                return datetime.fromtimestamp(date_value / 1000)
        except Exception:
            pass
        return None

    async def extract_article_content(
        self, url: str, language: str = "es"
    ) -> Optional[ArticleBase]:
        """Extract full article content using newspaper3k."""
        try:
            article = NewspaperArticle(url, language=language)
            article.download()
            article.parse()

            if not article.text or len(article.text) < 100:
                return None

            domain = urlparse(url).netloc.replace("www.", "")
            source = self._normalize_source(domain, url)

            return ArticleBase(
                url=url,
                title=article.title or "Sin título",
                content=article.text,
                source=source,
                author=article.authors[0] if article.authors else None,
                published_at=article.publish_date,
                image_url=article.top_image if article.top_image else None,
            )

        except Exception as e:
            logger.error(f"Error extracting {url}: {e}")
            return None
