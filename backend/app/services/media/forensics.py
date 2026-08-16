"""
Media forensics — calls Sightengine and Hive APIs for deepfake/AI detection.
Degrades gracefully if API keys are not set.
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ForensicsResult:
    ai_generation_probability: float = 0.0
    manipulation_probability: float = 0.0
    deepfake_probability: float = 0.0
    voice_clone_probability: float = 0.0
    media_authenticity: float = 1.0
    raw: dict[str, Any] = field(default_factory=dict)


async def analyze_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> ForensicsResult:
    """Analyze an image with Sightengine and/or Hive APIs."""
    results: list[dict] = []

    tasks = []
    if settings.SIGHTENGINE_API_USER and settings.SIGHTENGINE_API_SECRET:
        tasks.append(_sightengine_image(image_bytes, mime_type))
    if settings.HIVE_API_KEY:
        tasks.append(_hive_image(image_bytes, mime_type))

    if not tasks:
        logger.warning("No media forensics API keys configured — skipping forensics")
        return ForensicsResult()

    raw_results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in raw_results:
        if isinstance(r, dict):
            results.append(r)

    return _merge_image_results(results)


async def _sightengine_image(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    """Call Sightengine API for AI-generation and manipulation detection."""
    try:
        ext = mime_type.split("/")[-1] if "/" in mime_type else "jpg"
        files = {"media": (f"image.{ext}", image_bytes, mime_type)}
        data = {
            "models": "genai,deepfake,faces,nudity-2.0",
            "api_user": settings.SIGHTENGINE_API_USER,
            "api_secret": settings.SIGHTENGINE_API_SECRET,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.sightengine.com/1.0/check.json",
                files=files,
                data=data,
            )
            resp.raise_for_status()
            return {"source": "sightengine", "data": resp.json()}
    except Exception as e:
        logger.error(f"Sightengine API failed: {e}")
        return {}


async def _hive_image(image_bytes: bytes, mime_type: str) -> dict[str, Any]:
    """Call Hive Moderation API for AI-generated content detection."""
    try:
        ext = mime_type.split("/")[-1] if "/" in mime_type else "jpg"
        files = {"media": (f"image.{ext}", image_bytes, mime_type)}
        headers = {"Authorization": f"Token {settings.HIVE_API_KEY}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.thehive.ai/api/v2/task/sync",
                headers=headers,
                files=files,
            )
            resp.raise_for_status()
            return {"source": "hive", "data": resp.json()}
    except Exception as e:
        logger.error(f"Hive API failed: {e}")
        return {}


def _merge_image_results(results: list[dict]) -> ForensicsResult:
    """Merge results from multiple forensics APIs into a single score."""
    ai_prob = 0.0
    manip_prob = 0.0
    deepfake_prob = 0.0
    count = 0
    raw_all: dict[str, Any] = {}

    for r in results:
        source = r.get("source", "unknown")
        data = r.get("data", {})
        raw_all[source] = data

        if source == "sightengine":
            genai_data = data.get("type", {}).get("ai_generated", 0.0)
            ai_prob += float(genai_data)
            deepfake_data = data.get("faces", {})
            if isinstance(deepfake_data, dict):
                deepfake_prob += float(deepfake_data.get("deepfake", {}).get("score", 0.0))
            count += 1

        elif source == "hive":
            outputs = data.get("status", {}).get("response", {}).get("output", [])
            for output in outputs:
                for cls in output.get("classes", []):
                    if cls.get("class") == "ai_generated":
                        ai_prob += float(cls.get("score", 0.0))
                        count += 1
                        break

    if count > 0:
        ai_prob /= count
        deepfake_prob /= max(count, 1)

    # Media authenticity is inverse of manipulation signals
    media_authenticity = 1.0 - max(ai_prob, deepfake_prob, manip_prob)
    media_authenticity = max(0.0, min(1.0, media_authenticity))

    return ForensicsResult(
        ai_generation_probability=round(ai_prob, 3),
        manipulation_probability=round(manip_prob, 3),
        deepfake_probability=round(deepfake_prob, 3),
        media_authenticity=round(media_authenticity, 3),
        raw=raw_all,
    )
