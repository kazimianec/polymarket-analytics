import functools
import logging
import os

from dynaconf import Dynaconf

logger = logging.getLogger(__name__)

# Dual-file config strategy
# ──────────────────────────
# Both settings.toml and deploy.toml are always loaded. A single env switcher
# (ENV_FOR_DYNACONF) selects the active [section] across both files simultaneously.
#
# The two files partition environments by concern:
#   settings.toml — local dev environments, one [section] per developer/machine
#                   e.g. [dev_ak_mac], [dev_js], [testing]
#   deploy.toml   — deployment targets: [docker], [ci], [production]
#
# When a section exists in only one file, dynaconf silently skips the other —
# no error, no bleed. So:
#   ENV_FOR_DYNACONF=dev_ak_mac  → loads [dev_ak_mac] from settings.toml,
#                                   finds nothing in deploy.toml (harmless)
#   ENV_FOR_DYNACONF=docker      → loads [docker] from deploy.toml,
#                                   finds nothing in settings.toml (harmless)
#
# DEPLOY_ENV is NOT a dynaconf variable. It lives in .env and is consumed by
# docker-compose, which maps it to ENV_FOR_DYNACONF inside the container:
#   environment:
#     - ENV_FOR_DYNACONF=${DEPLOY_ENV:-docker}
# This lets developers control local dev and container target independently
# from a single .env file without touching docker-compose.yml.
settings = Dynaconf(
    envvar_prefix="APP",  # if changed, update APP_CORS_ORIGINS in docker-compose.yml to match
    settings_files=["settings.toml", "deploy.toml", ".secrets.toml"],
    environments=True,
    env_switcher="ENV_FOR_DYNACONF",
    # Loads .env from the working directory in local dev.
    # In Docker, .env is excluded by backend/.dockerignore so this is a no-op
    # there — production config is injected via docker-compose environment:.
    # In tests, always run via `make test-backend` (cwd = backend/), so .env
    # at the repo root is NOT found and this is a no-op. Running pytest from
    # the repo root (where .env exists) can bleed env vars into settings —
    # use `make test-backend` or `cd backend && pytest` to stay safe.
    load_dotenv=True,
)

_LOCAL_HOSTS: tuple[str, ...] = ("localhost", "127.0.0.1")


@functools.cache
def get_cors_origins() -> tuple[str, ...]:
    """Return CORS origins for the app.

    Uses ``cors_origins`` from settings if explicitly configured. Otherwise,
    if ``cors_allow_derived_origins`` is ``true``, derives localhost origins
    from ``VITE_PORT`` and ``FRONTEND_HOST_PORT`` (defaults: 5173, 5174).

    Result is cached — a server restart is required when ports or settings change.
    In tests, call ``get_cors_origins.cache_clear()`` between cases.

    Returns:
        A tuple of allowed origin strings.

    Raises:
        RuntimeError: If ``cors_origins`` is not set and ``cors_allow_derived_origins`` is false.
        ValueError: If a port env var is not a valid TCP port.
    """
    if (origins := settings.get("cors_origins")) is not None:
        if not origins:
            logger.warning(
                "blocked. Set it to a non-empty list, or remove it and "
                "set cors_allow_derived_origins = true to derive dev origins."
            )
        return tuple(origins)

    if not settings.get("cors_allow_derived_origins", False):
        raise RuntimeError(
            "cors_origins is not configured. "
            "Set cors_origins in settings.toml or via APP_CORS_ORIGINS, "
            "or set cors_allow_derived_origins = true to derive from VITE_PORT / FRONTEND_HOST_PORT."
        )

    raw: list[str] = []
    for var, default in (("VITE_PORT", "5173"), ("FRONTEND_HOST_PORT", "5174")):
        port = os.environ.get(var, default).strip()
        try:
            port_int = int(port)
            if not 1 <= port_int <= 65535:
                raise ValueError
        except ValueError:
            raise ValueError(f"{var}={port!r} is not a valid TCP port (1–65535).") from None
        raw.extend(f"http://{host}:{port}" for host in _LOCAL_HOSTS)
    return tuple(dict.fromkeys(raw))
