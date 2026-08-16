"""
Single responsibility: Automated test suite for Phase 1 verification pipeline and verdict contract adherence.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.session import get_db, Base
from app.main import app
from app.schemas.verdict import VerdictLabel, ConfidenceLevel
from app.services.verdict_synthesizer import synthesize_verdict


@pytest.fixture
def anyio_backend():
    return "asyncio"


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
async def test_unverifiable_guard_when_evidence_is_empty():
    """Verify rules.md §2: Empty evidence MUST force Unverifiable verdict without hallucinations."""
    verdict = await synthesize_verdict(
        raw_input="Aliens built a secret submarine base in Lake Michigan in 2026.",
        extracted_claims=["Aliens built a secret submarine base in Lake Michigan in 2026."],
        evidence_items=[],
    )
    assert verdict.verdict_label == VerdictLabel.UNVERIFIABLE
    assert verdict.confidence_level == ConfidenceLevel.LOW
    assert len(verdict.confidence_reason) > 0
    assert len(verdict.explanation) > 0
    assert len(verdict.evidence) == 0


@pytest.mark.anyio
async def test_end_to_end_verification_and_follow_up(test_client):
    """Test full Phase 1 verify endpoint and grounded follow-up conversation."""
    # 1. Submit claim for verification
    payload = {
        "content": "The Eiffel Tower is located in Paris, France.",
        "content_type": "text",
    }
    resp = await test_client.post("/api/v1/verifications/verify", json=payload)
    assert resp.status_code == 201
    data = resp.json()

    assert data["id"] is not None
    assert data["status"] == "completed"
    assert data["verdict_label"] in [l.value for l in VerdictLabel]
    assert data["confidence_level"] in [c.value for c in ConfidenceLevel]
    assert data["confidence_reason"] is not None
    assert data["explanation"] is not None
    assert len(data["evidence_items"]) > 0

    verification_id = data["id"]

    # 2. Submit follow-up question
    follow_up_payload = {"message": "When was it built and which country is it in?"}
    fu_resp = await test_client.post(
        f"/api/v1/verifications/{verification_id}/follow-up",
        json=follow_up_payload,
    )
    assert fu_resp.status_code == 200
    fu_data = fu_resp.json()
    assert len(fu_data["follow_up_messages"]) == 2  # user + assistant
    assert fu_data["follow_up_messages"][0]["role"] == "user"
    assert fu_data["follow_up_messages"][1]["role"] == "assistant"
    assert len(fu_data["follow_up_messages"][1]["content"]) > 10
