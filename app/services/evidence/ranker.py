"""
Evidence ranker — combines Serper + Tavily results, deduplicates,
and uses Gemini to analyze stance and credibility.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.services.evidence import serper, tavily
from app.services.ai import gemini

logger = logging.getLogger(__name__)

# Known high-authority domains for tier assignment
TIER_1_DOMAINS = {
    "rbi.org.in", "gov.in", "pib.gov.in", "nic.in",
    "who.int", "cdc.gov", "nih.gov", "fda.gov",
    "ec.europa.eu", "un.org", "worldbank.org",
    "supremecourt.gov.in", "mha.gov.in", "mef.in",
}

TIER_2_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
    "thehindu.com", "ndtv.com", "hindustantimes.com",
    "indianexpress.com", "timesofindia.com", "theguardian.com",
    "nytimes.com", "washingtonpost.com", "bloomberg.com",
    "ft.com", "economist.com", "aljazeera.com",
}

TIER_3_DOMAINS = {
    "snopes.com", "factcheck.org", "politifact.com",
    "boomlive.in", "altnews.in", "factchecker.in",
    "vishvasnews.com", "factly.in",
}


def _assign_tier(domain: str) -> int:
    domain = domain.lower()
    if any(t in domain for t in TIER_1_DOMAINS):
        return 1
    if any(t in domain for t in TIER_2_DOMAINS):
        return 2
    if any(t in domain for t in TIER_3_DOMAINS):
        return 3
    return 4


async def gather_and_rank_evidence(claim_text: str, max_results: int = 12) -> list[dict[str, Any]]:
    """
    Search multiple sources and rank evidence for a claim.
    Returns a list of enriched evidence dicts sorted by tier + credibility.
    """
    # Build search queries
    queries = [
        claim_text,
        f'fact check: "{claim_text[:80]}"',
    ]

    # Gather from all queries concurrently
    search_tasks = []
    for query in queries:
        search_tasks.append(serper.search(query, num=6))
        search_tasks.append(tavily.search(query, max_results=4))

    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    all_raw: list[dict] = []
    for r in search_results:
        if isinstance(r, list):
            all_raw.extend(r)

    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique: list[dict] = []
    for item in all_raw:
        url = item.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            item["source_tier"] = _assign_tier(item.get("source_name", ""))
            unique.append(item)

    # Sort by tier first, then by Tavily score if available
    unique.sort(key=lambda x: (x.get("source_tier", 4), -x.get("score", 0.0)))
    top = unique[:max_results]

    # Analyze stance via Gemini for top results (limit to 8 to save quota)
    # Use semaphore to avoid overwhelming Gemini's rate limits (free tier: 5 req/min)
    sem = asyncio.Semaphore(3)

    async def _analyze_with_limit(item: dict) -> dict:
        async with sem:
            result = await gemini.analyze_evidence_stance(
                claim=claim_text,
                title=item.get("title", ""),
                snippet=item.get("snippet", ""),
                source=item.get("source_name", ""),
            )
            await asyncio.sleep(0.5)  # small delay to stay under rate limits
            return result

    analysis_tasks = [_analyze_with_limit(item) for item in top[:8]]
    analyses = await asyncio.gather(*analysis_tasks, return_exceptions=True)

    enriched = []
    for i, item in enumerate(top):
        tier = item.get("source_tier", 4)
        analysis = analyses[i] if i < len(analyses) and isinstance(analyses[i], dict) and analyses[i].get("stance") else _fallback_stance_analysis(claim_text, item.get("title", ""), item.get("snippet", ""), item.get("source_name", ""), tier)
        enriched.append({
            **item,
            "stance": analysis.get("stance", "supports"),
            "relevance_score": analysis.get("relevance_score", 0.85),
            "credibility_score": analysis.get("credibility_score", 0.88 if tier <= 2 else 0.75),
            "source_tier": analysis.get("source_tier", tier),
            "source_type": _classify_source_type(item.get("source_name", ""), analysis.get("source_tier", tier)),
        })

    # Re-sort after Gemini enrichment
    enriched.sort(key=lambda x: (x.get("source_tier", 4), -x.get("credibility_score", 0.0)))
    return enriched


def _classify_source_type(domain: str, tier: int) -> str:
    domain = domain.lower()
    if tier == 1:
        if any(k in domain for k in ["gov", "nic", "rbi", "sebi", "who", "cdc", "nih"]):
            return "government"
        return "regulator"
    if tier == 2:
        return "news"
    if tier == 3:
        return "factcheck"
    return "other"


def _fallback_stance_analysis(claim_text: str, title: str, snippet: str, source_name: str, tier: int) -> dict:
    """Analyze stance and credibility using title/snippet text match when LLM is unavailable."""
    text = (title + " " + snippet).lower()
    claim_lower = claim_text.lower()

    credibility = 0.95 if tier == 1 else 0.88 if tier == 2 else 0.82 if tier == 3 else 0.70

    refute_keywords = ["fake", "false", "hoax", "banned", "denies", "debunk", "myth", "incorrect", "untrue", "no truth", "misleading", "fraud", "scam"]
    support_keywords = ["confirm", "official", "announced", "launch", "approved", "verified", "statement", "reports", "agreed", "valid", "true"]

    is_refute = any(k in text for k in refute_keywords)
    is_support = any(k in text for k in support_keywords)

    if is_refute and not is_support:
        stance = "refutes"
    elif is_support and not is_refute:
        stance = "supports"
    elif any(word in text for word in claim_lower.split() if len(word) > 4):
        stance = "supports"
    else:
        stance = "supports"

    return {
        "stance": stance,
        "relevance_score": 0.85,
        "credibility_score": credibility,
        "source_tier": tier,
    }
