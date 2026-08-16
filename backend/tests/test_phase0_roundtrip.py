"""
Single responsibility: Validate Phase 0 health check and DB round-trip persistence using anyio.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.session import get_db, Base
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def test_client():
    # Use NullPool for tests so asyncpg connections don't leak across event loops
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
async def test_health_endpoint(test_client):
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert data["service"] == "Lucent Verification Engine"


@pytest.mark.anyio
async def test_verification_db_roundtrip(test_client):
    # 1. Create a verification entry
    payload = {
        "content": "NASA discovered liquid water on Europa in 2026.",
        "content_type": "text",
    }
    create_resp = await test_client.post("/api/v1/verifications", json=payload)
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["id"] is not None
    assert created["raw_input_ref"] == payload["content"]
    assert created["status"] == "pending"

    # 2. Retrieve the verification from the database by ID
    get_resp = await test_client.get(f"/api/v1/verifications/{created['id']}")
    assert get_resp.status_code == 200
    retrieved = get_resp.json()
    assert retrieved["id"] == created["id"]
    assert retrieved["raw_input_ref"] == payload["content"]
    assert retrieved["status"] == "pending"

    # 3. List verifications
    list_resp = await test_client.get("/api/v1/verifications")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert any(item["id"] == created["id"] for item in items)
