# Fullstack Template

A GitHub project template for AI-assisted fullstack projects, optimised for use with [Claude Code](https://claude.ai/code).

**Stack:** Python 3.12 · FastAPI · Pydantic v2 · React 18 · Vite · MUI v6 · TanStack Query v5

> New to this repo? See [README_SETUP.md](README_SETUP.md) for environment setup and first-run instructions.

---

## What's Included

| Area | What's wired up |
|------|----------------|
| Backend | FastAPI app, CORS, dynaconf config, `GET /api/v1/health` |
| Frontend | React 18, MUI v6 theme, TanStack Query provider, React Router, `/health` status page |
| Database | Async SQLAlchemy + asyncpg, `get_db` FastAPI dependency, Cloud SQL proxy support, `scripts/db/` for schema files |
| Testing | pytest for backend (imports, health, config, OpenAPI routes, Pydantic models), Playwright for frontend e2e |
| Linting | Ruff (backend), ESLint v9 + typescript-eslint + react-hooks (frontend) |
| CI | GitHub Actions — lint + test on push/PR to `main` and `development` |
| Claude Code Review | Automatic AI code review on every PR via `claude-code-review.yml` |
| Docker | `docker-compose.yml` with backend + frontend services |
| Conventions | `CLAUDE.md` — read by Claude Code to understand project structure and rules |
| Slash commands | `/new-feature`, `/new-page`, `/ui-review` — scaffold and review workflows |

---

## Development

### Without containers (recommended)

Full hot-reload on every file save.

```bash
make dev             # Start backend + frontend concurrently
make dev-backend     # Backend only (default port 8000)
make dev-frontend    # Frontend only (default port 5173)
make stop            # Kill host dev processes only (backend + frontend ports)
```

Backend: `http://localhost:8000` · Frontend: `http://localhost:5173`

### With containers

Backend hot-reloads via volume mount; frontend requires a rebuild on source changes.

```bash
make docker-up              # Build and start both containers (prints URLs on start)
make docker-down            # Stop and remove containers only
make docker-rebuild         # Stop everything, rebuild images, and start fresh
make stop-all               # Kill host dev processes AND stop containers
docker compose up           # Start without rebuilding
```

Default ports when containerised: backend `8001`, frontend `5174` (configurable via `.env`).

> **Note:** Always stop local dev servers before starting containers (`make stop`) — if both run simultaneously, Vite auto-increments its port and collides with the Docker port mapping, causing the Docker frontend to proxy to the local backend instead of the container backend.

Set `DEPLOY_ENV` in `.env` to switch the deployment target loaded inside containers:

| `DEPLOY_ENV` | Target | `pg_host` |
|---|---|---|
| `docker` (default) | Docker Desktop — macOS, Windows, Linux, WSL2 | `host.docker.internal` |
| `ci` | GitHub Actions | `postgres` (service container) |
| `production` | Cloud Run + Cloud SQL Auth Proxy | `127.0.0.1` |

---

## Commands

**Testing & linting**
```bash
make test-backend    # pytest
make test-frontend   # Playwright e2e
make lint-backend    # ruff check + format check
make lint-frontend   # eslint src
```

**Database**
```bash
make db-auth         # gcloud login + application-default + set project (once per machine)
make db-proxy        # start Cloud SQL proxy in foreground (separate terminal)
make db-psql         # open psql shell
make db-apply FILE=scripts/db/001_schema.sql   # apply a SQL schema file
```

**Versioning**
```bash
make version         # print current version
make version-patch   # bump patch in backend + frontend, commit
make version-minor   # bump minor in backend + frontend, commit
make version-major   # bump major in backend + frontend, commit
```

---

## Configuration

All configurable ports and environment selectors are defined in `.env` (created from `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV_FOR_DYNACONF` | `development` | Active section in `backend/settings.toml` — one per developer/machine |
| `DEPLOY_ENV` | `docker` | Active section in `backend/deploy.toml` — used by docker-compose |
| `BACKEND_PORT` | `8000` | Port uvicorn listens on |
| `BACKEND_HOST_PORT` | `8001` | Host-side port when running via Docker |
| `VITE_PORT` | `5173` | Port Vite dev server listens on |
| `FRONTEND_HOST_PORT` | `5174` | Host-side port when running via Docker |
| `PGPORT` | `5435` | Proxy local port (psql / make db-*) |
| `PGDATABASE` | `appdb` | Database name (psql / make db-*) |
| `PGUSER` | `app` | Database user (psql / make db-*) |
| `PGPASSWORD` | — | Database password — never commit |

Backend config is split across two files loaded by dynaconf simultaneously:
- `backend/settings.toml` — local dev environments, one `[section]` per developer/machine + `[testing]`
- `backend/deploy.toml` — deployment targets: `[docker]`, `[ci]`, `[production]`
- `backend/.secrets.toml` — passwords and API keys (gitignored)

`ENV_FOR_DYNACONF` selects the active `[section]` across both files. Each file only defines sections relevant to its concern — dynaconf silently skips files where the active section doesn't exist, so there's no bleed between dev and deployment config.

`DEPLOY_ENV` is not a dynaconf variable. docker-compose maps it to `ENV_FOR_DYNACONF` inside the container (`ENV_FOR_DYNACONF=${DEPLOY_ENV:-docker}`), letting you control local dev and container target independently from `.env`.

---

## Using with Claude Code

1. Run `make dev` so both servers are up
2. Open the repo in Claude Code
3. Describe your project in plain English:

   > *"This is a task management app for small teams. Users can create boards, add cards, and assign them to team members."*

4. Claude reads `CLAUDE.md` and builds the real implementation — routers, services, Pydantic models, tests, pages, hooks, components.

**Slash commands** (type `/` in Claude Code):

| Command | What it does |
|---------|-------------|
| `/new-feature <name>` | Scaffolds a full backend vertical slice: router, service, Pydantic models, pytest tests |
| `/new-page <name>` | Scaffolds a frontend page: MUI layout, TanStack Query hook, loading/empty/error states |
| `/ui-review` | Screenshots the running UI, compares against `UIDesignGuidelines.md`, applies fixes |

**Once the real app takes shape:**
- Replace `HomePage` in `frontend/src/pages/HomePage.tsx` with your real landing page
- Remove or keep `HealthPage` at `/health` — it's useful as a system status page

---

## Project Structure

```
backend/
  src/app/
    main.py          # FastAPI app, CORS, router registration
    config.py        # dynaconf settings
    routers/
      domain/        # REST resources → /api/v1/<resource>
      bff/           # Client-specific composition → /api/bff/<client>
    services/        # Business logic (no FastAPI dependencies)
    models/
      requests/      # Pydantic request bodies
      responses/     # Pydantic response models
  tests/
frontend/
  src/
    api/             # TanStack Query hooks (server state)
    components/      # common/ + domain-scoped components
    pages/           # Route-level components
    store/           # Zustand (UI state only)
    theme/           # MUI theme config
    types/
  e2e/               # Playwright tests
scripts/             # dev / test / lint / db helpers
```

See `CLAUDE.md` for the full conventions and architectural rules.

---

## Database

The template uses **async SQLAlchemy + asyncpg** connecting via **Cloud SQL proxy** (runs on `127.0.0.1:5435` locally, `127.0.0.1:5432` as a Cloud Run sidecar). No ORM — schemas are plain `.sql` files in `scripts/db/`.

**Using the database in a router:**

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services import my_service

async def my_endpoint(db: Annotated[AsyncSession, Depends(get_db)]):
    return await my_service.fetch_data(db)
```

**Daily workflow:**

```bash
make db-auth     # once per machine / when token expires
make db-proxy    # terminal 1 — keep running
make db-psql     # terminal 2 — interactive shell
make db-apply FILE=scripts/db/001_schema.sql   # apply a schema file
```

See [README_SETUP.md](README_SETUP.md) for first-time installation of gcloud, cloud-sql-proxy, and psql.
