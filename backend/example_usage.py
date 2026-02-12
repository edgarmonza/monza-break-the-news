"""
Ejemplo de uso del sistema de scraping y embeddings
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from scrapers import ElTiempoScraper, ElEspectadorScraper
from services import EmbeddingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_complete_pipeline():
    """
    Ejemplo completo del pipeline de scraping + embedding
    """
    print("\n" + "="*60)
    print("EJEMPLO: Pipeline Completo de Scraping + Embeddings")
    print("="*60 + "\n")

    # 1. SCRAPING
    print("📡 PASO 1: Scraping de noticias\n")

    scraper = ElTiempoScraper()
    scraped_articles = await scraper.scrape_frontpage()

    print(f"✅ {len(scraped_articles)} artículos scraped")
    print(f"   Primer artículo: {scraped_articles[0].title}\n")

    # 2. EXTRAER CONTENIDO COMPLETO
    print("📄 PASO 2: Extracción de contenido completo\n")

    # Tomar los primeros 3 artículos como ejemplo
    full_articles = []
    for article in scraped_articles[:3]:
        full_article = await scraper.scrape_article_content(article.url)
        if full_article:
            full_articles.append(full_article)
            print(f"✅ {full_article.title}")
            print(f"   Contenido: {len(full_article.content)} caracteres")
        else:
            print(f"❌ No se pudo extraer: {article.url}")

    print(f"\n✅ {len(full_articles)} artículos completos extraídos\n")

    # 3. GENERAR EMBEDDINGS (requiere OPENAI_API_KEY en .env)
    print("🧠 PASO 3: Generación de embeddings\n")

    try:
        embedding_service = EmbeddingService()

        # Embed un solo artículo
        first_article = full_articles[0]
        embedded_article = await embedding_service.embed_article(first_article)

        if embedded_article:
            print(f"✅ Embedding generado")
            print(f"   Dimensiones: {len(embedded_article.embedding)}")
            print(f"   Primeros 5 valores: {embedded_article.embedding[:5]}\n")

            # Embed múltiples artículos en batch
            print("🔄 Procesando batch de artículos...\n")
            embedded_articles = await embedding_service.embed_articles_batch(
                full_articles,
                batch_size=2
            )

            print(f"✅ {len(embedded_articles)} artículos con embeddings\n")

            # 4. CALCULAR SIMILITUD
            print("📊 PASO 4: Cálculo de similitud semántica\n")

            if len(embedded_articles) >= 2:
                similarity = embedding_service.cosine_similarity(
                    embedded_articles[0].embedding,
                    embedded_articles[1].embedding
                )

                print(f"Artículo 1: {embedded_articles[0].title[:50]}...")
                print(f"Artículo 2: {embedded_articles[1].title[:50]}...")
                print(f"Similitud: {similarity:.3f}\n")

                # Interpretar similitud
                if similarity > 0.8:
                    print("💡 Artículos MUY similares (mismo tema)")
                elif similarity > 0.6:
                    print("💡 Artículos relacionados")
                else:
                    print("💡 Artículos diferentes")

        else:
            print("❌ No se pudo generar embedding")
            print("   Verifica que OPENAI_API_KEY esté configurado en .env")

    except Exception as e:
        print(f"❌ Error en embeddings: {str(e)}")
        print("   Asegúrate de tener OPENAI_API_KEY en .env")

    print("\n" + "="*60)
    print("EJEMPLO COMPLETADO")
    print("="*60 + "\n")


async def example_multi_source_scraping():
    """
    Ejemplo de scraping de múltiples fuentes en paralelo
    """
    print("\n" + "="*60)
    print("EJEMPLO: Scraping Multi-Fuente en Paralelo")
    print("="*60 + "\n")

    # Crear scrapers
    scrapers = [
        (ElTiempoScraper(), "El Tiempo"),
        (ElEspectadorScraper(), "El Espectador")
    ]

    # Scrape en paralelo
    print("🚀 Scraping de 2 fuentes en paralelo...\n")

    tasks = [scraper.scrape_frontpage() for scraper, _ in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Procesar resultados
    all_articles = []
    for (scraper, name), result in zip(scrapers, results):
        if isinstance(result, list):
            print(f"✅ {name}: {len(result)} artículos")
            all_articles.extend(result)
        else:
            print(f"❌ {name}: Error - {str(result)}")

    print(f"\n✅ Total: {len(all_articles)} artículos de todas las fuentes\n")

    # Eliminar duplicados por URL
    unique_urls = {article.url for article in all_articles}
    print(f"📊 Artículos únicos: {len(unique_urls)}")

    print("\n" + "="*60)
    print("EJEMPLO COMPLETADO")
    print("="*60 + "\n")


async def example_search_query():
    """
    Ejemplo de búsqueda semántica con embeddings
    """
    print("\n" + "="*60)
    print("EJEMPLO: Búsqueda Semántica")
    print("="*60 + "\n")

    try:
        embedding_service = EmbeddingService()

        # Generar embedding de una query
        query = "¿Qué dice el presidente sobre la economía?"
        print(f"🔍 Query: {query}\n")

        query_embedding = await embedding_service.embed_query(query)

        if query_embedding:
            print(f"✅ Query embedding generado")
            print(f"   Dimensiones: {len(query_embedding)}")
            print(f"\n💡 Este embedding se usaría para buscar artículos similares")
            print(f"   en la base de datos vectorial (Fase 3)\n")
        else:
            print("❌ No se pudo generar embedding")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("   Verifica OPENAI_API_KEY en .env")

    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n🎯 EJEMPLOS DE USO - COLOMBIA NEWS\n")
    print("Selecciona un ejemplo:")
    print("1. Pipeline completo (scraping + embeddings + similitud)")
    print("2. Scraping multi-fuente en paralelo")
    print("3. Búsqueda semántica con query")
    print("4. Ejecutar todos\n")

    choice = input("Opción (1-4): ").strip()

    if choice == "1":
        asyncio.run(example_complete_pipeline())
    elif choice == "2":
        asyncio.run(example_multi_source_scraping())
    elif choice == "3":
        asyncio.run(example_search_query())
    elif choice == "4":
        async def run_all():
            await example_complete_pipeline()
            await example_multi_source_scraping()
            await example_search_query()
        asyncio.run(run_all())
    else:
        print("Opción inválida")
