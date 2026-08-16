"""
Single responsibility: Query Tavily Search API for primary evidence and fact-checks, respecting call caps (rules.md §4).
"""

import httpx
from typing import List, Dict, Any
from app.core.config import settings


async def search_tavily(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """Execute a single search query against the Tavily Search API."""
    if not settings.TAVILY_API_KEY:
        return []

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "include_answer": False,
        "max_results": max_results,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code != 200:
                return []
            data = resp.json()
            return data.get("results", [])
    except Exception:
        return []


async def gather_evidence_for_claims(claims: List[str]) -> List[Dict[str, str]]:
    """
    Fan out search queries across extracted claims up to the MAX_SEARCH_QUERIES cap.
    Deduplicates URLs and normalizes evidence items into {source_title, source_url, snippet}.
    """
    if not claims:
        return []

    # Limit total search queries to cap (rules.md §4)
    queries_to_run = claims[: settings.MAX_SEARCH_QUERIES_PER_VERIFICATION]
    seen_urls = set()
    raw_evidence_items: List[Dict[str, str]] = []

    for claim in queries_to_run:
        # 1. Search the factual claim directly
        results = await search_tavily(f"{claim} fact check news evidence", max_results=3)
        for r in results:
            url = r.get("url", "").strip()
            title = r.get("title", "").strip()
            content = r.get("content", "").strip()

            if url and url not in seen_urls and content:
                seen_urls.add(url)
                raw_evidence_items.append({
                    "source_title": title or url,
                    "source_url": url,
                    "snippet": content[:1200],
                })

    return raw_evidence_items
