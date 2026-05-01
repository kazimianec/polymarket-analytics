"""Unit tests for database URL assembly. No live DB connection required."""

from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _clear_db_cache() -> Generator[None, None, None]:
    """Clear engine/session factory caches between database tests.

    Intentionally file-local (defined here rather than conftest.py) because
    only database tests require cache isolation. Tests in other modules that
    import app.database do not need this fixture.
    """
    from app import database

    database._get_engine.cache_clear()
    database._get_session_factory.cache_clear()
    yield
    database._get_engine.cache_clear()
    database._get_session_factory.cache_clear()


def _mock_settings(**overrides: object) -> MagicMock:
    data = {
        "pg_user": "app",
        "pg_password": "secret",
        "pg_host": "127.0.0.1",
        "pg_port": 5435,
        "pg_db": "appdb_dev",
        **overrides,
    }
    m = MagicMock()
    m.get.side_effect = lambda key, default=None: data.get(key, default)
    return m


def test_build_database_url_correct() -> None:
    """URL is correctly assembled from settings and password is masked in repr."""
    with patch("app.database.settings", _mock_settings()):
        from app.database import _build_database_url

        url = _build_database_url()
        assert url.render_as_string(hide_password=False) == (
            "postgresql+asyncpg://app:secret@127.0.0.1:5435/appdb_dev"
        )
        assert "secret" not in str(url), "Password must be masked in str(url)"


@pytest.mark.parametrize(
    "pg_user, pg_password",
    [
        (None, None),
        (None, "secret"),
        ("app", None),
    ],
)
def test_build_database_url_raises_without_credentials(
    pg_user: str | None, pg_password: str | None
) -> None:
    """RuntimeError is raised when either or both credentials are absent."""
    with patch("app.database.settings", _mock_settings(pg_user=pg_user, pg_password=pg_password)):
        from app.database import _build_database_url

        with pytest.raises(RuntimeError, match="Database credentials not configured"):
            _build_database_url()
