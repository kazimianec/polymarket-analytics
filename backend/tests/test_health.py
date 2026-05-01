from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.main import app


async def _mock_db():
    """Yield a mock AsyncSession that succeeds for all queries."""
    yield AsyncMock(spec=AsyncSession)


async def _failing_db():
    """Yield a mock AsyncSession that raises on execute."""
    mock = AsyncMock(spec=AsyncSession)
    mock.execute.side_effect = Exception("connection refused")
    yield mock


@pytest.fixture()
def client():
    """TestClient with the DB dependency overridden to a healthy mock."""
    app.dependency_overrides[get_db] = _mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def failing_client():
    """TestClient with the DB dependency overridden to a failing mock."""
    app.dependency_overrides[get_db] = _failing_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_returns_ok(client: TestClient) -> None:
    """GET /api/v1/health should return 200 ok when DB is up."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "fullstack-template"
    assert body["env"] == "testing"
    assert body["runtime"] in {"local", "container"}
    assert "database" in body["checks"]


def test_health_returns_degraded_when_db_fails(failing_client: TestClient) -> None:
    """GET /api/v1/health should return 503 degraded when DB check fails."""
    response = failing_client.get("/api/v1/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"]["database"]["status"] == "error"
    assert body["checks"]["database"]["detail"] == "database unreachable"
