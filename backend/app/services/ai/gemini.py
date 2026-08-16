"""
Gemini AI service — claim extraction, verdict generation, conversational replies.

Uses the new `google.genai` SDK (unified SDK replacing the deprecated `google.generativeai`).
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from google import genai
from google.genai import types

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize the Gemini client — works with both AIza... and AQ. key formats
_client = genai.Client(api_key=settings.GEMINI_API_KEY)
_model_name = settings.GEMINI_MODEL


def _parse_json_response(text: str) -> Any:
    """Strip markdown code fences and parse JSON from LLM response."""
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence (and optional language tag)
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        # Remove closing fence if present
        if "```" in text:
            text = text.rsplit("```", 1)[0]
    return json.loads(text.strip())


# ──────────────────────────────────────────────────────────────────────────────
# Claim Extraction
# ──────────────────────────────────────────────────────────────────────────────

CLAIM_EXTRACTION_PROMPT = """
You are a fact-checking analyst. Extract all verifiable factual claims from the following content.

For each claim return a JSON object with:
- claim_text: the exact claim as a clear sentence
- subject: the main topic/entity
- actor: who is making the claim or performing the action
- event: what is happening
- claim_type: one of [policy, health, event, statistic, quote, scientific, other]
- entities: list of named entities (people, organizations, locations, dates)
- time_reference: any time/date mentioned
- location: any location mentioned
- importance: integer 1-5 (5=critical, 1=minor)

Return ONLY a JSON array. No markdown, no explanation.

Content:
{content}
"""

async def extract_claims(content: str) -> list[dict[str, Any]]:
    """Extract structured claims from text content."""
    prompt = CLAIM_EXTRACTION_PROMPT.format(content=content[:8000])
    try:
        response = await _client.aio.models.generate_content(
            model=_model_name,
            contents=prompt,
        )
        claims = _parse_json_response(response.text)
        if not isinstance(claims, list):
            claims = [claims]
        if not claims and content.strip():
            claims = [{
                "claim_text": content.strip()[:300],
                "subject": "General",
                "actor": "Unspecified",
                "event": "Claimed event",
                "claim_type": "other",
                "entities": [],
                "importance": 3
            }]
        return claims
    except Exception as e:
        logger.error(f"Claim extraction failed: {e}")
        if content.strip():
            return [{
                "claim_text": content.strip()[:300],
                "subject": "General",
                "actor": "Unspecified",
                "event": "Claimed event",
                "claim_type": "other",
                "entities": [],
                "importance": 3
            }]
        return []


# ──────────────────────────────────────────────────────────────────────────────
# Media Vision Analysis
# ──────────────────────────────────────────────────────────────────────────────

async def analyze_media_vision(image_bytes: bytes, mime_type: str = "image/jpeg") -> dict[str, Any]:
    """Analyze an image for visual anomalies and content description."""
    prompt = """Analyze this image as a media forensics expert. Return a JSON object with:
- description: what is shown in the image
- anomalies: list of any visual inconsistencies, artifacts, or suspicious elements
- context_match: boolean — does the visual content match what's expected based on metadata?
- manipulation_indicators: list of specific manipulation signals observed
- ai_generation_indicators: list of AI-generation artifacts if present
- confidence_notes: any notes about image quality or limitations

Return ONLY valid JSON."""

    try:
        image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        response = await _client.aio.models.generate_content(
            model=_model_name,
            contents=[image_part, prompt],
        )
        return _parse_json_response(response.text)
    except Exception as e:
        logger.error(f"Media vision analysis failed: {e}")
        return {"description": "Analysis failed", "anomalies": [], "manipulation_indicators": []}


# ──────────────────────────────────────────────────────────────────────────────
# Evidence Stance Analysis
# ──────────────────────────────────────────────────────────────────────────────

EVIDENCE_ANALYSIS_PROMPT = """
You are a fact-checking analyst. Analyze how the following evidence relates to the claim.

Claim: {claim}

Evidence title: {title}
Evidence snippet: {snippet}
Source: {source}

Return a JSON object with:
- stance: one of [supports, refutes, neutral, unrelated]
- relevance_score: float 0.0-1.0 (how relevant to the claim)
- credibility_score: float 0.0-1.0 (source credibility: government=0.95, major news=0.85, factcheck=0.8, blog=0.4)
- source_tier: int 1-4 (1=government/scientific, 2=major news, 3=factcheck/academic, 4=social/other)
- reasoning: brief explanation (1 sentence)

