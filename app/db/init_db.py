"""
Database initialisation helpers.
Called once during app startup (lifespan) to create tables if not present.
"""
from app.db.session import engine, Base

# Import all models so SQLAlchemy registers them on Base.metadata
import app.models.models  # noqa: F401


async def create_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
