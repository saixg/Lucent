"""
Single responsibility: Automated test suite for Phase 2 image verification and multimodal forensics.
"""

import io
import pytest
from PIL import Image, ImageDraw
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.session import get_db, Base
from app.main import app
from app.services.image_forensics import check_image_forensics
from app.services.image_analyzer import analyze_image_with_vision
from app.schemas.verdict import VerdictLabel, ConfidenceLevel


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def sample_image_bytes():
    img = Image.new("RGB", (320, 240), color=(30, 45, 60))
    draw = ImageDraw.Draw(img)
    draw.text((20, 100), "Apollo 11 Moon Landing 1969", fill=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
async def test_client():
    test_engine = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)
    test_session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await test_engine.dispose()


@pytest.mark.anyio
async def test_sightengine_forensics(sample_image_bytes):
    """Test Sightengine AI image generation detection service."""
    result = await check_image_forensics(sample_image_bytes, "image/jpeg")
    assert result["status"] in ["success", "unavailable"]
    assert "ai_generated_score" in result
    assert isinstance(result["ai_generated_score"], float)


@pytest.mark.anyio
async def test_gemini_multimodal_vision(sample_image_bytes):
    """Test Gemini multimodal vision claim extraction."""
    analysis = await analyze_image_with_vision(sample_image_bytes, "image/jpeg")
    assert analysis.scene_description is not None
    assert len(analysis.extracted_claims) > 0


@pytest.mark.anyio
async def test_end_to_end_image_verification(test_client, sample_image_bytes):
    """Test full Phase 2 multipart image verification endpoint."""
    files = {
        "file": ("apollo11.jpg", sample_image_bytes, "image/jpeg"),
    }
    resp = await test_client.post("/api/v1/verifications/verify-image", files=files)
    assert resp.status_code == 201
    data = resp.json()

    assert data["id"] is not None
    assert data["content_type"] == "image"
    assert data["status"] == "completed"
    assert data["verdict_label"] in [l.value for l in VerdictLabel]
    assert data["confidence_level"] in [c.value for c in ConfidenceLevel]
    assert len(data["evidence_items"]) > 0
