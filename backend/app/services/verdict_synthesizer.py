"""
Single responsibility: Synthesize evidence into the strict 6-part verdict contract (prd.md §6) with code-enforced Unverifiable guards (rules.md §2).
"""

import json
import re
import asyncio
from typing import List, Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings
from app.schemas.verdict import (
    ConfidenceLevel,
    EvidenceItemSchema,
    RelationType,
    VerdictContract,
    VerdictLabel,
)


class SynthesizedEvidenceMapping(BaseModel):
    source_url: str
    relation: str = Field(
        ...,
        description="Whether this source 'supports', 'contradicts', or provides 'context_only' for the claim",
    )


class LLMVerdictOutput(BaseModel):
    claim_summary: str = Field(
        ...,
        description="What is actually being claimed or shown",
    )
    verdict_label: str = Field(
        ...,
        description="One of: True, False, Misleading, Missing Context, Altered/Manipulated, AI-Generated, Unverifiable",
    )
    confidence_level: str = Field(
        ...,
        description="High, Medium, or Low",
    )
    confidence_reason: str = Field(
        ...,
        description="One-line reasoning for the confidence level itself",
    )
    explanation: str = Field(
        ...,
        description="Plain-language explanation of what is actually true based solely on the evidence provided.",
    )
    evidence_relations: List[SynthesizedEvidenceMapping] = Field(
        default_factory=list,
        description="Mapping of each retrieved source URL to its relationship with the claim (supports/contradicts/context_only)",
    )


