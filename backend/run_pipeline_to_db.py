"""
Script para ejecutar pipeline completo y guardar resultados en Supabase.

Usage:
  python run_pipeline_to_db.py                     # Colombia only
  python run_pipeline_to_db.py CO MX AR            # Multi-country
  python run_pipeline_to_db.py CO MX AR CL PE EC   # Full LATAM
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.pipeline import NewsProcessingPipeline
from db import Database, ArticleRepository, ThreadRepository
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def save_articles_to_db(articles, article_repo):
    """Guarda artículos en la base de datos"""
    saved_count = 0
    skipped_count = 0

    for article in articles:
        # Verificar si ya existe
        existing = await article_repo.get_by_url(article.url)
        if existing:
            logger.debug(f"Article already exists: {article.url}")
            skipped_count += 1
            continue

        # Guardar nuevo artículo
        result = await article_repo.create(article)
        if result:
            saved_count += 1
        else:
            logger.warning(f"Failed to save article: {article.url}")

    logger.info(f"Articles saved: {saved_count}, skipped: {skipped_count}")
    return saved_count, skipped_count


async def save_threads_to_db(threads, thread_repo):
    """Guarda threads en la base de datos"""
    saved_count = 0

    for thread in threads:
        result = await thread_repo.create(thread)
        if result:
            saved_count += 1
            logger.info(f"Thread saved: {thread.title_id}")
        else:
            logger.warning(f"Failed to save thread: {thread.title_id}")

    logger.info(f"Threads saved: {saved_count}")
    return saved_count


async def main():
    """Ejecuta pipeline y guarda en BD"""
    # Parse country arguments
    countries = sys.argv[1:] if len(sys.argv) > 1 else ["CO"]
    countries = [c.upper().strip() for c in countries]

    print("\n" + "="*70)
    print(f"PIPELINE TO DATABASE — Countries: {', '.join(countries)}")
    print("="*70 + "\n")

    print("Este script ejecutará:")
    print(f"1. Pipeline completo para: {', '.join(countries)}")
    print("2. Guardará artículos en Supabase")
    print("3. Guardará threads en Supabase")
    print()

    # Verificar configuración
    try:
        db = Database()
        healthy = db.health_check()
        if not healthy:
            print("❌ Error: No se puede conectar a Supabase")
            print("   Verifica SUPABASE_URL y SUPABASE_KEY en .env")
            return
        print("✅ Conexión a Supabase OK\n")
    except Exception as e:
        print(f"❌ Error de configuración: {e}")
        print("   Asegúrate de tener SUPABASE_URL y SUPABASE_KEY en .env")
        return

    # Confirmar ejecución (auto-yes para ejecución no interactiva)
    # response = input("¿Continuar? (y/n): ").strip().lower()
    # if response != 'y':
    #     print("Cancelado")
    #     return
    print("Continuando automáticamente...")

    print("\n🚀 Iniciando pipeline...\n")

    # 1. EJECUTAR PIPELINE
    pipeline = NewsProcessingPipeline()

    try:
        threads = await pipeline.run_full_pipeline(
            max_articles_per_source=20,
            min_cluster_size=2,
            countries=countries,
        )

        if not threads:
            print("\n❌ No se generaron threads")
            return

        print(f"\n✅ Pipeline completado: {len(threads)} threads generados\n")

    except Exception as e:
        print(f"\n❌ Error en pipeline: {e}")
        logger.exception("Pipeline error:")
        return

    # 2. GUARDAR EN BASE DE DATOS
    print("💾 Guardando en base de datos...\n")

    article_repo = ArticleRepository(db)
    thread_repo = ThreadRepository(db)

    # Extraer todos los artículos de los threads
    all_articles = []
    for thread in threads:
        if thread.articles:
            all_articles.extend(thread.articles)

    # Eliminar duplicados por URL
    unique_articles = {article.url: article for article in all_articles}
    unique_articles_list = list(unique_articles.values())

    print(f"📰 Guardando {len(unique_articles_list)} artículos únicos...")
    articles_saved, articles_skipped = await save_articles_to_db(
        unique_articles_list,
        article_repo
    )

    print(f"🧵 Guardando {len(threads)} threads...")
    threads_saved = await save_threads_to_db(threads, thread_repo)

    # RESUMEN
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Artículos guardados: {articles_saved}")
    print(f"Artículos ya existían: {articles_skipped}")
    print(f"Threads guardados: {threads_saved}")
    print("="*70 + "\n")

    # Mostrar threads guardados
    if threads_saved > 0:
        print("🎉 Threads creados:\n")
        for i, thread in enumerate(threads, 1):
            print(f"{i}. {thread.title_id}")
            print(f"   Score: {thread.trending_score:.3f}")
            print(f"   Artículos: {len(thread.article_ids)}")
            print()

    print("✅ Pipeline a DB completado exitosamente")
    print("   Puedes ver los datos en:")
    print("   - API: http://localhost:8000/api/feed")
    print("   - Docs: http://localhost:8000/docs\n")


if __name__ == "__main__":
    asyncio.run(main())
