import asyncio
from app.db.session import engine, Base
import app.models # register models

async def init_db():
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully!")
    await engine.dispose()

asyncio.run(init_db())
