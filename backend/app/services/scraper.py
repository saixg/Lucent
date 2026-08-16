"""
Single responsibility: Fetch and extract clean article text from input URLs.
"""

import httpx
import trafilatura
from typing import Optional


async def scrape_url_content(url: str, timeout: float = 10.0) -> Optional[str]:
    """
    Fetch a web page and extract readable main body text using trafilatura.
    Falls back gracefully if scraping fails.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return None
            html = resp.text

        # Extract main text
        extracted_text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )
        return extracted_text.strip() if extracted_text else None
    except Exception:
        return None
