"""Health check service — aggregates runtime info and infrastructure checks."""

import logging
import os
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.responses.health import CheckResult, HealthResponse

logger = logging.getLogger(__name__)


def _detect_runtime() -> str:
    """Return 'container' when running inside Docker or Kubernetes, else 'local'.

    Returns:
        str: "container" or "local".
    """
    if Path("/.dockerenv").exists() or os.getenv("KUBERNETES_SERVICE_HOST"):
        return "container"
    return "local"


def _detect_env() -> str:
    """Return the active dynaconf environment name.

    Returns:
        str: Value of ENV_FOR_DYNACONF, defaulting to "default".
    """
    return os.getenv("ENV_FOR_DYNACONF", "default")


async def _check_database(db: AsyncSession) -> CheckResult:
    """Verify database connectivity with a SELECT 1 query.

    Args:
        db: Async database session to test.

    Returns:
        CheckResult: status "ok" on success, "error" with detail on failure.
    """
    try:
        await db.execute(text("SELECT 1"))
        return CheckResult(status="ok")
    except Exception as exc:
        logger.exception("Database health check failed: %s", exc)
        return CheckResult(status="error", detail="database unreachable")


async def get_health(db: AsyncSession) -> HealthResponse:
    """Aggregate all health checks into a HealthResponse.

    Args:
        db: Async database session injected by the router.

    Returns:
        HealthResponse: Overall status, runtime info, and named check results.
    """
    checks: dict[str, CheckResult] = {
        "database": await _check_database(db),
    }
    overall = "ok" if all(c.status == "ok" for c in checks.values()) else "degraded"
    return HealthResponse(
        status=overall,
        app_name=settings.app_name,
        env=_detect_env(),
        runtime=_detect_runtime(),
        checks=checks,
    )
