from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.models import Conversation, Message, Investigation, Claim, Evidence, AnalysisResult
from app.schemas.conversation import ConversationCreate, ConversationOut, MessageCreate, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


async def _load_investigation_context(investigation_id: str, db: AsyncSession) -> dict:
    """Load full investigation context for the conversational agent."""
    result = await db.execute(
        select(Investigation)
        .options(
            selectinload(Investigation.claims).selectinload(Claim.evidence),
            selectinload(Investigation.analysis_results),
        )
        .where(Investigation.id == investigation_id)
    )
    inv = result.scalar_one_or_none()
    if not inv:
        return {}

    return {
        "input_text": inv.input_text,
        "input_type": inv.input_type,
        "verdict": inv.verdict or "UNVERIFIED",
        "confidence": inv.confidence or 0.65,
        "summary": inv.summary or (f"Investigation into content topic: '{inv.input_text}'." if inv.input_text else "Media/URL content investigation."),
        "claims": [
            {
                "claim_text": c.claim_text,
                "verdict": c.verdict,
                "evidence": [
                    {
                        "source_name": e.source_name,
                        "source_type": e.source_type,
                        "stance": e.stance,
                        "snippet": e.snippet,
                        "credibility_score": e.credibility_score,
                    }
                    for e in c.evidence
                ],
            }
            for c in inv.claims
        ],
        "analysis_results": [
            {
                "media_authenticity": a.media_authenticity,
                "ai_generation_probability": a.ai_generation_probability,
                "manipulation_probability": a.manipulation_probability,
                "provenance_status": a.provenance_status,
            }
            for a in inv.analysis_results
        ],
    }


@router.post("/", response_model=ConversationOut, status_code=201)
async def create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a conversation linked to an investigation."""
    inv = (await db.execute(
        select(Investigation).where(Investigation.id == payload.investigation_id)
    )).scalar_one_or_none()
    if not inv:
        raise HTTPException(404, "Investigation not found")

    convo = Conversation(
        investigation_id=payload.investigation_id,
        platform=payload.platform,
        platform_user_id=payload.platform_user_id,
    )
    db.add(convo)
    await db.flush()
    return convo


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return all messages in a conversation."""
    convo = (await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )).scalar_one_or_none()
    if not convo:
        raise HTTPException(404, "Conversation not found")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return result.scalars().all()


@router.post("/{conversation_id}/messages", response_model=MessageOut)
async def send_message(
    conversation_id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Send a message and receive a Gemini-powered reply."""
    convo = (await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )).scalar_one_or_none()
    if not convo:
        raise HTTPException(404, "Conversation not found")

    # Save user message
    user_msg = Message(
        conversation_id=conversation_id,
        role="user",
        content=payload.content,
    )
    db.add(user_msg)
    await db.flush()

    # Load message history for context
    history_result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(20)
    )
    history = [
        {"role": m.role, "content": m.content}
        for m in history_result.scalars().all()
    ]

    # Load investigation context
    inv_context = await _load_investigation_context(convo.investigation_id, db)

    # Generate Gemini reply
    try:
        from app.services.ai.gemini import conversational_reply
        reply_text = await conversational_reply(
            investigation_context=inv_context,
            message_history=history,
            user_message=payload.content,
        )
    except Exception as e:
        reply_text = f"I'm having trouble responding right now. Error: {str(e)[:100]}"

    assistant_msg = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply_text,
    )
    db.add(assistant_msg)
    await db.flush()
    return assistant_msg
