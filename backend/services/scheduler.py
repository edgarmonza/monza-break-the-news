"""
Scheduler service — runs the news pipeline on a configurable interval.

Uses APScheduler for reliable, in-process job scheduling.
Default: every 2 hours, processing CO + LATAM.
Can be expanded to MX, AR, CL, PE, EC as the product scales.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.interval import IntervalTrigger
    HAS_APSCHEDULER = True
except ImportError:
    AsyncIOScheduler = None  # type: ignore
    IntervalTrigger = None  # type: ignore
    HAS_APSCHEDULER = False

logger = logging.getLogger(__name__)

# ── Pipeline run status (in-memory, also persisted to pipeline_runs table) ──
_scheduler_state: Dict[str, Any] = {
    "is_running": False,
    "last_run_at": None,
    "last_run_status": None,
    "last_run_stats": {},
    "next_run_at": None,
    "total_runs": 0,
}


def get_scheduler_status() -> Dict[str, Any]:
    """Get current scheduler status for the API."""
    return {**_scheduler_state}


async def run_scheduled_pipeline(
    countries: Optional[List[str]] = None,
    decay_old_threads: bool = True,
) -> Dict[str, Any]:
    """
    Run one iteration of the pipeline. Called by the scheduler or manually.

    Steps:
    1. Run full pipeline (scrape → embed → cluster → thread)
    2. Save new articles and threads to DB
    3. Decay old thread scores
    4. Clean up very old threads (>7 days, score < 0.1)
    5. Log run to pipeline_runs table

    Returns:
        Dict with run statistics
    """
    from services.pipeline import NewsProcessingPipeline
    from db import Database, ArticleRepository, ThreadRepository
    from services.trending_service import TrendingService

    if _scheduler_state["is_running"]:
        logger.warning("Pipeline already running, skipping this iteration")
        return {"status": "skipped", "reason": "already_running"}

    _scheduler_state["is_running"] = True
    _scheduler_state["last_run_at"] = datetime.utcnow().isoformat()

    countries = countries or ["CO", "LATAM"]
    stats = {
        "started_at": datetime.utcnow().isoformat(),
        "countries": countries,
        "articles_scraped": 0,
        "articles_new": 0,
        "threads_created": 0,
        "threads_decayed": 0,
        "threads_cleaned": 0,
        "status": "running",
        "error": None,
    }

    try:
        db = Database()
        if not db.health_check():
            raise RuntimeError("Database connection failed")

        article_repo = ArticleRepository(db)
        thread_repo = ThreadRepository(db)
        pipeline = NewsProcessingPipeline()
        trending = TrendingService()

        # ── 1. Run pipeline ──
        logger.info(f"[Scheduler] Starting pipeline for {countries}")
        threads = await pipeline.run_full_pipeline(
            max_articles_per_source=20,
            min_cluster_size=2,
            countries=countries,
        )

        if not threads:
            logger.warning("[Scheduler] Pipeline returned 0 threads")
            stats["status"] = "completed_empty"
            return stats

        # ── 2. Save articles ──
        all_articles = []
        for thread in threads:
            if thread.articles:
                all_articles.extend(thread.articles)

        unique_articles = {a.url: a for a in all_articles}
        stats["articles_scraped"] = len(unique_articles)

        saved = 0
        for article in unique_articles.values():
            existing = await article_repo.get_by_url(article.url)
            if not existing:
                result = await article_repo.create(article)
                if result:
                    saved += 1

        stats["articles_new"] = saved

        # ── 3. Save threads ──
        created = 0
        for thread in threads:
            result = await thread_repo.create(thread)
            if result:
                created += 1

        stats["threads_created"] = created

        # ── 4. Decay old thread scores ──
        if decay_old_threads:
            decayed = await _decay_old_scores(thread_repo, trending)
            stats["threads_decayed"] = decayed

        # ── 5. Clean up very old threads ──
        cleaned = await _cleanup_old_threads(thread_repo)
        stats["threads_cleaned"] = cleaned

        stats["status"] = "completed"
        stats["finished_at"] = datetime.utcnow().isoformat()

        logger.info(
            f"[Scheduler] Done: {saved} new articles, "
            f"{created} threads, {stats['threads_decayed']} decayed, "
            f"{cleaned} cleaned"
        )

        # ── 6. Log run to DB ──
        try:
            started = datetime.fromisoformat(stats["started_at"])
            finished = datetime.utcnow()
            duration = (finished - started).total_seconds()

            db.client.table("pipeline_runs").insert({
                "status": "completed",
                "country": ",".join(countries),
                "articles_scraped": stats["articles_scraped"],
                "articles_new": stats["articles_new"],
                "threads_created": stats["threads_created"],
                "threads_updated": stats["threads_decayed"],
                "finished_at": finished.isoformat(),
                "duration_seconds": duration,
            }).execute()
        except Exception as e:
            logger.warning(f"[Scheduler] Failed to log run to DB: {e}")

    except Exception as e:
        logger.error(f"[Scheduler] Pipeline error: {e}", exc_info=True)
        stats["status"] = "failed"
        stats["error"] = str(e)

        try:
            db = Database()
            db.client.table("pipeline_runs").insert({
                "status": "failed",
                "country": ",".join(countries),
                "error_message": str(e)[:500],
            }).execute()
        except Exception:
            pass

    finally:
        _scheduler_state["is_running"] = False
        _scheduler_state["last_run_status"] = stats["status"]
        _scheduler_state["last_run_stats"] = stats
        _scheduler_state["total_runs"] += 1

    return stats


async def _decay_old_scores(thread_repo, trending_service) -> int:
    """Apply time-decay to all existing threads' trending scores."""
    try:
        from db import Database
        db = Database()
        result = db.client.table("threads").select("id, trending_score, created_at").execute()

        if not result.data:
            return 0

        decayed = 0
        for row in result.data:
            created_at = datetime.fromisoformat(row["created_at"])
            current_score = row["trending_score"]

            new_score = trending_service.calculate_decay_adjusted_score(
                current_score, created_at
            )

            # Only update if score changed meaningfully
            if abs(new_score - current_score) > 0.01:
                from uuid import UUID
                await thread_repo.update_trending_score(UUID(row["id"]), round(new_score, 3))
                decayed += 1

        return decayed

    except Exception as e:
        logger.error(f"Error decaying scores: {e}")
        return 0


