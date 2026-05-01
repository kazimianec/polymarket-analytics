"""Async SQLAlchemy engine and session factory for Cloud SQL proxy connectivity.

Engine and session factory are constructed lazily on first use. This allows
safe module import in the testing environment where DB credentials are absent.

Typical usage in a router — pass the session into a service, never query directly::

    from typing import Annotated
    from fastapi import Depends
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.database import get_db
    from app.services.my_service import fetch_items

    async def my_endpoint(db: Annotated[AsyncSession, Depends(get_db)]) -> ...:
        return await fetch_items(db)
"""

import functools
import logging
from collections.abc import AsyncGenerator

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

logger = logging.getLogger(__name__)


def _build_database_url() -> URL:
    """Assemble the asyncpg connection URL from dynaconf settings.

    Returns a SQLAlchemy URL object, which masks the password in logs and repr.

    Returns:
        URL: A SQLAlchemy-compatible async connection URL.

    Raises:
        RuntimeError: If pg_user or pg_password are not configured.
    """
    user = settings.get("pg_user")
    password = settings.get("pg_password")
    host = settings.get("pg_host", "127.0.0.1")
    port = settings.get("pg_port", 5432)
    db = settings.get("pg_db", "appdb")

    if not user or not password:
        raise RuntimeError(
            "Database credentials not configured. "
            "Set pg_user and pg_password in .secrets.toml "
            "or via APP_PG_USER / APP_PG_PASSWORD env vars."
        )

    if host.startswith("/"):
        # Unix domain socket — Cloud Run + Cloud SQL Auth Proxy.
        # asyncpg expects the socket directory in the 'host' query parameter.
        return URL.create(
            drivername="postgresql+asyncpg",
            username=user,
            password=password,
            database=db,
            query={"host": host},
        )

    return URL.create(
        drivername="postgresql+asyncpg",
        username=user,
        password=password,
        host=host,
        port=int(port),
        database=db,
    )


@functools.cache
def _get_engine() -> AsyncEngine:
    """Return the shared async engine, constructing it on first call.

    Returns:
        AsyncEngine: The configured SQLAlchemy async engine.
    """
    return create_async_engine(
        _build_database_url(),
        echo=settings.get("debug", False),
        hide_parameters=True,
        pool_pre_ping=True,
    )


@functools.cache
def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared session factory, constructing it on first call.

    Returns:
        async_sessionmaker: Configured async session factory.
    """
    return async_sessionmaker(_get_engine(), expire_on_commit=False)


async def dispose_engine() -> None:
    """Dispose the shared engine if it has been initialised.

    Safe to call unconditionally — no-op when the engine was never created.
    Intended for use in the FastAPI lifespan shutdown handler.
    """
    if _get_engine.cache_info().currsize > 0:
        await _get_engine().dispose()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session per request.

    Commits on success and rolls back on exception. Intended for use
    as a FastAPI dependency via ``Annotated[AsyncSession, Depends(get_db)]``.

    Services and routers must not call ``session.commit()`` or
    ``session.rollback()`` directly — this dependency handles both.

    Yields:
        AsyncSession: An open database session.
    """
    async with _get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
