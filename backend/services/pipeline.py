"""
Pipeline completo de procesamiento: scraping → embeddings → clustering → threads
"""
from typing import List, Dict
import logging
import asyncio
from datetime import datetime

from scrapers import (
    # Colombianos (nacionales)
    ElTiempoScraper, ElEspectadorScraper, SemanaScraper,
    LaSillaVaciaScraper, PortafolioScraper, CaracolScraper,
    PulzoScraper, Las2OrillasScraper,
    # Colombianos (regionales)
    ElHeraldoScraper, ElColombianoScraper, ElPaisCaliScraper,
    VanguardiaScraper, ElUniversalScraper, LaOpinionScraper,
    # Internacionales (español)
    BBCMundoScraper, CNNEspanolScraper, France24Scraper, DWEspanolScraper,
    InfobaeScraper, ElPaisScraper,
    # Internacionales (inglés)
    ReutersScraper, APNewsScraper, TheGuardianScraper, BloombergScraper,
    InSightCrimeScraper, ColombiaReportsScraper, NYTimesScraper, DWEnglishScraper,
)
from scrapers.base import BaseScraper
from services.embedding_service import EmbeddingService
from services.clustering_service import ClusteringService
from services.llm_service import LLMThreadService
from services.trending_service import TrendingService
from models.article import Article, ArticleBase, Thread

logger = logging.getLogger(__name__)


