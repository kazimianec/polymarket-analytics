# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.1] - 2026-03-23

### Added
- `make docker-up` target — builds and starts containers, prints App / Health / API URLs on start
- `deploy.toml` — deployment target environments (`[docker]`, `[ci]`, `[production]`) split out from `settings.toml`
- `DEPLOY_ENV` variable in `.env` / `.env.example` — selects the active deploy target independently from the local dev env
- `[docker]` section in `.secrets.toml.example` for local container secrets

### Changed
- Health endpoint (`GET /api/v1/health`) now returns `app_name`, `env`, `runtime`, and per-check `checks` map
- Health endpoint returns HTTP 503 when status is `degraded` (previously always 200)
- DB error detail sanitised — logs internally, returns `"database unreachable"` to callers
- `Literal` types on all status/runtime fields in Pydantic models (`CheckResult`, `HealthResponse`)
- Backend config split: dev environments stay in `settings.toml`, deployment targets moved to `deploy.toml`; both loaded simultaneously by dynaconf
- `frontend/src/types/index.ts` cleared — domain types now live alongside their API hooks (`api/health.ts`)
- Root route (`/`) replaced redirect-to-health with a real `HomePage` stub for cleaner template starting point
- Visual regression snapshot test skipped in CI (OS-specific snapshots run locally only)
- `docker-compose.yml` CORS origins value quoted to prevent YAML token splitting on `[`

### Fixed
- Dockerfile layer ordering: `--no-root` on dep install, project installed after `COPY .` — correct layer caching
- `conftest.py`: force `ENV_FOR_DYNACONF=testing` via direct assignment (was `setdefault`, allowing `.env` bleed)
- `host.docker.internal` missing on Linux — documented; Cloud Run and Linux Docker alternatives added to `deploy.toml`
- `pg_host` restored to `[default]` in `settings.toml` (was accidentally removed)

### Security
- Raw SQLAlchemy exception messages no longer forwarded to API callers

---

## [0.2.0] - 2026-03-22

### Added
- Health endpoint (`GET /api/v1/health`) with basic status response
- Async SQLAlchemy + asyncpg database layer with `get_db` FastAPI dependency
- Cloud SQL proxy support for local development
- Frontend health status page with MUI components and Playwright e2e tests
- Docker Compose setup with backend and frontend services
- GitHub Actions CI (lint + test on push/PR to `main` and `development`)
- Claude Code auto-review workflow on every PR
- dynaconf configuration with per-developer environment sections
- `CLAUDE.md` with project conventions for AI-assisted development

---

## [0.1.0] - Initial release

- FastAPI backend scaffold with CORS, dynaconf config, Ruff linting, pytest
- React 18 frontend with Vite, MUI v6, TanStack Query v5, Zustand, React Router
- Makefile with canonical dev, test, lint, db, and versioning targets
