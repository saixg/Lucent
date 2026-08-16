"""
Serper (Google Search API) evidence retrieval service.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

SERPER_URL = "https://google.serper.dev/search"


async def search(query: str, num: int = 8) -> list[dict[str, Any]]:
    """Search Google via Serper API. Returns list of result dicts."""
    if not settings.SERPER_API_KEY:
        logger.warning("SERPER_API_KEY not set, skipping Serper search")
        return []

    headers = {
        "X-API-KEY": settings.SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": num, "gl": "in", "hl": "en"}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(SERPER_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source_name": _extract_domain(item.get("link", "")),
                "published_at": item.get("date"),
            })
        return results

    except Exception as e:
        logger.error(f"Serper search failed for '{query}': {e}")
        return []


def _extract_domain(url: str) -> str:
    """Extract clean domain name from URL."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.replace("www.", "")
        return domain
    except Exception:
        return url[:50]