def extract_json_payload(raw_text: str) -> dict:
    """Safely extract JSON dict from raw LLM output, stripping markdown fences if present."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        text = match.group(1)

    return json.loads(text)


def normalize_verdict_label(label: str) -> VerdictLabel:
    cleaned = label.strip().lower()
    if "ai" in cleaned or "synthetic" in cleaned or "generated" in cleaned:
        return VerdictLabel.AI_GENERATED
    if "alter" in cleaned or "manipulat" in cleaned or "deepfake" in cleaned:
        return VerdictLabel.ALTERED_MANIPULATED
    if "miss" in cleaned or "context" in cleaned:
        return VerdictLabel.MISSING_CONTEXT
    if "mislead" in cleaned:
        return VerdictLabel.MISLEADING
    if "false" in cleaned or "fake" in cleaned or "debunk" in cleaned:
        return VerdictLabel.FALSE
    if "true" in cleaned or "correct" in cleaned or "accurate" in cleaned:
        return VerdictLabel.TRUE
    return VerdictLabel.UNVERIFIABLE


def normalize_confidence_level(level: str) -> ConfidenceLevel:
    cleaned = level.strip().capitalize()
    if cleaned in ["High", "Medium", "Low"]:
        return ConfidenceLevel(cleaned)
    return ConfidenceLevel.LOW


def normalize_relation_type(rel: str) -> RelationType:
    cleaned = rel.strip().lower()
    if "support" in cleaned or "confirm" in cleaned:
        return RelationType.SUPPORTS
    if "contradict" in cleaned or "refute" in cleaned or "debunk" in cleaned or "false" in cleaned:
        return RelationType.CONTRADICTS
    return RelationType.CONTEXT_ONLY


async def synthesize_verdict(
    raw_input: str,
    extracted_claims: List[str],
    evidence_items: List[Dict[str, str]],
) -> VerdictContract:
    """
    Synthesize a structured 6-part verdict contract from the extracted claims and gathered evidence.
    Enforces rules.md §2: If evidence is empty, automatically returns Unverifiable.
    """
    # ─── Hard Code Guard 1: Empty Evidence ────────────────────────────────────
    if not evidence_items:
        return VerdictContract(
            claim_summary=extracted_claims[0] if extracted_claims else raw_input[:200],
            verdict_label=VerdictLabel.UNVERIFIABLE,
            confidence_level=ConfidenceLevel.LOW,
            confidence_reason="Low — No authoritative public records, primary reporting, or fact-check database entries were found for this claim.",
            explanation="Lucent searched available news indexes and fact-checking databases but found no decisive public evidence supporting or refuting this specific claim. Per verification integrity rules, this claim is classified as Unverifiable.",
            evidence=[],
        )

    # ─── Context Formatting ───────────────────────────────────────────────────
    evidence_context = []
    for idx, item in enumerate(evidence_items, 1):
        evidence_context.append(
            f"[{idx}] Title: {item.get('source_title', 'Untitled')}\n"
            f"URL: {item.get('source_url', '')}\n"
            f"Snippet: {item.get('snippet', '')}\n"
        )

    claims_text = "\n".join(f"- {c}" for c in extracted_claims) or raw_input

    system_instruction = (
        "You are Lucent, an independent content verification engine. "
        "Your mission is to evaluate factual claims strictly against the provided evidence snippets.\n"
        "Rules:\n"
        "1. Never fabricate sources or facts outside the provided snippets.\n"
        "2. Neutral, evidentiary tone only — evaluate factual claims, never editorialize about opinions.\n"
        "3. Verdict Label must be exactly one of: True, False, Misleading, Missing Context, Altered/Manipulated, AI-Generated, Unverifiable.\n"
        "4. If the evidence is ambiguous or insufficient to prove or disprove the claim, select Unverifiable.\n"
        "5. Give a concise one-line reason for your confidence rating.\n"
        "6. Provide a clear, accessible plain-language explanation of what is actually true.\n\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "claim_summary": "string",\n'
        '  "verdict_label": "True" | "False" | "Misleading" | "Missing Context" | "Altered/Manipulated" | "AI-Generated" | "Unverifiable",\n'
        '  "confidence_level": "High" | "Medium" | "Low",\n'
        '  "confidence_reason": "string",\n'
        '  "explanation": "string",\n'
        '  "evidence_relations": [{"source_url": "string", "relation": "supports" | "contradicts" | "context_only"}]\n'
        "}"
    )

    user_prompt = (
        f"Input Claim / Content:\n{raw_input}\n\n"
        f"Extracted Checkable Claims:\n{claims_text}\n\n"
        f"Retrieved Evidence Sources:\n\n" + "\n---\n".join(evidence_context)
    )

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    for attempt in range(2):
        try:
            response = await client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            if response.text:
                parsed = extract_json_payload(response.text)
                llm_output = LLMVerdictOutput(**parsed)

                # Normalize labels safely
                final_label = normalize_verdict_label(llm_output.verdict_label)
                final_conf = normalize_confidence_level(llm_output.confidence_level)

                # Map LLM relation outputs back to the validated retrieved evidence items
                url_to_relation = {
                    m.source_url: normalize_relation_type(m.relation)
                    for m in llm_output.evidence_relations
                }

                final_evidence_items: List[EvidenceItemSchema] = []
                for item in evidence_items:
                    rel = url_to_relation.get(item.get("source_url", ""), RelationType.CONTEXT_ONLY)
                    final_evidence_items.append(
                        EvidenceItemSchema(
                            source_title=item.get("source_title", "Evidence Source"),
                            source_url=item.get("source_url", ""),
                            snippet=item.get("snippet", ""),
                            relation=rel,
                        )
                    )

                # ─── Hard Code Guard 2: No evidence attached -> Force Unverifiable ──
                if not final_evidence_items:
                    return VerdictContract(
                        claim_summary=llm_output.claim_summary,
                        verdict_label=VerdictLabel.UNVERIFIABLE,
                        confidence_level=ConfidenceLevel.LOW,
                        confidence_reason="Low — No verifiable external sources attached.",
                        explanation=llm_output.explanation,
                        evidence=[],
                    )

                return VerdictContract(
                    claim_summary=llm_output.claim_summary,
                    verdict_label=final_label,
                    confidence_level=final_conf,
                    confidence_reason=llm_output.confidence_reason,
                    explanation=llm_output.explanation,
                    evidence=final_evidence_items,
                )
        except Exception:
            if attempt == 0:
                await asyncio.sleep(1.0)
            continue

    return VerdictContract(
        claim_summary=extracted_claims[0] if extracted_claims else raw_input[:200],
        verdict_label=VerdictLabel.UNVERIFIABLE,
        confidence_level=ConfidenceLevel.LOW,
        confidence_reason="Low — Automated synthesis encountered an error while analyzing evidence sources.",
        explanation="The evidence could not be decisively verified at this moment. Please review the attached source links.",
        evidence=[
            EvidenceItemSchema(
                source_title=item.get("source_title", "Evidence Source"),
                source_url=item.get("source_url", ""),
                snippet=item.get("snippet", ""),
                relation=RelationType.CONTEXT_ONLY,
            )
            for item in evidence_items[:3]
        ],
    )
