from unittest.mock import MagicMock, patch

import pytest

from app.config import get_cors_origins, settings


def _mock_settings(
    cors_origins: list | None = None,
    cors_allow_derived_origins: bool = True,
) -> MagicMock:
    mock = MagicMock()

    def _get(key: str, default=None):
        if key == "cors_origins":
            return cors_origins
        if key == "cors_allow_derived_origins":
            return cors_allow_derived_origins
        return default

    mock.get.side_effect = _get
    return mock


def test_config_has_required_keys() -> None:
    """Settings object exposes expected keys with correct types."""
    assert isinstance(settings.app_name, str) and settings.app_name


def test_get_cors_origins_returns_nonempty_tuple(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_cors_origins returns a non-empty tuple of origin strings in dev."""
    monkeypatch.delenv("VITE_PORT", raising=False)
    monkeypatch.delenv("FRONTEND_HOST_PORT", raising=False)
    with patch("app.config.settings", _mock_settings()):
        origins = get_cors_origins()
    assert isinstance(origins, tuple) and len(origins) > 0
    assert all(origin.startswith("http") for origin in origins)


def test_get_cors_origins_derives_urls_from_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_cors_origins builds localhost and 127.0.0.1 origins from port env vars."""
    monkeypatch.setenv("VITE_PORT", "3000")
    monkeypatch.setenv("FRONTEND_HOST_PORT", "3001")
    with patch("app.config.settings", _mock_settings()):
        origins = get_cors_origins()
    assert "http://localhost:3000" in origins
    assert "http://127.0.0.1:3000" in origins
    assert "http://localhost:3001" in origins
    assert "http://127.0.0.1:3001" in origins


def test_get_cors_origins_uses_explicit_setting() -> None:
    """get_cors_origins returns cors_origins from settings when explicitly set."""
    with patch("app.config.settings", _mock_settings(cors_origins=["https://example.com"])):
        origins = get_cors_origins()
    assert origins == ("https://example.com",)


def test_get_cors_origins_respects_explicit_empty_list() -> None:
    """get_cors_origins returns () and logs a warning when cors_origins is explicitly []."""
    with (
        patch("app.config.settings", _mock_settings(cors_origins=[])),
        patch("app.config.logger") as mock_logger,
    ):
        origins = get_cors_origins()
    mock_logger.warning.assert_called_once()
    assert origins == ()


def test_get_cors_origins_raises_on_non_numeric_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_cors_origins raises ValueError for non-numeric port values."""
    monkeypatch.setenv("VITE_PORT", "abc")
    with (
        patch("app.config.settings", _mock_settings()),
        pytest.raises(ValueError, match="not a valid TCP port"),
    ):
        get_cors_origins()


def test_get_cors_origins_raises_on_out_of_range_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_cors_origins raises ValueError for out-of-range port values."""
    monkeypatch.setenv("FRONTEND_HOST_PORT", "99999")
    with (
        patch("app.config.settings", _mock_settings()),
        pytest.raises(ValueError, match="not a valid TCP port"),
    ):
        get_cors_origins()


def test_get_cors_origins_raises_when_derived_origins_not_allowed() -> None:
    """get_cors_origins raises RuntimeError when cors_allow_derived_origins is false/unset."""
    with (
        patch("app.config.settings", _mock_settings(cors_allow_derived_origins=False)),
        pytest.raises(RuntimeError, match="cors_origins is not configured"),
    ):
        get_cors_origins()
