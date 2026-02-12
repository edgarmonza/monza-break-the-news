"""
Script de prueba para scrapers de medios colombianos
"""
import asyncio
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers import ElTiempoScraper, ElEspectadorScraper, SemanaScraper
from scrapers.base import BaseScraper
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_scraper(scraper: BaseScraper, name: str):
    """Prueba un scraper específico"""
    print(f"\n{'='*60}")
    print(f"PROBANDO: {name}")
    print(f"{'='*60}\n")

    try:
        # 1. Scrape frontpage
        logger.info(f"Scraping frontpage de {name}...")
        articles = await scraper.scrape_frontpage()

        print(f"✅ Artículos encontrados: {len(articles)}")

        if articles:
            print(f"\n📰 Primeros 5 artículos:\n")
            for i, article in enumerate(articles[:5], 1):
                print(f"{i}. {article.title}")
                print(f"   URL: {article.url}")
                print(f"   Source: {article.source}")
                if article.image_url:
                    print(f"   Imagen: {article.image_url[:60]}...")
                print()

            # 2. Probar scraping de contenido completo del primer artículo
            print(f"🔍 Extrayendo contenido completo del primer artículo...")
            first_article_url = articles[0].url
            full_article = await scraper.scrape_article_content(first_article_url)

            if full_article:
                print(f"✅ Contenido extraído exitosamente")
                print(f"   Título: {full_article.title}")
                print(f"   Autor: {full_article.author or 'N/A'}")
                print(f"   Fecha: {full_article.published_at or 'N/A'}")
                print(f"   Contenido (primeros 200 chars): {full_article.content[:200]}...")
            else:
                print(f"❌ No se pudo extraer contenido completo")

        else:
            print(f"⚠️  No se encontraron artículos")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        logger.exception(f"Error testing {name}")


async def main():
    """Ejecuta pruebas de todos los scrapers"""
    print("\n" + "="*60)
    print("PRUEBA DE SCRAPERS - COLOMBIA NEWS")
    print("="*60)

    scrapers = [
        (ElTiempoScraper(), "El Tiempo"),
        (ElEspectadorScraper(), "El Espectador"),
        (SemanaScraper(), "Semana")
    ]

    for scraper, name in scrapers:
        await test_scraper(scraper, name)

    print(f"\n{'='*60}")
    print("PRUEBAS COMPLETADAS")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
