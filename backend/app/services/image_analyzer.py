"""
Single responsibility: Analyze visual content, OCR text, and visual claims using Gemini multimodal vision.
"""

import asyncio
import json
import re
from typing import List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import settings


class ImageAnalysisOutput(BaseModel):
    scene_description: str = Field(..., description="Objective description of what is depicted in the image")
    visible_text: str = Field("", description="Any text, meme captions, or headlines visible in the image")
    extracted_claims: List[str] = Field(
        default_factory=list,
        description="List of 1 to 3 core checkable factual claims made by or associated with this image",
    )
    visual_anomalies: str = Field(
        "",
        description="Any noticeable visual artifacts, unnatural hands/features, or editing anomalies",
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

    # Match inner JSON object if surrounded by extra text
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        text = match.group(1)

    return json.loads(text)


async def analyze_image_with_vision(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> ImageAnalysisOutput:
    """
    Analyze image using Gemini multimodal vision to extract claims and scene details.
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)

    prompt = (
        "You are the visual ingestion module for Lucent verification engine.\n"
        "Examine this image carefully.\n"
        "Return ONLY a valid JSON object matching this schema:\n"
        "{\n"
        '  "scene_description": "Objective description of what is depicted in the image",\n'
        '  "visible_text": "Any text, meme captions, or headlines visible in the image",\n'
        '  "extracted_claims": ["1 to 3 atomic checkable factual claims extracted from the image and text"],\n'
        '  "visual_anomalies": "Any noticeable visual artifacts, AI distortions, or editing anomalies"\n'
        "}"
    )

    for attempt in range(2):
        try:
            response = await client.aio.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )

            if response.text:
                data = extract_json_payload(response.text)
                return ImageAnalysisOutput(**data)
        except Exception:
            if attempt == 0:
                await asyncio.sleep(1.0)
            continue

    return ImageAnalysisOutput(
        scene_description="Image provided for verification.",
        visible_text="",
        extracted_claims=["Visual claim depicted in uploaded image."],
        visual_anomalies="",
    )
