"""
Media content extractor — handles YouTube, Instagram Reels/Posts, Twitter/X, TikTok, web articles, images, and raw media files.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import tempfile
from dataclasses import dataclass, field
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MediaContent:
    """Normalized content extracted from any source."""
    raw_text: str = ""
    title: str = ""
    description: str = ""
    transcript: str = ""
    platform: str = "web"
    source_url: str = ""
    video_path: str | None = None
    audio_path: str | None = None
    image_bytes: bytes | None = None
    image_mime: str = "image/jpeg"
    duration_seconds: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        """Combine all text for claim extraction."""
        parts = [self.title, self.description, self.transcript, self.raw_text]
        # Remove duplicate text parts
        seen = set()
        unique = []
        for p in parts:
            p_clean = p.strip()
            if p_clean and p_clean not in seen:
                seen.add(p_clean)
                unique.append(p_clean)
        return "\n\n".join(unique).strip()


async def extract_from_url(url: str) -> MediaContent:
    """Auto-detect URL type and extract content with fallbacks."""
    url = url.strip()
    url_lower = url.lower()

    if any(domain in url_lower for domain in ["youtube.com", "youtu.be", "instagram.com", "twitter.com", "x.com", "tiktok.com", "fb.watch", "facebook.com"]):
        platform = "youtube" if ("youtube.com" in url_lower or "youtu.be" in url_lower) \
            else "instagram" if "instagram.com" in url_lower \
            else "x" if ("twitter.com" in url_lower or "x.com" in url_lower) \
            else "tiktok" if "tiktok.com" in url_lower \
            else "web"
        return await _extract_social_media(url, platform)

    if url_lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
        return await _extract_image_url(url)

    return await _extract_web_article(url)


async def _extract_social_media(url: str, platform: str = "web") -> MediaContent:
    """Extract metadata, captions, and thumbnails from YouTube, Instagram, Twitter/X, TikTok using yt-dlp + OpenGraph fallback."""
    title = ""
    description = ""
    duration = None
    thumbnail_url = None
    meta = {"platform": platform, "url": url}
    image_bytes = None

    try:
        import yt_dlp  # type: ignore

        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "ignoreerrors": True,
        }

        loop = asyncio.get_event_loop()

        def _extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)

        info = await loop.run_in_executor(None, _extract)

        if info and isinstance(info, dict):
            title = info.get("title") or ""
            description = info.get("description") or info.get("caption") or ""
            duration = info.get("duration")
            thumbnail_url = info.get("thumbnail")
            meta.update({
                "uploader": info.get("uploader") or info.get("channel") or "",
                "view_count": info.get("view_count", 0),
                "like_count": info.get("like_count", 0),
                "upload_date": info.get("upload_date", ""),
                "tags": (info.get("tags") or [])[:10],
            })
    except Exception as e:
        logger.warning(f"yt-dlp extraction note for {url}: {e}")

    # Fallback to OpenGraph HTML extraction if yt-dlp description is empty
    if not description.strip() and not title.strip():
        og_title, og_desc, og_image = await _fetch_opengraph_meta(url)
        if og_title:
            title = title or og_title
        if og_desc:
            description = description or og_desc
        if og_image and not thumbnail_url:
            thumbnail_url = og_image

    # Download thumbnail/image if available for vision analysis & forensics
    if thumbnail_url:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(thumbnail_url)
                if resp.status_code == 200:
                    image_bytes = resp.content
        except Exception as e:
            logger.warning(f"Thumbnail download warning for {thumbnail_url}: {e}")

    raw_text_parts = []
    if title:
        raw_text_parts.append(f"Title: {title}")
    if description:
        raw_text_parts.append(f"Caption/Description: {description}")
    if not raw_text_parts:
        raw_text_parts.append(f"Post URL: {url}")

    return MediaContent(
        platform=platform,
        source_url=url,
        title=title,
        description=description,
        raw_text="\n\n".join(raw_text_parts),
        duration_seconds=duration,
        image_bytes=image_bytes,
        image_mime="image/jpeg",
        metadata=meta,
    )


async def _fetch_opengraph_meta(url: str) -> tuple[str, str, str]:
    """Extract (title, description, image_url) from HTML OpenGraph & Twitter meta tags."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        async with httpx.AsyncClient(timeout=10.0, headers=headers, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                return "", "", ""
            html = resp.text

        title, desc, image_url = "", "", ""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")

            for attr in [{"property": "og:title"}, {"name": "twitter:title"}, {"name": "title"}]:
                tag = soup.find("meta", attrs=attr)
                if tag and tag.get("content"):
                    title = tag["content"].strip()
                    break
            if not title and soup.find("title"):
                title = soup.find("title").get_text().strip()

            for attr in [{"property": "og:description"}, {"name": "twitter:description"}, {"name": "description"}]:
                tag = soup.find("meta", attrs=attr)
                if tag and tag.get("content"):
                    desc = tag["content"].strip()
                    break

            for attr in [{"property": "og:image"}, {"name": "twitter:image"}]:
                tag = soup.find("meta", attrs=attr)
                if tag and tag.get("content"):
                    image_url = tag["content"].strip()
                    break
        except Exception:
            pass

        return title, desc, image_url
    except Exception as e:
        logger.warning(f"OpenGraph fetch failed for {url}: {e}")
        return "", "", ""


