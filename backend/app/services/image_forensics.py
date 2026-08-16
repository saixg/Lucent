"""
Single responsibility: Query Sightengine API to evaluate AI-generated image likelihood and digital manipulation signals.
"""

import httpx
from typing import Dict, Any
from app.core.config import settings


async def check_image_forensics(image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
    """
    Query Sightengine API for AI-generation likelihood and image properties.
    Returns:
        {
            "ai_generated_score": float (0.0 to 1.0),
            "is_ai_generated": bool,
            "status": "success" | "unavailable",
            "summary": str
        }
    """
    if not settings.SIGHTENGINE_API_USER or not settings.SIGHTENGINE_API_SECRET:
        return {
            "ai_generated_score": 0.0,
            "is_ai_generated": False,
            "status": "unavailable",
            "summary": "Forensics API credentials not configured.",
        }

    url = "https://api.sightengine.com/1.0/check.json"
    data = {
        "models": "genai",
        "api_user": settings.SIGHTENGINE_API_USER,
        "api_secret": settings.SIGHTENGINE_API_SECRET,
    }
    files = {"media": ("uploaded_image.jpg", image_bytes, mime_type)}

    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            resp = await client.post(url, data=data, files=files)
            if resp.status_code != 200:
                return {
                    "ai_generated_score": 0.0,
                    "is_ai_generated": False,
                    "status": "error",
                    "summary": f"Forensics check returned HTTP {resp.status_code}",
                }

            result = resp.json()
            if result.get("status") == "success":
                ai_score = float(result.get("type", {}).get("ai_generated", 0.0))
                is_ai = ai_score >= 0.70
                return {
                    "ai_generated_score": round(ai_score, 3),
                    "is_ai_generated": is_ai,
                    "status": "success",
                    "summary": (
                        f"AI Generation Probability: {int(ai_score * 100)}% "
                        f"({'High probability of synthetic generation' if is_ai else 'Likely authentic or low synthetic probability'})."
                    ),
                }
    except Exception as e:
        return {
            "ai_generated_score": 0.0,
            "is_ai_generated": False,
            "status": "error",
            "summary": f"Forensics check encountered error: {str(e)[:80]}",
        }

    return {
        "ai_generated_score": 0.0,
        "is_ai_generated": False,
        "status": "unavailable",
        "summary": "No conclusive forensic output.",
    }
