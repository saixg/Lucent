"""
Single responsibility: HTTP route handlers for creating, running, retrieving, and following up on text, URL, and image verifications.
"""

import asyncio
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.verification import Verification, EvidenceItem, FollowUpMessage
from app.schemas.verdict import (
    FollowUpRequest,
    VerificationCreateRequest,
    VerificationResponse,
)
from app.services.scraper import scrape_url_content
from app.services.claim_extractor import extract_claims
from app.services.evidence_gatherer import gather_evidence_for_claims
from app.services.verdict_synthesizer import synthesize_verdict
from app.services.follow_up import answer_follow_up
from app.services.image_forensics import check_image_forensics
from app.services.image_analyzer import analyze_image_with_vision

router = APIRouter(prefix="/verifications", tags=["Verifications"])


@router.post("/verify", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def verify_claim_end_to_end(
    payload: VerificationCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Core Verification Loop for Text and URL claims:
    1. Normalizes input (scrapes article text if URL).
    2. Extracts atomic checkable claims via Gemini.
    3. Searches for primary evidence & fact-checks via Tavily.
    4. Synthesizes 6-part verdict contract with Unverifiable guard.
    5. Persists verification and evidence items to PostgreSQL.
    """
    raw_input = payload.content.strip()
    content_type = payload.content_type.lower()
    scraped_text = None

    # Step 1: Ingestion & URL Normalization
    if content_type == "url" or raw_input.startswith("http://") or raw_input.startswith("https://"):
        content_type = "url"
        scraped_text = await scrape_url_content(raw_input)

    text_to_analyze = scraped_text if scraped_text else raw_input

    # Step 2: Claim Extraction
    extracted_claims = await extract_claims(text_to_analyze)
    if not extracted_claims:
        extracted_claims = [raw_input[:300]]

    # Step 3: Evidence Gathering
    evidence_items = await gather_evidence_for_claims(extracted_claims)

    # Step 4: Synthesis & Verdict Engine (strict 6-part contract)
    verdict = await synthesize_verdict(
        raw_input=raw_input,
        extracted_claims=extracted_claims,
        evidence_items=evidence_items,
    )

    # Step 5: Database Persistence
    verification = Verification(
        content_type=content_type,
        raw_input_ref=raw_input,
        extracted_claims=extracted_claims,
        verdict_label=verdict.verdict_label.value,
        confidence_level=verdict.confidence_level.value,
        confidence_reason=verdict.confidence_reason,
        explanation=verdict.explanation,
        status="completed",
    )
    db.add(verification)
    await db.flush()

    for item in verdict.evidence:
        ev_item = EvidenceItem(
            verification_id=verification.id,
            source_title=item.source_title,
            source_url=item.source_url,
            snippet=item.snippet,
            relation=item.relation.value,
        )
        db.add(ev_item)

    await db.commit()

    # Re-fetch with eager loaded relationships
    stmt = (
        select(Verification)
        .where(Verification.id == verification.id)
        .options(
            selectinload(Verification.evidence_items),
            selectinload(Verification.follow_up_messages),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.post("/verify-image", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def verify_image_end_to_end(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Image Verification Loop (Phase 2):
    1. Ingests uploaded image file.
    2. Runs Sightengine forensics & Gemini multimodal vision analysis.
    3. Queries Tavily for reverse-context and debunk evidence.
    4. Synthesizes 6-part verdict (AI-Generated, Altered, True, False, etc.).
    5. Persists verification and evidence items to PostgreSQL.
    """
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image file is empty.",
        )

    mime_type = file.content_type or "image/jpeg"
    filename = file.filename or "uploaded_image.jpg"

    # Step 1 & 2: Concurrently analyze image with vision + check forensics
    vision_task = analyze_image_with_vision(image_bytes, mime_type)
    forensics_task = check_image_forensics(image_bytes, mime_type)
    vision_output, forensics_output = await asyncio.gather(vision_task, forensics_task)

    claims = vision_output.extracted_claims
    if not claims:
        claims = [f"Image visual content: {vision_output.scene_description[:200]}"]

    # Step 3: Search for reverse context and news evidence
    evidence_items = await gather_evidence_for_claims(claims)

    # Attach forensic evidence card as a verifiable evidence item
    forensic_evidence = {
        "source_title": f"Sightengine Digital Forensics Analysis ({filename})",
        "source_url": "https://sightengine.com/docs/ai-generated-image-detection",
        "snippet": (
            f"Forensics Summary: {forensics_output['summary']} | "
            f"AI-Generated Likelihood: {int(forensics_output['ai_generated_score'] * 100)}%. "
            f"Visual Observations: {vision_output.visual_anomalies or 'Standard visual composition'}. "
            f"Scene Text: {vision_output.visible_text or 'None'}."
        ),
    }
    evidence_items.insert(0, forensic_evidence)

    # Step 4: Synthesis & Verdict
    raw_prompt = (
        f"[IMAGE FILE: {filename}]\n"
        f"Scene Description: {vision_output.scene_description}\n"
        f"Visible Text/Captions: {vision_output.visible_text}\n"
        f"Forensic Assessment: {forensics_output['summary']}"
    )

    verdict = await synthesize_verdict(
        raw_input=raw_prompt,
        extracted_claims=claims,
        evidence_items=evidence_items,
    )

    # If forensics strongly indicates AI-generation (> 75%), ensure verdict label reflects this
    verdict_label_val = verdict.verdict_label.value
    if forensics_output["is_ai_generated"] and verdict_label_val in ["True", "False", "Unverifiable"]:
        verdict_label_val = "AI-Generated"

    # Step 5: Database Persistence
    verification = Verification(
        content_type="image",
        raw_input_ref=f"[Image] {filename} — {vision_output.scene_description[:250]}",
        extracted_claims=claims,
        verdict_label=verdict_label_val,
        confidence_level=verdict.confidence_level.value,
        confidence_reason=verdict.confidence_reason,
        explanation=verdict.explanation,
        status="completed",
    )
    db.add(verification)
    await db.flush()

    for item in verdict.evidence:
        ev_item = EvidenceItem(
            verification_id=verification.id,
            source_title=item.source_title,
            source_url=item.source_url,
            snippet=item.snippet,
            relation=item.relation.value,
        )
        db.add(ev_item)

    await db.commit()

    # Re-fetch with eager loaded relationships
    stmt = (
        select(Verification)
        .where(Verification.id == verification.id)
        .options(
            selectinload(Verification.evidence_items),
            selectinload(Verification.follow_up_messages),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.post("", response_model=VerificationResponse, status_code=status.HTTP_201_CREATED)
async def create_verification_record(
    payload: VerificationCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Create a new pending verification record in the database."""
    verification = Verification(
        content_type=payload.content_type,
        raw_input_ref=payload.content,
        extracted_claims=[payload.content],
        status="pending",
    )
    db.add(verification)
    await db.commit()

    stmt = (
        select(Verification)
        .where(Verification.id == verification.id)
        .options(
            selectinload(Verification.evidence_items),
            selectinload(Verification.follow_up_messages),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.post("/{verification_id}/follow-up", response_model=VerificationResponse)
async def submit_follow_up_message(
    verification_id: str,
    payload: FollowUpRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Handle a user follow-up turn strictly grounded in the stored verification evidence.
    """
    stmt = (
        select(Verification)
        .where(Verification.id == verification_id)
        .options(
            selectinload(Verification.evidence_items),
            selectinload(Verification.follow_up_messages),
        )
    )
    result = await db.execute(stmt)
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification {verification_id} not found",
        )

    # 1. Save user question
    user_msg = FollowUpMessage(
        verification_id=verification.id,
        role="user",
        content=payload.message.strip(),
    )
    db.add(user_msg)
    await db.flush()

    # 2. Generate grounded assistant reply
    answer = await answer_follow_up(verification, payload.message.strip())

    # 3. Save assistant reply
    assistant_msg = FollowUpMessage(
        verification_id=verification.id,
        role="assistant",
        content=answer,
    )
    db.add(assistant_msg)
    await db.commit()

    # Expire cached relationship collections and re-query
    db.expire_all()
    stmt = (
        select(Verification)
        .where(Verification.id == verification_id)
        .options(
            selectinload(Verification.evidence_items),
            selectinload(Verification.follow_up_messages),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/{verification_id}", response_model=VerificationResponse)
async def get_verification(
    verification_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a verification and its evidence by ID."""
    stmt = (
        select(Verification)
        .where(Verification.id == verification_id)
        .options(
            selectinload(Verification.evidence_items),
            selectinload(Verification.follow_up_messages),
        )
    )
    result = await db.execute(stmt)
    verification = result.scalar_one_or_none()

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verification {verification_id} not found",
        )
    return verification


@router.get("", response_model=List[VerificationResponse])
async def list_verifications(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """List recent verifications."""
    stmt = (
        select(Verification)
        .options(
            selectinload(Verification.evidence_items),
            selectinload(Verification.follow_up_messages),
        )
        .order_by(Verification.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()
