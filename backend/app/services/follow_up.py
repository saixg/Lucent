"""
Single responsibility: Answer user follow-up questions strictly grounded in the stored verification evidence bundle.
"""

from typing import List
from google import genai
from google.genai import types

from app.core.config import settings
from app.models.verification import Verification, FollowUpMessage


async def answer_follow_up(
    verification: Verification,
    new_message: str,
) -> str:
    """
    Generate an answer to a user's follow-up question grounded strictly in the original
    verification's evidence bundle and previous conversation turns.
    """
    evidence_text_list = []
    for idx, ev in enumerate(verification.evidence_items, 1):
        evidence_text_list.append(
            f"[{idx}] {ev.source_title} ({ev.source_url})\n"
            f"Relation: {ev.relation}\n"
            f"Snippet: {ev.snippet}"
        )

    evidence_context = "\n\n".join(evidence_text_list) or "No external evidence sources available."

    history_lines = []
    for msg in verification.follow_up_messages:
        role = "User" if msg.role == "user" else "Lucent"
        history_lines.append(f"{role}: {msg.content}")

    history_context = "\n".join(history_lines)

    system_instruction = (
        "You are Lucent, an independent content verification conversation partner. "
        "The user is asking follow-up questions about a verified claim. "
        "Rules:\n"
        "1. Strictly ground your answer in the provided verification verdict and evidence sources.\n"
        "2. Do NOT invent new facts or cite external sources not present in the evidence list.\n"
        "3. If the user asks something that cannot be answered from the gathered evidence, state clearly: "
        "'This detail was not covered in the original verification evidence and would require a new investigation.'\n"
        "4. Maintain a neutral, direct, evidentiary tone."
    )

    user_prompt = (
        f"Original Claim:\n{verification.raw_input_ref}\n\n"
        f"Verdict: {verification.verdict_label} ({verification.confidence_level} Confidence - {verification.confidence_reason})\n"
        f"Explanation: {verification.explanation}\n\n"
        f"Original Evidence Bundle:\n{evidence_context}\n\n"
        f"Conversation History:\n{history_context}\n\n"
        f"User's Follow-up Question:\n{new_message}"
    )

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
        if response.text:
            return response.text.strip()
    except Exception as e:
        return f"Unable to process follow-up at this moment: {str(e)}"

    return "I could not generate a response based on the stored evidence."
