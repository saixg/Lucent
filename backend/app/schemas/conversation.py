"""
Pydantic schemas for Conversation and Message endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ConversationCreate(BaseModel):
    investigation_id: str
    platform: str = "web"
    platform_user_id: Optional[str] = None


class ConversationOut(BaseModel):
    id: str
    investigation_id: str
    platform: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    cited_evidence_ids: Optional[list[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
