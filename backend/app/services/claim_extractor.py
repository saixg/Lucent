"""
Single responsibility: Extract atomic, checkable factual claims from raw user text or scraped article text using Google Gemini.
"""

import json
from typing import List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings


class ExtractedClaimsList(BaseModel):
    claims: List[str] = Field(
        ...,
        description="List of distinct, checkable factual claims extracted from the content. Max 3 concise claims.",
    )


async def extract_claims(raw_text: str) -> List[str]:
    """
    Extract checkable factual claims from the input text using async Gemini structured output.
    Falls back gracefully to returning the raw text if extraction fails.
    """
    cleaned_input = raw_text.strip()
    if not cleaned_input:
        return []

    # If the input is already a short single-sentence claim, return it directly
    if len(cleaned_input) < 120 and "\n" not in cleaned_input:
        return [cleaned_input]

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        prompt = (
            "Analyze the following text/article content. Extract the core atomic factual claims "
            "that can be fact-checked or verified against external evidence.\n\n"
            f"Content:\n{cleaned_input[:4000]}"
        )

        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedClaimsList,
                temperature=0.1,
            ),
        )

        if response.text:
            data = json.loads(response.text)
            claims = data.get("claims", [])
            if claims:
                return claims[:3]
    except Exception:
        pass

    return [cleaned_input[:300]]