class NewsProcessingPipeline:
    """Pipeline end-to-end para procesar noticias y generar threads"""

    def __init__(self):
        self.scrapers: List[BaseScraper] = [
            # ── Medios colombianos (nacionales) ──
            ElTiempoScraper(),
            ElEspectadorScraper(),
            SemanaScraper(),
            LaSillaVaciaScraper(),
            PortafolioScraper(),
            CaracolScraper(),
            PulzoScraper(),
            Las2OrillasScraper(),
            # ── Medios colombianos (regionales) ──
            ElHeraldoScraper(),
            ElColombianoScraper(),
            ElPaisCaliScraper(),
            VanguardiaScraper(),
            ElUniversalScraper(),
            LaOpinionScraper(),
            # ── Internacionales (español) ──
            BBCMundoScraper(),
            CNNEspanolScraper(),
            France24Scraper(),
            DWEspanolScraper(),
            InfobaeScraper(),
            ElPaisScraper(),
            # ── Internacionales (inglés) ──
            ReutersScraper(),
            APNewsScraper(),
            TheGuardianScraper(),
            BloombergScraper(),
            InSightCrimeScraper(),
            ColombiaReportsScraper(),
            NYTimesScraper(),
            DWEnglishScraper(),
        ]
        self.embedding_service = EmbeddingService()
        self.clustering_service = ClusteringService()
        self.llm_service = LLMThreadService()
        self.trending_service = TrendingService()

    async def run_full_pipeline(
        self,
        max_articles_per_source: int = 20,
        min_cluster_size: int = 2
    ) -> List[Thread]:
        """
        Ejecuta el pipeline completo:
        1. Scraping de todas las fuentes
        2. Extracción de contenido completo
        3. Generación de embeddings
        4. Clustering de artículos similares
        5. Generación de threads con LLM
        6. Cálculo de trending scores
        7. Ranking y filtrado

        Returns:
            Lista de Threads listos para servir
        """
        logger.info("="*60)
        logger.info("INICIANDO PIPELINE COMPLETO")
        logger.info("="*60)

        start_time = datetime.utcnow()

        # PASO 1: SCRAPING
        logger.info("\n[1/7] SCRAPING de fuentes...")
        scraped_articles = await self._run_scraping(max_articles_per_source)

        if not scraped_articles:
            logger.error("No se obtuvieron artículos del scraping")
            return []

        # PASO 2: CONTENT EXTRACTION
        logger.info(f"\n[2/7] EXTRACCIÓN de contenido completo...")
        full_articles = await self._extract_full_content(scraped_articles)

        if not full_articles:
            logger.error("No se pudo extraer contenido de ningún artículo")
            return []

        # PASO 3: EMBEDDINGS
        logger.info(f"\n[3/7] GENERACIÓN de embeddings...")
        embedded_articles = await self._generate_embeddings(full_articles)

        if not embedded_articles:
            logger.error("No se generaron embeddings")
            return []

        # PASO 4: CLUSTERING
        logger.info(f"\n[4/7] CLUSTERING semántico...")
        clusters = await self._cluster_articles(embedded_articles)

        if not clusters:
            logger.error("No se formaron clusters")
            return []

        # Filtrar clusters válidos
        valid_clusters = self.clustering_service.filter_valid_clusters(
            clusters,
            min_articles=min_cluster_size,
            min_sources=1
        )

        logger.info(f"Clusters válidos: {len(valid_clusters)}")

        # PASO 5: THREAD GENERATION
        logger.info(f"\n[5/7] GENERACIÓN de threads con LLM...")
        threads = await self._generate_threads(valid_clusters)

        if not threads:
            logger.warning("No se generaron threads")
            return []

        # PASO 6: TRENDING SCORES
        logger.info(f"\n[6/7] CÁLCULO de trending scores...")
        threads_with_scores = self._calculate_trending_scores(threads)

        # PASO 7: RANKING
        logger.info(f"\n[7/7] RANKING y filtrado final...")
        ranked_threads = self.trending_service.rank_threads(threads_with_scores)

        # Log final
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info("\n" + "="*60)
        logger.info("PIPELINE COMPLETADO")
        logger.info(f"Tiempo total: {elapsed:.1f}s")
        logger.info(f"Threads generados: {len(ranked_threads)}")
        logger.info("="*60 + "\n")

        return ranked_threads

    async def _run_scraping(
        self,
        max_per_source: int
    ) -> List:
        """Scraping paralelo de todas las fuentes"""
        logger.info(f"Scraping {len(self.scrapers)} fuentes...")

        tasks = [scraper.scrape_frontpage() for scraper in self.scrapers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_articles = []
        for scraper, result in zip(self.scrapers, results):
            if isinstance(result, Exception):
                logger.error(f"Error en {scraper.source_name}: {str(result)}")
            else:
                # Limitar artículos por fuente
                articles = result[:max_per_source]
                all_articles.extend(articles)
                logger.info(
                    f"  ✓ {scraper.source_name}: {len(articles)} artículos"
                )

        logger.info(f"Total scraped: {len(all_articles)} artículos")
        return all_articles

    async def _extract_full_content(
        self,
        scraped_articles: List
    ) -> List[ArticleBase]:
        """Extrae contenido completo de artículos"""
        logger.info(f"Extrayendo contenido de {len(scraped_articles)} artículos...")

        full_articles = []

        # Procesar en batches para no saturar
        batch_size = 10
        for i in range(0, len(scraped_articles), batch_size):
            batch = scraped_articles[i:i + batch_size]

            # Intentar con diferentes scrapers
            tasks = []
            for article in batch:
                # Encontrar el scraper correcto por source
                scraper = next(
                    (s for s in self.scrapers if s.source_name == article.source),
                    None
                )
                if scraper:
                    tasks.append(scraper.scrape_article_content(article.url))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, ArticleBase):
                    full_articles.append(result)

            logger.info(
                f"  Procesado batch {i//batch_size + 1}: "
                f"{len(full_articles)} artículos completos"
            )

            # Pequeña pausa entre batches
            if i + batch_size < len(scraped_articles):
                await asyncio.sleep(0.5)

        logger.info(
            f"Contenido extraído: {len(full_articles)}/{len(scraped_articles)}"
        )
        return full_articles

    async def _generate_embeddings(
        self,
        articles: List[ArticleBase]
    ) -> List[Article]:
        """Genera embeddings para artículos"""
        logger.info(f"Generando embeddings para {len(articles)} artículos...")

        embedded_articles = await self.embedding_service.embed_articles_batch(
            articles,
            batch_size=10
        )

        logger.info(f"Embeddings generados: {len(embedded_articles)}")
        return embedded_articles

    async def _cluster_articles(
        self,
        articles: List[Article]
    ) -> Dict[int, List[Article]]:
        """Agrupa artículos en clusters"""
        logger.info("Ejecutando clustering semántico...")

        clusters = self.clustering_service.cluster_articles(articles)

        # Log estadísticas
        stats = self.clustering_service.get_cluster_statistics(clusters)
        for cluster_id, stat in stats.items():
            logger.info(
                f"  Cluster {cluster_id}: {stat['size']} artículos, "
                f"{stat['n_sources']} fuentes, "
                f"similitud={stat['avg_similarity']:.3f}"
            )

        return clusters

    async def _generate_threads(
        self,
        clusters: Dict[int, List[Article]]
    ) -> List[Thread]:
        """Genera threads con metadata LLM"""
        logger.info(f"Generando metadata para {len(clusters)} clusters...")

        threads = []

        for cluster_id, articles in clusters.items():
            try:
                # Generar metadata con LLM
                metadata = await self.llm_service.generate_thread_metadata(articles)

                if not metadata:
                    logger.warning(f"No se generó metadata para cluster {cluster_id}")
                    continue

                # Crear Thread
                thread = Thread(
                    title_id=metadata.title_id,
                    display_title=metadata.display_title,
                    summary=metadata.summary,
                    article_ids=[a.id for a in articles],
                    articles=articles,
                    suggested_questions=metadata.suggested_questions,
                    trending_score=0.0  # Se calculará después
                )

                threads.append(thread)
                logger.info(f"  ✓ Thread creado: {thread.title_id}")

            except Exception as e:
                logger.error(f"Error generando thread para cluster {cluster_id}: {e}")
                continue

        logger.info(f"Threads generados: {len(threads)}")
        return threads

    def _calculate_trending_scores(self, threads: List[Thread]) -> List[Thread]:
        """Calcula y asigna trending scores"""
        logger.info(f"Calculando trending scores...")

        for thread in threads:
            # Calcular score base
            score = self.trending_service.calculate_trending_score(
                thread.articles
            )

            # Verificar si merece boost
            should_boost, multiplier = self.trending_service.should_boost_score(
                thread.articles
            )

            if should_boost:
                score *= multiplier
                logger.info(
                    f"  BOOST para {thread.title_id}: "
                    f"{score/multiplier:.3f} → {score:.3f}"
                )

            thread.trending_score = min(1.0, score)  # Cap at 1.0

            category = self.trending_service.get_trending_category(score)
            logger.info(
                f"  {thread.title_id}: {score:.3f} [{category.upper()}]"
            )

        return threads

    async def quick_pipeline(
        self,
        scraped_articles: List,
        skip_full_content: bool = False
    ) -> List[Thread]:
        """
        Pipeline rápido que salta el scraping (útil para testing)

        Args:
            scraped_articles: Artículos ya scraped
            skip_full_content: Si True, usa solo títulos (más rápido pero menos preciso)
        """
        logger.info("EJECUTANDO PIPELINE RÁPIDO")

        if skip_full_content:
            # Crear ArticleBase con solo título y URL
            articles = [
                ArticleBase(
                    url=a.url,
                    title=a.title,
                    content=a.title,  # Usar título como contenido
                    source=a.source
                )
                for a in scraped_articles
            ]
        else:
            articles = await self._extract_full_content(scraped_articles)

        embedded_articles = await self._generate_embeddings(articles)
        clusters = await self._cluster_articles(embedded_articles)
        valid_clusters = self.clustering_service.filter_valid_clusters(clusters)
        threads = await self._generate_threads(valid_clusters)
        threads_with_scores = self._calculate_trending_scores(threads)
        ranked_threads = self.trending_service.rank_threads(threads_with_scores)

        return ranked_threads