async def _cleanup_old_threads(thread_repo) -> int:
    """Remove threads older than 7 days with very low scores."""
    try:
        from db import Database
        db = Database()
        cutoff = (datetime.utcnow() - timedelta(days=7)).isoformat()

        result = db.client.table("threads")\
            .select("id")\
            .lt("trending_score", 0.05)\
            .lt("created_at", cutoff)\
            .execute()

        if not result.data:
            return 0

        cleaned = 0
        for row in result.data:
            from uuid import UUID
            deleted = await thread_repo.delete(UUID(row["id"]))
            if deleted:
                cleaned += 1

        return cleaned

    except Exception as e:
        logger.error(f"Error cleaning old threads: {e}")
        return 0


# ── Scheduler setup ──

_scheduler = None


def start_scheduler(
    interval_hours: int = 2,
    countries: Optional[List[str]] = None,
):
    """
    Start the background scheduler.
    Call this from the FastAPI startup event.
    """
    global _scheduler

    if not HAS_APSCHEDULER:
        logger.warning("[Scheduler] APScheduler not installed — skipping (Vercel?)")
        return

    if _scheduler and _scheduler.running:
        logger.warning("Scheduler already running")
        return

    countries = countries or ["CO", "LATAM"]
    _scheduler = AsyncIOScheduler()

    _scheduler.add_job(
        run_scheduled_pipeline,
        trigger=IntervalTrigger(hours=interval_hours),
        kwargs={"countries": countries},
        id="news_pipeline",
        name=f"News Pipeline (every {interval_hours}h)",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )

    _scheduler.start()

    next_run = _scheduler.get_job("news_pipeline").next_run_time
    _scheduler_state["next_run_at"] = next_run.isoformat() if next_run else None

    logger.info(
        f"[Scheduler] Started — interval={interval_hours}h, "
        f"countries={countries}, next_run={next_run}"
    )


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Stopped")
    _scheduler = None
