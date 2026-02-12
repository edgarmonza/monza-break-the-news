"""
Script de prueba para Fase 2: Clustering + Thread Generation
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services import NewsProcessingPipeline
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_full_pipeline():
    """Prueba el pipeline completo end-to-end"""
    print("\n" + "="*70)
    print("PRUEBA FASE 2: PIPELINE COMPLETO")
    print("="*70 + "\n")

    print("⚠️  NOTA: Esta prueba requiere:")
    print("  • OPENAI_API_KEY en .env (para embeddings)")
    print("  • ANTHROPIC_API_KEY en .env (para thread generation)")
    print()

    # Crear pipeline
    pipeline = NewsProcessingPipeline()

    try:
        # Ejecutar pipeline completo
        print("🚀 Iniciando pipeline completo...\n")
        print("Esto tomará ~2-3 minutos (scraping + embeddings + LLM)\n")

        threads = await pipeline.run_full_pipeline(
            max_articles_per_source=15,  # Limitar para testing
            min_cluster_size=2
        )

        # Mostrar resultados
        if not threads:
            print("\n❌ No se generaron threads")
            print("   Posibles causas:")
            print("   - Artículos muy diferentes (no forman clusters)")
            print("   - Problemas con API keys")
            print("   - Sitios web no accesibles")
            return

        print("\n" + "="*70)
        print(f"✅ THREADS GENERADOS: {len(threads)}")
        print("="*70 + "\n")

        # Mostrar cada thread
        for i, thread in enumerate(threads, 1):
            category = get_category_emoji(thread.trending_score)

            print(f"{i}. {category} {thread.title_id}")
            print(f"   📊 Score: {thread.trending_score:.3f}")
            print(f"   📰 Título: {thread.display_title}")
            print(f"   📄 Artículos: {len(thread.article_ids)}")

            # Fuentes
            sources = set(a.source for a in thread.articles)
            print(f"   📡 Fuentes: {', '.join(sources)}")

            # Resumen
            print(f"\n   💬 Resumen:")
            print(f"   {thread.summary}\n")

            # Preguntas sugeridas
            print(f"   ❓ Preguntas sugeridas:")
            for q in thread.suggested_questions:
                print(f"      • {q}")

            print("\n" + "-"*70 + "\n")

        # Exportar a JSON
        export_path = Path(__file__).parent / "threads_output.json"
        export_threads_to_json(threads, export_path)
        print(f"💾 Threads exportados a: {export_path}\n")

    except Exception as e:
        print(f"\n❌ Error en pipeline: {str(e)}")
        logger.exception("Error detallado:")


async def test_clustering_only():
    """Prueba solo el clustering (sin LLM)"""
    print("\n" + "="*70)
    print("PRUEBA: CLUSTERING SEMÁNTICO (sin LLM)")
    print("="*70 + "\n")

    from scrapers import ElTiempoScraper
    from services import EmbeddingService, ClusteringService

    # 1. Scraping
    print("📡 Scraping El Tiempo...\n")
    scraper = ElTiempoScraper()
    articles = await scraper.scrape_frontpage()
    print(f"✅ {len(articles)} artículos scraped\n")

    # 2. Contenido completo (solo primeros 20)
    print("📄 Extrayendo contenido completo...\n")
    full_articles = []
    for article in articles[:20]:
        full = await scraper.scrape_article_content(article.url)
        if full:
            full_articles.append(full)
        if len(full_articles) >= 15:  # Límite para testing
            break

    print(f"✅ {len(full_articles)} artículos con contenido\n")

    # 3. Embeddings
    print("🧠 Generando embeddings...\n")
    embedding_service = EmbeddingService()
    embedded = await embedding_service.embed_articles_batch(full_articles)
    print(f"✅ {len(embedded)} artículos con embeddings\n")

    # 4. Clustering
    print("🔍 Ejecutando clustering...\n")
    clustering_service = ClusteringService()
    clusters = clustering_service.cluster_articles(embedded)

    # Mostrar clusters
    print("\n" + "="*70)
    print(f"CLUSTERS ENCONTRADOS: {len(clusters)}")
    print("="*70 + "\n")

    for cluster_id, cluster_articles in clusters.items():
        if cluster_id == -1:
            print(f"🔸 OUTLIERS: {len(cluster_articles)} artículos sin cluster\n")
            continue

        print(f"📦 CLUSTER {cluster_id}: {len(cluster_articles)} artículos")

        # Mostrar títulos
        for article in cluster_articles[:3]:  # Primeros 3
            print(f"   • [{article.source}] {article.title}")

        if len(cluster_articles) > 3:
            print(f"   ... y {len(cluster_articles) - 3} más")

        print()


async def test_llm_generation():
    """Prueba solo la generación de LLM"""
    print("\n" + "="*70)
    print("PRUEBA: GENERACIÓN DE THREADS CON LLM")
    print("="*70 + "\n")

    from scrapers import ElTiempoScraper
    from services import LLMThreadService
    from models import ArticleBase

    # Crear artículos de ejemplo (simulados)
    example_articles = [
        ArticleBase(
            url="https://example.com/1",
            title="Gobierno anuncia nueva reforma tributaria con impuestos a bebidas azucaradas",
            content="El gobierno colombiano presentó hoy una reforma tributaria que incluye impuestos adicionales a bebidas azucaradas y alimentos ultra-procesados. La medida busca recaudar $5 billones adicionales.",
            source="eltiempo"
        ),
        ArticleBase(
            url="https://example.com/2",
            title="Congreso debate propuesta de reforma tributaria del gobierno",
            content="El Congreso de la República inició el debate sobre la reforma tributaria propuesta por el gobierno, que genera controversia entre empresarios y economistas.",
            source="elespectador"
        ),
        ArticleBase(
            url="https://example.com/3",
            title="Empresarios rechazan nueva reforma tributaria: 'afectará inversión'",
            content="Los gremios empresariales manifestaron su rechazo a la reforma tributaria, argumentando que aumentará costos y reducirá la inversión privada en el país.",
            source="semana"
        )
    ]

    print("📝 Artículos de ejemplo:")
    for i, article in enumerate(example_articles, 1):
        print(f"{i}. [{article.source}] {article.title}")

    print("\n🤖 Generando metadata con Claude...\n")

    llm_service = LLMThreadService()
    metadata = await llm_service.generate_thread_metadata(example_articles)

    if metadata:
        print("✅ METADATA GENERADA:\n")
        print(f"🏷️  Handle: {metadata.title_id}")
        print(f"📰 Título: {metadata.display_title}")
        print(f"\n💬 Resumen:\n{metadata.summary}\n")
        print(f"❓ Preguntas sugeridas:")
        for q in metadata.suggested_questions:
            print(f"   • {q}")
        print()
    else:
        print("❌ No se pudo generar metadata")


def get_category_emoji(score: float) -> str:
    """Retorna emoji según el score"""
    if score >= 0.8:
        return "🔥"  # Hot
    elif score >= 0.6:
        return "📈"  # Trending
    elif score >= 0.4:
        return "📊"  # Active
    else:
        return "📰"  # Normal


def export_threads_to_json(threads, path: Path):
    """Exporta threads a JSON"""
    data = []
    for thread in threads:
        data.append({
            "title_id": thread.title_id,
            "display_title": thread.display_title,
            "summary": thread.summary,
            "trending_score": thread.trending_score,
            "n_articles": len(thread.article_ids),
            "sources": list(set(a.source for a in thread.articles)),
            "suggested_questions": thread.suggested_questions,
            "articles": [
                {
                    "title": a.title,
                    "source": a.source,
                    "url": a.url
                }
                for a in thread.articles
            ]
        })

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def main():
    """Menú principal"""
    print("\n" + "="*70)
    print("PRUEBAS - FASE 2: CLUSTERING & THREAD GENERATION")
    print("="*70 + "\n")

    print("Selecciona una prueba:")
    print("1. Pipeline completo (scraping → threads)")
    print("2. Solo clustering (scraping → embeddings → clusters)")
    print("3. Solo LLM (generar metadata de ejemplo)")
    print("4. Todas las pruebas")
    print()

    choice = input("Opción (1-4): ").strip()

    if choice == "1":
        await test_full_pipeline()
    elif choice == "2":
        await test_clustering_only()
    elif choice == "3":
        await test_llm_generation()
    elif choice == "4":
        await test_llm_generation()
        print("\n" + "="*70 + "\n")
        await test_clustering_only()
        print("\n" + "="*70 + "\n")
        await test_full_pipeline()
    else:
        print("Opción inválida")


if __name__ == "__main__":
    asyncio.run(main())
