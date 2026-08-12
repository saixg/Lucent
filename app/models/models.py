"""
SQLAlchemy ORM models — mirrors the DB schema defined in plan.md.
All tables use UUID primary keys and timestamptz created_at.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _uuid() -> str:
    return str(uuid.uuid4())


# ──────────────────────────────────────────────────────────────────────────────
# investigations
# ──────────────────────────────────────────────────────────────────────────────

class Investigation(Base):
    __tablename__ = "investigations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=_uuid
    )
    user_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    # Input
    input_type: Mapped[str] = mapped_column(
        String(32)
    )  # youtube_url | x_url | ig_url | image | video | audio | text | screenshot
    input_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    platform: Mapped[str | None] = mapped_column(String(32), nullable=True)  # youtube | x | instagram | web

    # Status
    status: Mapped[str] = mapped_column(
        String(32), default="pending"
    )  # pending | processing | complete | failed

    # Verdict
    verdict: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # VERIFIED | FALSE | MISLEADING | OUT_OF_CONTEXT | MANIPULATED | UNVERIFIED
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Scores
    claim_credibility: Mapped[float | None] = mapped_column(Float, nullable=True)
    media_authenticity: Mapped[float | None] = mapped_column(Float, nullable=True)
    context_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    evidence_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    media_assets: Mapped[list["MediaAsset"]] = relationship(back_populates="investigation")
    claims: Mapped[list["Claim"]] = relationship(back_populates="investigation")
    analysis_results: Mapped[list["AnalysisResult"]] = relationship(back_populates="investigation")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="investigation")


# ──────────────────────────────────────────────────────────────────────────────
# media_assets
# ──────────────────────────────────────────────────────────────────────────────

class MediaAsset(Base):
    __tablename__ = "media_assets"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    investigation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("investigations.id", ondelete="CASCADE"), index=True
    )

    asset_type: Mapped[str] = mapped_column(
        String(32)
    )  # video | audio | image | frame | transcript | screenshot

    storage_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    local_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # SHA-256
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)

    asset_metadata: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    investigation: Mapped["Investigation"] = relationship(back_populates="media_assets")


# ──────────────────────────────────────────────────────────────────────────────
# claims
# ──────────────────────────────────────────────────────────────────────────────

class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    investigation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("investigations.id", ondelete="CASCADE"), index=True
    )

    claim_text: Mapped[str] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor: Mapped[str | None] = mapped_column(Text, nullable=True)
    event: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_type: Mapped[str | None] = mapped_column(String(64), nullable=True)  # policy | health | event | statistic | quote

    entities: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    time_reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    importance: Mapped[int] = mapped_column(Integer, default=1)  # 1 (low) – 5 (critical)

    # Per-claim verdict
    verdict: Mapped[str | None] = mapped_column(String(32), nullable=True)
    verdict_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="claim")
    investigation: Mapped["Investigation"] = relationship(back_populates="claims")


# ──────────────────────────────────────────────────────────────────────────────
# evidence
# ──────────────────────────────────────────────────────────────────────────────

class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    claim_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("claims.id", ondelete="CASCADE"), index=True
    )

    source_url: Mapped[str] = mapped_column(Text)
    source_name: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source_type: Mapped[str] = mapped_column(
        String(32)
    )  # government | regulator | science | news | factcheck | social | other

    source_tier: Mapped[int] = mapped_column(Integer, default=4)  # 1 (primary) – 4 (low-authority)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stance: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # supports | refutes | neutral | unrelated

    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    credibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)

    claim: Mapped["Claim"] = relationship(back_populates="evidence")


# ──────────────────────────────────────────────────────────────────────────────
# analysis_results  (media forensics output)
# ──────────────────────────────────────────────────────────────────────────────

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    investigation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("investigations.id", ondelete="CASCADE"), index=True
    )

    # Media authenticity signals (0.0 – 1.0, higher = more likely authentic / detected)
    media_authenticity: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_generation_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    manipulation_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    deepfake_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    voice_clone_probability: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Context engine output
    context_match: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    provenance_status: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # original | edited | reposted | unknown

    original_source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    original_location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    original_caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timeline of reposts/edits (JSON array of {date, url, change_description})
    provenance_timeline: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)

    # Manipulation heatmap data (JSON — frame → region → score)
    manipulation_regions: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Raw reasoning from LLM
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Full raw output from forensics APIs
    raw_forensics: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    investigation: Mapped["Investigation"] = relationship(back_populates="analysis_results")


# ──────────────────────────────────────────────────────────────────────────────
# conversations
# ──────────────────────────────────────────────────────────────────────────────

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    investigation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("investigations.id", ondelete="CASCADE"), index=True
    )

    platform: Mapped[str] = mapped_column(
        String(32), default="web"
    )  # web | youtube | x | instagram

    platform_user_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    platform_thread_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")
    investigation: Mapped["Investigation"] = relationship(back_populates="conversations")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )

    role: Mapped[str] = mapped_column(String(16))  # user | assistant | system
    content: Mapped[str] = mapped_column(Text)

    # Optional: attach referenced evidence IDs
    cited_evidence_ids: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
