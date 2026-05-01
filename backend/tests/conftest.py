import os
from collections.abc import Generator

import pytest

# Set the dynaconf env before any test module imports app.main, so that
# get_cors_origins() sees cors_allow_derived_origins = true from [testing].
os.environ["ENV_FOR_DYNACONF"] = "testing"


@pytest.fixture(autouse=True)
def _clear_cors_origins_cache() -> Generator[None, None, None]:
    """Clear the lru_cache on get_cors_origins before and after each test."""
    from app.config import get_cors_origins

    get_cors_origins.cache_clear()
    yield
    get_cors_origins.cache_clear()