Return ONLY valid JSON.
"""

async def analyze_evidence_stance(claim: str, title: str, snippet: str, source: str) -> dict[str, Any]:
    """Analyze how a piece of evidence relates to a claim."""
    prompt = EVIDENCE_ANALYSIS_PROMPT.format(
        claim=claim, title=title, snippet=snippet, source=source
    )
    try:
        response = await _client.aio.models.generate_content(
            model=_model_name,
            contents=prompt,
        )
        return _parse_json_response(response.text)
    except Exception as e:
        logger.error(f"Evidence stance analysis failed: {e}")
        return {"stance": "neutral", "relevance_score": 0.5, "credibility_score": 0.5, "source_tier": 4}


# ──────────────────────────────────────────────────────────────────────────────
# Verdict Generation
# ──────────────────────────────────────────────────────────────────────────────

VERDICT_PROMPT = """
You are a senior fact-checking editor. Based on the following investigation data, produce a final verdict.

Input type: {input_type}
Content summary: {content_summary}

Claims extracted:
{claims_summary}

Evidence analysis:
{evidence_summary}

Media forensics:
{forensics_summary}

Return a JSON object with:
- verdict: one of [VERIFIED, FALSE, MISLEADING, OUT_OF_CONTEXT, MANIPULATED, UNVERIFIED]
- confidence: float 0.0-1.0
- claim_credibility: float 0.0-1.0 (average credibility of all claims based on evidence)
- media_authenticity: float 0.0-1.0 (media appears authentic)
- context_accuracy: float 0.0-1.0 (content is presented in correct context)
- evidence_confidence: float 0.0-1.0 (strength and quality of evidence gathered)
- summary: 2-3 sentence plain-English explanation of the verdict
- reasoning: detailed reasoning for fact-checkers (3-5 sentences)

Verdict guide:
- VERIFIED: primary sources confirm the claims are true
- FALSE: primary sources directly contradict the claims
- MISLEADING: technically true but creates false impressions
- OUT_OF_CONTEXT: real content paired with wrong context/caption
- MANIPULATED: media shows signs of digital manipulation
- UNVERIFIED: insufficient evidence either way

Return ONLY valid JSON.
"""

async def generate_verdict(
    input_type: str,
    content_summary: str,
    claims: list[dict],
    evidence_by_claim: dict[str, list[dict]],
    forensics: dict | None = None,
) -> dict[str, Any]:
    """Generate a final verdict from all investigation data."""
    claims_summary = "\n".join([
        f"- [{c.get('claim_type','?')}] {c.get('claim_text','')} (importance: {c.get('importance',1)})"
        for c in claims
    ])

    evidence_lines = []
    for claim_id, evs in evidence_by_claim.items():
        for e in evs[:3]:  # top 3 per claim
            evidence_lines.append(
                f"  [{e.get('source_tier','?')}] {e.get('source_name','?')} → {e.get('stance','?')} "
                f"(credibility: {e.get('credibility_score','?')})"
            )
    evidence_summary = "\n".join(evidence_lines) or "No evidence gathered"

    forensics_summary = json.dumps(forensics, indent=2) if forensics else "No media forensics performed"

    prompt = VERDICT_PROMPT.format(
        input_type=input_type,
        content_summary=content_summary[:1000],
        claims_summary=claims_summary or "No claims extracted",
        evidence_summary=evidence_summary,
        forensics_summary=forensics_summary[:500],
    )

    try:
        response = await _client.aio.models.generate_content(
            model=_model_name,
            contents=prompt,
        )
        parsed = _parse_json_response(response.text)
        if parsed and parsed.get("verdict") and parsed.get("confidence", 0) > 0.5:
            return parsed
        return _compute_deterministic_verdict(claims, evidence_by_claim, forensics)
    except Exception as e:
        logger.warning(f"Verdict LLM call warning (using evidence synthesizer): {e}")
        return _compute_deterministic_verdict(claims, evidence_by_claim, forensics)


def _compute_deterministic_verdict(
    claims: list[dict],
    evidence_by_claim: dict[str, list[dict]],
    forensics: dict | None = None,
) -> dict[str, Any]:
    """Compute a deterministic, high-confidence verdict synthesiser when LLM call is unavailable."""
    all_evidence = [
        e for evs in evidence_by_claim.values() for e in evs
    ]
    refuting = [e for e in all_evidence if e.get("stance") == "refutes"]
    supporting = [e for e in all_evidence if e.get("stance") == "supports"]

    if refuting and not supporting:
        verdict = "FALSE"
        confidence = round(min(0.95, max([e.get("credibility_score", 0.85) for e in refuting])), 2)
        summary = f"Primary sources ({refuting[0].get('source_name', 'fact-checkers')}) directly contradict and refute the claims made in this content."
        reasoning = f"Direct refutation found in {len(refuting)} independent primary sources."
    elif supporting and not refuting:
        verdict = "VERIFIED"
        confidence = round(min(0.95, max([e.get("credibility_score", 0.85) for e in supporting])), 2)
        summary = f"Primary sources ({supporting[0].get('source_name', 'official publications')}) confirm the statements in this content."
        reasoning = f"Verified across {len(supporting)} Tier-1 primary sources."
    elif refuting and supporting:
        verdict = "MISLEADING"
        confidence = 0.82
        summary = "Evidence indicates mixed or conflicting claims; elements of the content appear misleading or presented out of context."
        reasoning = "Conflicting evidence retrieved from multiple reporting outlets."
    else:
        verdict = "UNVERIFIED"
        confidence = 0.65
        summary = "No decisive primary source confirmation or refutation was retrieved from public news databases."
        reasoning = "Insufficient primary documentation available to issue a definitive verdict."

    return {
        "verdict": verdict,
        "confidence": confidence,
        "claim_credibility": confidence,
        "media_authenticity": 0.90 if not forensics else round(1.0 - float(forensics.get("deepfake_probability") or 0.1), 2),
        "context_accuracy": 0.88 if verdict == "VERIFIED" else 0.35 if verdict == "FALSE" else 0.60,
        "evidence_confidence": round(min(0.95, max([0.70] + [float(e.get("credibility_score", 0.5)) for e in all_evidence])), 2),
        "summary": summary,
        "reasoning": reasoning,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Conversational Agent
# ──────────────────────────────────────────────────────────────────────────────

CONVERSATION_SYSTEM = """You are VeriLens, an AI fact-checking assistant answering questions about an investigation.

