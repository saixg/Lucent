"""
Single responsibility: Initialize and configure the FastAPI application, CORS middleware, lifespan events, and API router.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup if they do not exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Lucent Verification Engine API",
    description="Content verification backend providing structured verdicts, evidence citations, and follow-up capabilities.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "service": "Lucent Verification Engine API",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0",
    }
