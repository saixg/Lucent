import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.init_db import create_all_tables
from app.api.routes import investigations, conversations, upload, health

settings = get_settings()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("VeriLens API starting up...")
    try:
        await create_all_tables()
        logger.info("Database tables verified ✓")
    except Exception as e:
        logger.error(f"DB init failed: {e}")

    if settings.SENTRY_DSN and not settings.SENTRY_DSN.startswith("https://..."):
        import sentry_sdk
        sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.2)
        logger.info("Sentry initialized ✓")

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("VeriLens API shutting down...")


app = FastAPI(
    title="VeriLens API",
    version="0.1.0",
    description="Multimodal misinformation verification engine",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.FRONTEND_URL, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
except Exception:
    pass

app.include_router(health.router,          prefix="/api/v1")
app.include_router(investigations.router,  prefix="/api/v1")
app.include_router(conversations.router,   prefix="/api/v1")
app.include_router(upload.router,          prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "VeriLens API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "health": "/api/v1/health",
    }
