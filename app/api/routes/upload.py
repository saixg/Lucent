from __future__ import annotations

import asyncio
import hashlib
import io
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.models import Investigation, MediaAsset
from app.schemas.investigation import InvestigationOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "video/mp4", "video/webm", "video/quicktime",
    "audio/mpeg", "audio/wav", "audio/ogg", "audio/mp4",
}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB


async def _run_pipeline_bg(investigation_id: str) -> None:
    try:
        logger.info(f"Starting background pipeline for upload {investigation_id}")
        from app.services.pipeline.orchestrator import run_pipeline
        await run_pipeline(investigation_id)
    except Exception as e:
        logger.error(f"Upload background pipeline failed for {investigation_id}: {e}", exc_info=True)


@router.post("/", response_model=InvestigationOut, status_code=201)
async def upload_media(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a media file (image/video/audio).
    Creates an investigation and kicks off the pipeline.
    """
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, detail=f"Unsupported file type: {file.content_type}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, detail="File exceeds 200 MB limit")

    # Determine input_type from MIME
    major = (file.content_type or "").split("/")[0]
    input_type = major if major in ("image", "video", "audio") else "image"

    file_hash = hashlib.sha256(content).hexdigest()

    inv = Investigation(
        input_type=input_type,
        platform="web",
        user_id=user_id,
    )
    db.add(inv)
    await db.flush()

    # Try to upload to Supabase Storage in background thread with 2s timeout
    storage_url = None
    try:
        def _do_supabase_upload() -> str:
            from app.core.config import get_settings
            from supabase import create_client

            settings = get_settings()
            supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
            ext = (file.filename or "upload").rsplit(".", 1)[-1] if file.filename else "bin"
            storage_path = f"{inv.id}/{file.filename or f'upload.{ext}'}"
            supabase.storage.from_(settings.STORAGE_BUCKET_MEDIA).upload(
                path=storage_path,
                file=content,
                file_options={"content-type": file.content_type},
            )
            return supabase.storage.from_(settings.STORAGE_BUCKET_MEDIA).get_public_url(storage_path)

        storage_url = await asyncio.wait_for(asyncio.to_thread(_do_supabase_upload), timeout=2.0)
    except Exception as e:
        logger.warning(f"Supabase storage upload skipped or timed out (continuing without): {e}")

    # Store content temporarily for pipeline to access
    import tempfile, os
    suffix = f".{(file.filename or 'f').rsplit('.', 1)[-1]}"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(content)
    tmp.close()

    asset = MediaAsset(
        investigation_id=inv.id,
        asset_type=input_type,
        mime_type=file.content_type,
        file_size_bytes=len(content),
        file_hash=file_hash,
        storage_url=storage_url,
        local_path=tmp.name,
        asset_metadata={"filename": file.filename, "original_size": len(content)},
    )
    db.add(asset)

    # CRITICAL: commit NOW so the background task's independent session can see the investigation and media assets.
    await db.commit()

    # Enqueue pipeline — runs immediately via FastAPI BackgroundTasks
    background_tasks.add_task(_run_pipeline_bg, inv.id)

    # Load with relations for response
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.models import Claim

    result = await db.execute(
        select(Investigation)
        .options(
            selectinload(Investigation.claims).selectinload(Claim.evidence),
            selectinload(Investigation.analysis_results),
            selectinload(Investigation.media_assets),
        )
        .where(Investigation.id == inv.id)
    )
    return result.scalar_one()
