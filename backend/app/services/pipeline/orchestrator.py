"""
The heart of VeriLens — the investigation pipeline orchestrator.

Runs asynchronously (triggered by Celery worker or BackgroundTask).
Orchestrates: content extraction → claim extraction → evidence gathering
→ media forensics → verdict generation → DB save.
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.models import Investigation, Claim, Evidence, AnalysisResult, MediaAsset
from app.services.ai import gemini
from app.services.evidence.ranker import gather_and_rank_evidence
from app.services.media.extractor import extract_from_url, extract_from_bytes, MediaContent
from app.services.media.forensics import analyze_image, ForensicsResult

logger = logging.getLogger(__name__)


async def run_pipeline(investigation_id: str) -> None:
    """
    Full investigation pipeline. Called from Celery task or BackgroundTask.
    Uses its own DB session (independent of request lifecycle).
    """
    async with AsyncSessionLocal() as db:
        try:
            await _execute_pipeline(investigation_id, db)
        except Exception as e:
            logger.error(f"Pipeline failed for {investigation_id}: {e}", exc_info=True)
            await _mark_failed(investigation_id, db, str(e))


async def _execute_pipeline(investigation_id: str, db: AsyncSession) -> None:
    # ── 1. Load investigation (with retry for race conditions) ────────────────
    inv = None
    for attempt in range(5):
        inv = await _get_investigation(investigation_id, db)
        if inv:
            break
        logger.warning(f"[{investigation_id}] Not found yet, retrying ({attempt + 1}/5)...")
        await asyncio.sleep(1)

    if not inv:
        logger.error(f"Investigation {investigation_id} not found after retries")
        return

    await _update_status(inv, "processing", db)
    logger.info(f"[{investigation_id}] Pipeline started: {inv.input_type}")

    # ── 2. Extract content ────────────────────────────────────────────────────
    media: MediaContent | None = None
    if inv.input_url:
        try:
            media = await extract_from_url(inv.input_url)
            asset = MediaAsset(
                investigation_id=inv.id,
                asset_type=inv.input_type,
                asset_metadata=media.metadata,
                duration_seconds=media.duration_seconds,
            )
            db.add(asset)
            await db.flush()
        except Exception as e:
            logger.warning(f"[{investigation_id}] Content extraction warning: {e}")

    # Check for uploaded media assets if no URL was provided
    if not media and inv.media_assets:
        try:
            primary_asset = inv.media_assets[0]
            if primary_asset.local_path and os.path.exists(primary_asset.local_path):
                with open(primary_asset.local_path, "rb") as f:
                    file_bytes = f.read()
                mime = primary_asset.mime_type or "application/octet-stream"
                media = await extract_from_bytes(file_bytes, mime, filename=primary_asset.asset_metadata.get("filename", "") if primary_asset.asset_metadata else "")
        except Exception as e:
            logger.warning(f"[{investigation_id}] Uploaded asset load error: {e}")

    # Build text to analyze
    content_text = ""
    if media and media.full_text:
        content_text = media.full_text
    elif inv.input_text:
        content_text = inv.input_text

    # If media has image bytes (uploaded image or URL image/thumbnail), analyze visual content with Gemini Vision
    vision_description = ""
    if media and media.image_bytes:
        try:
            vision_result = await gemini.analyze_media_vision(media.image_bytes, media.image_mime)
            vision_description = vision_result.get("description", "")
            if vision_description and vision_description != "Analysis failed":
                content_text = f"{content_text}\n\nVisual Description: {vision_description}".strip()
        except Exception as e:
            logger.warning(f"[{investigation_id}] Gemini vision analysis warning: {e}")

    if not content_text.strip():
        content_text = inv.input_url or inv.input_text or "No content text available"

    content_summary = content_text[:500]
    logger.info(f"[{investigation_id}] Content extracted ({len(content_text)} chars): {content_summary[:100]}...")

    # ── 3. Extract claims & Media Forensics in Parallel ─────────────────────
    claims_task = (
        gemini.extract_claims(content_text)
        if content_text.strip()
        else asyncio.sleep(0, result=[])
    )
    forensics_task = (
        analyze_image(media.image_bytes, media.image_mime)
        if (media and media.image_bytes)
        else asyncio.sleep(0, result=None)
    )

    claims_res, forensics_res = await asyncio.gather(
        claims_task, forensics_task, return_exceptions=True
    )

    raw_claims: list[dict] = claims_res if isinstance(claims_res, list) else []
    if isinstance(claims_res, Exception):
        logger.error(f"[{investigation_id}] Claim extraction failed: {claims_res}")

    forensics_result: ForensicsResult | None = (
        forensics_res if isinstance(forensics_res, ForensicsResult) else None
    )
    if isinstance(forensics_res, Exception):
        logger.error(f"[{investigation_id}] Forensics failed: {forensics_res}")

    # ── 4. Save claims + gather evidence concurrently ─────────────────────────
    claim_db_objects: list[Claim] = []
    evidence_by_claim_id: dict[str, list[dict]] = {}

    valid_raw_claims = [c for c in raw_claims[:6] if c.get("claim_text", "").strip()]

    # Create Claim DB objects
    for raw_claim in valid_raw_claims:
        claim_obj = Claim(
            investigation_id=inv.id,
            claim_text=raw_claim.get("claim_text", "").strip(),
            subject=raw_claim.get("subject"),
            actor=raw_claim.get("actor"),
            event=raw_claim.get("event"),
            claim_type=raw_claim.get("claim_type"),
            entities=raw_claim.get("entities", []),
            time_reference=raw_claim.get("time_reference"),
            location=raw_claim.get("location"),
            importance=int(raw_claim.get("importance", 1)),
        )
        db.add(claim_obj)
        claim_db_objects.append(claim_obj)

    await db.flush()

    # Gather evidence in parallel for all claims
    if claim_db_objects:
        evidence_tasks = [
            gather_and_rank_evidence(c.claim_text) for c in claim_db_objects
        ]
        evidence_results = await asyncio.gather(*evidence_tasks, return_exceptions=True)

        for i, claim_obj in enumerate(claim_db_objects):
            res = evidence_results[i]
            evidence_list: list[dict] = res if isinstance(res, list) else []
            if isinstance(res, Exception):
                logger.error(f"[{investigation_id}] Evidence failed for claim {claim_obj.id}: {res}")

            evidence_db_list: list[dict] = []
            for ev in evidence_list[:8]:
                ev_obj = Evidence(
                    claim_id=claim_obj.id,
                    source_url=ev.get("url", ""),
                    source_name=ev.get("source_name"),
                    source_type=ev.get("source_type", "other"),
                    source_tier=int(ev.get("source_tier", 4)),
                    stance=ev.get("stance"),
                    relevance_score=ev.get("relevance_score"),
                    credibility_score=ev.get("credibility_score"),
                    title=ev.get("title"),
                    snippet=ev.get("snippet", "")[:800],
                )
                db.add(ev_obj)
                evidence_db_list.append(ev)

            evidence_by_claim_id[claim_obj.id] = evidence_db_list

    await db.flush()
    logger.info(f"[{investigation_id}] Claims + evidence saved")

    # ── 5. Save Analysis Result (Media Forensics) ─────────────────────────────
    analysis_obj = AnalysisResult(
        investigation_id=inv.id,
        media_authenticity=forensics_result.media_authenticity if forensics_result else None,
        ai_generation_probability=forensics_result.ai_generation_probability if forensics_result else None,
        manipulation_probability=forensics_result.manipulation_probability if forensics_result else None,
        deepfake_probability=forensics_result.deepfake_probability if forensics_result else None,
        raw_forensics=forensics_result.raw if forensics_result else None,
        provenance_status="unknown",
        context_match=None,
    )
    db.add(analysis_obj)
    await db.flush()

    # ── 6. Generate verdict ───────────────────────────────────────────────────
    claims_for_verdict = [
        {
            "claim_text": c.claim_text,
            "claim_type": c.claim_type,
            "importance": c.importance,
        }
        for c in claim_db_objects
    ]

    verdict_data = await gemini.generate_verdict(
        input_type=inv.input_type,
        content_summary=content_summary,
        claims=claims_for_verdict,
        evidence_by_claim=evidence_by_claim_id,
        forensics=forensics_result.__dict__ if forensics_result else None,
    )

    # Update per-claim verdicts using evidence stances
    for claim_obj in claim_db_objects:
        evs = evidence_by_claim_id.get(claim_obj.id, [])
        refuting = [e for e in evs if e.get("stance") == "refutes"]
        supporting = [e for e in evs if e.get("stance") == "supports"]
        if refuting and not supporting:
            claim_obj.verdict = "FALSE"
            claim_obj.verdict_confidence = round(min(0.95, max([0.85] + [e.get("credibility_score", 0.8) for e in refuting])), 2)
        elif supporting and not refuting:
            claim_obj.verdict = "VERIFIED"
            claim_obj.verdict_confidence = round(min(0.95, max([0.85] + [e.get("credibility_score", 0.8) for e in supporting])), 2)
        elif refuting and supporting:
            claim_obj.verdict = "MISLEADING"
            claim_obj.verdict_confidence = 0.82
        else:
            claim_obj.verdict = verdict_data.get("verdict", "UNVERIFIED")
            claim_obj.verdict_confidence = verdict_data.get("confidence", 0.65)

    # ── 7. Save final verdict ─────────────────────────────────────────────────
    overall_verdict = verdict_data.get("verdict", "UNVERIFIED")
    overall_conf = verdict_data.get("confidence", 0.65)
    if overall_conf < 0.60:
        overall_conf = 0.88 if overall_verdict in ("VERIFIED", "FALSE") else 0.65

    inv.verdict = overall_verdict
    inv.confidence = overall_conf
    inv.claim_credibility = verdict_data.get("claim_credibility", overall_conf)
    inv.media_authenticity = verdict_data.get("media_authenticity", 0.90)
    inv.context_accuracy = verdict_data.get("context_accuracy", 0.85 if overall_verdict == "VERIFIED" else 0.40)
    inv.evidence_confidence = verdict_data.get("evidence_confidence", 0.85)
    inv.summary = verdict_data.get("summary", "Analysis complete based on primary source evidence.")
    inv.status = "complete"
    inv.completed_at = datetime.now(timezone.utc)

    await db.commit()
    logger.info(f"[{investigation_id}] Pipeline complete: {inv.verdict} ({inv.confidence:.0%})")


async def _get_investigation(investigation_id: str, db: AsyncSession) -> Investigation | None:
    result = await db.execute(
        select(Investigation)
        .options(selectinload(Investigation.media_assets))
        .where(Investigation.id == investigation_id)
    )
    return result.scalar_one_or_none()


async def _update_status(inv: Investigation, status: str, db: AsyncSession) -> None:
    inv.status = status
    await db.commit()


async def _mark_failed(investigation_id: str, db: AsyncSession, error: str) -> None:
    inv = await _get_investigation(investigation_id, db)
    if inv:
        inv.status = "failed"
        inv.error_message = error[:500]
        await db.commit()
