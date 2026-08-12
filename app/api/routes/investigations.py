from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.models import Investigation, Claim, Evidence, AnalysisResult
from app.schemas.investigation import (
    InvestigationCreate,
    InvestigationOut,
    InvestigationListOut,
)

router = APIRouter(prefix="/investigations", tags=["investigations"])


# ─── helpers ─────────────────────────────────────────────────────────────────

async def _load_full(investigation_id: str, db: AsyncSession) -> Investigation | None:
    """Load investigation with all related data eagerly."""
    result = await db.execute(
        select(Investigation)
        .options(
            selectinload(Investigation.claims).selectinload(Claim.evidence),
            selectinload(Investigation.analysis_results),
            selectinload(Investigation.media_assets),
        )
        .where(Investigation.id == investigation_id)
    )
    return result.scalar_one_or_none()


def _enqueue_pipeline(investigation_id: str) -> None:
    """Try Celery first, fall back to asyncio BackgroundTask."""
    try:
        from app.workers.tasks import run_investigation_pipeline
        run_investigation_pipeline.delay(investigation_id)
    except Exception:
        pass  # Celery not running — pipeline runs via BackgroundTask fallback


async def _run_pipeline_bg(investigation_id: str) -> None:
    """Async fallback when Celery is unavailable."""
    from app.services.pipeline.orchestrator import run_pipeline
    await run_pipeline(investigation_id)


# ─── routes ──────────────────────────────────────────────────────────────────

@router.post("/", response_model=InvestigationOut, status_code=status.HTTP_201_CREATED)
async def create_investigation(
    payload: InvestigationCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new investigation and kick off the async pipeline.
    Returns immediately with status=pending.
    """
    inv = Investigation(
        input_type=payload.input_type,
        input_url=str(payload.input_url) if payload.input_url else None,
        input_text=payload.input_text,
        platform=payload.platform,
        user_id=payload.user_id,
    )
    db.add(inv)
    # CRITICAL: commit NOW so the background task's independent session can see the row.
    # Without this, the pipeline races the request's auto-commit and loses.
    await db.commit()

    # Schedule pipeline — only use BackgroundTask (Celery fallback is handled inside _enqueue_pipeline if needed)
    background_tasks.add_task(_run_pipeline_bg, inv.id)

    # Load with relations for response (re-fetch after commit)
    inv_full = await _load_full(inv.id, db)
    return inv_full


@router.get("/", response_model=list[InvestigationListOut])
async def list_investigations(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List recent investigations (newest first)."""
    result = await db.execute(
        select(Investigation)
        .order_by(desc(Investigation.created_at))
        .limit(min(limit, 100))
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/{investigation_id}/status")
async def get_investigation_status(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Lightweight polling endpoint — returns status + verdict only."""
    result = await db.execute(
        select(Investigation.id, Investigation.status, Investigation.verdict, Investigation.confidence, Investigation.summary)
        .where(Investigation.id == investigation_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return {
        "id": row.id,
        "status": row.status,
        "verdict": row.verdict,
        "confidence": row.confidence,
        "summary": row.summary,
    }


@router.get("/{investigation_id}", response_model=InvestigationOut)
async def get_investigation(
    investigation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Full investigation with claims, evidence, analysis."""
    inv = await _load_full(investigation_id, db)
    if not inv:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return inv
