from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_cors_origins
from app.database import dispose_engine
from app.routers.domain.health import router as health_router
from app.routers.domain.markets import router as markets_router
from app.routers.domain.stats import router as stats_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan: dispose DB engine on shutdown."""
    yield
    await dispose_engine()


app = FastAPI(title="Fullstack Template API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api/v1")
app.include_router(markets_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
