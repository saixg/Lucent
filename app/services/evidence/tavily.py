"""
Tavily AI-optimized search evidence retrieval service.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

TAVILY_URL = "https://api.tavily.com/search"


async def search(query: str, max_results: int = 6) -> list[dict[str, Any]]:
    """Search via Tavily API. Returns list of result dicts with extracted content."""
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY not set, skipping Tavily search")
        return []

    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": "advanced",
        "include_answer": False,
        "include_raw_content": False,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(TAVILY_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "snippet": item.get("content", "")[:500],
                "source_name": _extract_domain(item.get("url", "")),
                "published_at": item.get("published_date"),
                "score": item.get("score", 0.0),
            })
        return results

    except Exception as e:
        logger.error(f"Tavily search failed for '{query}': {e}")
        return []


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.replace("www.", "")
    except Exception:
        return url[:50]