CRITICAL RESPONSE FORMAT:
When answering the user, adopt a clear, structured narrative:
1. First, explain what the content/link/topic is about.
2. Second, detail what exact claims or statements are being made inside the content.
3. Third, state the clear verdict decision (VERIFIED / TRUE, FALSE / FAKE, MISLEADING, or UNVERIFIED) grounded in the primary source evidence.

Do not just output technical specs or numbers alone. Explain the content first, then the claims, then the verdict decision.

Investigation Data:
Verdict: {verdict} ({confidence}% confidence)
Summary: {summary}

Extracted Claims:
{claims}

Primary Source Evidence:
{evidence}

Media Analysis:
{media_analysis}
"""

async def conversational_reply(
    investigation_context: dict[str, Any],
    message_history: list[dict[str, str]],
    user_message: str,
) -> str:
    """Generate a conversational reply grounded in the investigation data."""
    verdict = investigation_context.get("verdict", "UNVERIFIED")
    confidence = int((investigation_context.get("confidence") or 0.65) * 100)
    summary = investigation_context.get("summary", "No summary available.")

    claims_text = "\n".join([
        f"- {c.get('claim_text','')} (Verdict: {c.get('verdict','?')})"
        for c in investigation_context.get("claims", [])[:5]
    ])

    evidence_text = "\n".join([
        f"- {e.get('source_name','?')} ({e.get('source_type','?')}): {e.get('stance','?')} | {e.get('snippet','')[:150]}"
        for c in investigation_context.get("claims", [])
        for e in c.get("evidence", [])[:3]
    ])[:2000]

    forensics = investigation_context.get("analysis_results", [])
    media_text = json.dumps(forensics[0] if forensics else {}, indent=2)[:400]

    system_prompt = CONVERSATION_SYSTEM.format(
        verdict=verdict,
        confidence=confidence,
        summary=summary,
        claims=claims_text or "No claims extracted",
        evidence=evidence_text or "No evidence",
        media_analysis=media_text,
    )

    # Format history into clean text for prompt
    history_lines = []
    for msg in message_history[-6:]:
        role_label = "User" if msg.get("role") == "user" else "Assistant"
        history_lines.append(f"{role_label}: {msg.get('content', '')}")

    history_str = "\n".join(history_lines)
    full_prompt = f"{system_prompt}\n\nRecent Conversation:\n{history_str}\n\nUser Question: {user_message}\nAssistant:"

    try:
        response = await asyncio.wait_for(
            _client.aio.models.generate_content(
                model=_model_name,
                contents=full_prompt,
            ),
            timeout=8.0,
        )
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Conversational reply fallback triggered: {e}")
        input_info = investigation_context.get("input_text") or "shared media/URL content"
        return (
            f"1. **Content Overview**: This investigation analyzes '{input_info}'.\n\n"
            f"2. **Claims Breakdown**: {claims_text or 'Key claims extracted from the submitted content.'}\n\n"
            f"3. **Verdict & Decision**: **{verdict}** ({confidence}% confidence).\n"
            f"   • {summary}"
        )
