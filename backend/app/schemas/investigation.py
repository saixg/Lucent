"""
Pydantic schemas for Investigation endpoints.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, AnyHttpUrl, field_validator, model_validator


# ──────────────────────────────────────────────────────────────────────────────
# Input schemas
# ──────────────────────────────────────────────────────────────────────────────

class InvestigationCreate(BaseModel):
    input_type: str  # youtube_url | x_url | ig_url | image | video | audio | text | screenshot
    input_url: Optional[str] = None
    input_text: Optional[str] = None
    platform: Optional[str] = None
    user_id: Optional[str] = None

    @model_validator(mode="after")
    def require_url_or_text(self) -> "InvestigationCreate":
        if not self.input_url and not self.input_text:
            raise ValueError("Either input_url or input_text is required")
        return self


# ──────────────────────────────────────────────────────────────────────────────
# Nested output schemas
# ──────────────────────────────────────────────────────────────────────────────

class EvidenceOut(BaseModel):
    id: str
    source_url: str
    source_name: Optional[str] = None
    source_type: str
    source_tier: int
    stance: Optional[str] = None
    relevance_score: Optional[float] = None
    credibility_score: Optional[float] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ClaimOut(BaseModel):
    id: str
    claim_text: str
    subject: Optional[str] = None
    actor: Optional[str] = None
    event: Optional[str] = None
    claim_type: Optional[str] = None
    entities: Optional[list[str]] = None
    time_reference: Optional[str] = None
    location: Optional[str] = None
    importance: int = 1
    verdict: Optional[str] = None
    verdict_confidence: Optional[float] = None
    evidence: list[EvidenceOut] = []

    model_config = {"from_attributes": True}


class AnalysisResultOut(BaseModel):
    id: str
    media_authenticity: Optional[float] = None
    ai_generation_probability: Optional[float] = None
    manipulation_probability: Optional[float] = None
    deepfake_probability: Optional[float] = None
    voice_clone_probability: Optional[float] = None
    context_match: Optional[bool] = None
    provenance_status: Optional[str] = None
    original_source_url: Optional[str] = None
    original_date: Optional[datetime] = None
    original_caption: Optional[str] = None
    provenance_timeline: Optional[list[dict]] = None
    reasoning: Optional[str] = None

    model_config = {"from_attributes": True}


class MediaAssetOut(BaseModel):
    id: str
    asset_type: str
    storage_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    mime_type: Optional[str] = None
    asset_metadata: Optional[dict[str, Any]] = None

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────────────────────────────────────
# Full Investigation output
# ──────────────────────────────────────────────────────────────────────────────

class InvestigationOut(BaseModel):
    id: str
    input_type: str
    input_url: Optional[str] = None
    input_text: Optional[str] = None
    platform: Optional[str] = None
    status: str
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    claim_credibility: Optional[float] = None
    media_authenticity: Optional[float] = None
    context_accuracy: Optional[float] = None
    evidence_confidence: Optional[float] = None
    summary: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    claims: list[ClaimOut] = []
    analysis_results: list[AnalysisResultOut] = []
    media_assets: list[MediaAssetOut] = []

    model_config = {"from_attributes": True}


class InvestigationListOut(BaseModel):
    id: str
    input_type: str
    input_url: Optional[str] = None
    status: str
    verdict: Optional[str] = None
    confidence: Optional[float] = None
    summary: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