async def _extract_web_article(url: str) -> MediaContent:
    """Extract article text using trafilatura + OpenGraph fallback."""
    title = ""
    text = ""
    image_bytes = None

    try:
        import trafilatura  # type: ignore

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(
            timeout=15.0,
            headers=headers,
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        ) or ""

        og_title, og_desc, og_image = await _fetch_opengraph_meta(url)
        title = og_title or ""
        if not text and og_desc:
            text = og_desc

        if og_image:
            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    img_resp = await client.get(og_image)
                    if img_resp.status_code == 200:
                        image_bytes = img_resp.content
            except Exception:
                pass

        return MediaContent(
            platform="web",
            source_url=url,
            title=title,
            description=og_desc or "",
            raw_text=(text or og_desc or title or url)[:6000],
            image_bytes=image_bytes,
        )
    except Exception as e:
        logger.error(f"Web article extraction failed for {url}: {e}")
        og_title, og_desc, _ = await _fetch_opengraph_meta(url)
        return MediaContent(
            platform="web",
            source_url=url,
            title=og_title,
            description=og_desc,
            raw_text=og_desc or og_title or url,
        )


async def _extract_image_url(url: str) -> MediaContent:
    """Download image from URL."""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            image_bytes = resp.content
            mime = resp.headers.get("content-type", "image/jpeg").split(";")[0]
        return MediaContent(
            platform="web",
            source_url=url,
            image_bytes=image_bytes,
            image_mime=mime,
            raw_text=f"Image URL: {url}",
        )
    except Exception as e:
        logger.error(f"Image download failed for {url}: {e}")
        return MediaContent(platform="web", source_url=url, raw_text=url)


async def extract_from_bytes(
    content: bytes, mime_type: str, filename: str = ""
) -> MediaContent:
    """Extract content from uploaded file bytes."""
    major = mime_type.split("/")[0]
    file_hash = hashlib.sha256(content).hexdigest()

    if major == "image":
        return MediaContent(
            platform="web",
            image_bytes=content,
            image_mime=mime_type,
            raw_text=f"Uploaded image: {filename}",
            metadata={"filename": filename, "hash": file_hash, "size": len(content)},
        )
    elif major in ("video", "audio"):
        suffix = f".{mime_type.split('/')[-1]}"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.write(content)
        tmp.close()
        result = MediaContent(
            platform="web",
            raw_text=f"Uploaded {major}: {filename}",
            metadata={"filename": filename, "hash": file_hash, "size": len(content)},
        )
        if major == "video":
            result.video_path = tmp.name
        else:
            result.audio_path = tmp.name
        return result
    else:
        return MediaContent(platform="web", raw_text=content.decode("utf-8", errors="ignore")[:5000])
