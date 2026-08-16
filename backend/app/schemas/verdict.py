"""
Single responsibility: Define Pydantic models for the 6-part verdict contract and verification request/response schemas.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class VerdictLabel(str, Enum):
    TRUE = "True"
    FALSE = "False"
    MISLEADING = "Misleading"
    MISSING_CONTEXT = "Missing Context"
    ALTERED_MANIPULATED = "Altered/Manipulated"
    AI_GENERATED = "AI-Generated"
    UNVERIFIABLE = "Unverifiable"


class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RelationType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXT_ONLY = "context_only"


class EvidenceItemSchema(BaseModel):
    id: Optional[str] = None
    source_title: str
    source_url: str
    snippet: str
    relation: RelationType = RelationType.CONTEXT_ONLY


class FollowUpMessageSchema(BaseModel):
    id: Optional[str] = None
    role: str  # user | assistant
    content: str
    created_at: Optional[datetime] = None


class VerificationCreateRequest(BaseModel):
    content: str = Field(..., min_length=1, description="Text claim or URL to verify")
    content_type: str = Field(default="text", description="text | url | image | video | audio")


class VerdictContract(BaseModel):
    claim_summary: str = Field(..., description="What is actually being claimed or shown")
    verdict_label: VerdictLabel = Field(..., description="The classification verdict")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level in verdict")
    confidence_reason: str = Field(..., description="One-line reasoning for confidence level")
    explanation: str = Field(..., description="Plain-language explanation of what is actually true")
    evidence: List[EvidenceItemSchema] = Field(default_factory=list, description="List of cited evidence sources")


class VerificationResponse(BaseModel):
    id: str
    created_at: datetime
    content_type: str
    raw_input_ref: str
    extracted_claims: List[str] = Field(default_factory=list)
    verdict_label: Optional[VerdictLabel] = None
    confidence_level: Optional[ConfidenceLevel] = None
    confidence_reason: Optional[str] = None
    explanation: Optional[str] = None
    status: str
    evidence_items: List[EvidenceItemSchema] = Field(default_factory=list)
    follow_up_messages: List[FollowUpMessageSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class FollowUpRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Follow-up question about the verification")
