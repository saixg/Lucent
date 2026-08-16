"""
Celery tasks — wraps the async pipeline in a sync Celery task.
"""
import asyncio
import logging

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="verilens.run_pipeline",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
)
def run_investigation_pipeline(self, investigation_id: str) -> dict:
    """
    Celery task that runs the full async investigation pipeline.
    Uses asyncio.run() to execute the async orchestrator.
    """
    logger.info(f"Celery task started for investigation {investigation_id}")
    try:
        from app.services.pipeline.orchestrator import run_pipeline
        asyncio.run(run_pipeline(investigation_id))
        return {"status": "complete", "investigation_id": investigation_id}
    except Exception as exc:
        logger.error(f"Pipeline task failed: {exc}", exc_info=True)
        try:
            self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {"status": "failed", "investigation_id": investigation_id, "error": str(exc)}
