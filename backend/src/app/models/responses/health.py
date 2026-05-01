from typing import Literal

from pydantic import BaseModel


class CheckResult(BaseModel):
    """Result of a single named health check."""

    status: Literal["ok", "error"]
    detail: str | None = None


class HealthResponse(BaseModel):
    """Health check response model."""

    status: Literal["ok", "degraded"]
    app_name: str
    env: str
    runtime: Literal["container", "local"]
    checks: dict[str, CheckResult]
