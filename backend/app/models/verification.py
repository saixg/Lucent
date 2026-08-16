"""
Single responsibility: Define SQLAlchemy ORM entities for Verifications, Evidence, and FollowUpMessages per architecture.md §3.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now, index=True)
    
    # Input
    content_type: Mapped[str] = mapped_column(String(32), default="text")  # text | url | image | video | audio
    raw_input_ref: Mapped[str] = mapped_column(Text)
    extracted_claims: Mapped[list] = mapped_column(JSON, default=list)

    # Verdict Contract (prd.md §6)
    verdict_label: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # True | False | Misleading | Missing Context | Altered/Manipulated | AI-Generated | Unverifiable
    confidence_level: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)  # High | Medium | Low
    confidence_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)  # pending | processing | completed | failed

    # Relationships
    evidence_items: Mapped[List["EvidenceItem"]] = relationship(
        "EvidenceItem",
        back_populates="verification",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    follow_up_messages: Mapped[List["FollowUpMessage"]] = relationship(
        "FollowUpMessage",
        back_populates="verification",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class EvidenceItem(Base):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    verification_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("verifications.id", ondelete="CASCADE"), index=True
    )
    
    source_title: Mapped[str] = mapped_column(String(255))
    source_url: Mapped[str] = mapped_column(Text)
    snippet: Mapped[str] = mapped_column(Text)
    relation: Mapped[str] = mapped_column(String(32))  # supports | contradicts | context_only
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    verification: Mapped["Verification"] = relationship("Verification", back_populates="evidence_items")


class FollowUpMessage(Base):
    __tablename__ = "follow_up_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    verification_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("verifications.id", ondelete="CASCADE"), index=True
    )
    
    role: Mapped[str] = mapped_column(String(16))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utc_now)

    verification: Mapped["Verification"] = relationship("Verification", back_populates="follow_up_messages")
