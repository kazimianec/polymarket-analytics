.PHONY: dev dev-backend dev-frontend docker-up docker-down docker-rebuild stop stop-all test-backend test-frontend lint-backend lint-frontend version version-patch version-minor version-major db-psql db-apply db-proxy db-auth deploy

-include .env
export

BACKEND_PORT      ?= 8000
BACKEND_HOST_PORT ?= 8001
VITE_PORT         ?= 5173
FRONTEND_HOST_PORT ?= 5174

# Cloud SQL proxy instance — override via .env
CLOUDSQL_INSTANCE ?= shared-infra-prod-490809:europe-west1:main-postgres-dev

# Standard PostgreSQL env vars for Make / psql tooling.
# psql reads these automatically — no explicit -h/-p/-U flags needed.
# Using PG* (not APP_PG_*) so dynaconf does not pick them up.
# The application reads its DB config from backend/settings.toml + .secrets.toml.
# Shared-infra users: cities_ro (read-only app), cities_dba (read-write), postgres (superuser)
PGHOST     ?= 127.0.0.1
PGPORT     ?= 5435
PGDATABASE ?= cities
PGUSER     ?= cities_dba

# Start backend + frontend concurrently
dev:
	@echo "Starting backend and frontend..."
	@echo "  App:    http://localhost:$(VITE_PORT)"
	@echo "  Health: http://localhost:$(VITE_PORT)/health"
	@echo "  API:    http://localhost:$(BACKEND_PORT)/docs"
	@trap 'kill 0' SIGINT; \
	make dev-backend & \
	make dev-frontend & \
	wait

# Kill host processes on BACKEND_PORT and VITE_PORT (make dev / make dev-backend / make dev-frontend)
# Does NOT affect Docker containers — use make docker-down for that
stop:
	@echo "Stopping local dev processes..."
	@PIDS=$$(lsof -ti:$(BACKEND_PORT) 2>/dev/null; lsof -ti:$(VITE_PORT) 2>/dev/null); \
	if [ -n "$$PIDS" ]; then \
	  echo "$$PIDS" | sort -u | xargs kill && echo "  Stopped" || echo "  Failed to kill some processes"; \
	else echo "  Nothing running"; fi

# Stop Docker containers (make docker-up / make docker-rebuild)
# Does NOT affect host dev processes — use make stop for that
docker-down:
	docker compose down

# Stop host dev processes, Docker containers, and Cloud SQL proxy
stop-all: stop docker-down
	@echo "Stopping Cloud SQL proxy..."
	@PIDS=$$(lsof -ti:$(PGPORT) 2>/dev/null); \
	if [ -n "$$PIDS" ]; then \
	  echo "$$PIDS" | sort -u | xargs kill && echo "  Stopped" || echo "  Failed to kill proxy"; \
	else echo "  Proxy not running"; fi

# Stop host dev processes and containers, rebuild images, and start fresh
# Preserves the Cloud SQL proxy — use make stop-all to kill everything
docker-rebuild: stop docker-down
	docker compose build
	@echo ""
	@echo "Starting containers — will be available at:"
	@echo "  App:    http://localhost:$(FRONTEND_HOST_PORT)"
	@echo "  Health: http://localhost:$(FRONTEND_HOST_PORT)/health"
	@echo "  API:    http://localhost:$(BACKEND_HOST_PORT)/docs"
	@echo ""
	docker compose up

# Build images and start containers — does not stop/remove containers first; may be a no-op if already running
# For a guaranteed clean start (stop + rebuild + restart) use make docker-rebuild
docker-up:
	docker compose build
	@echo ""
	@echo "Starting containers — will be available at:"
	@echo "  App:    http://localhost:$(FRONTEND_HOST_PORT)"
	@echo "  Health: http://localhost:$(FRONTEND_HOST_PORT)/health"
	@echo "  API:    http://localhost:$(BACKEND_HOST_PORT)/docs"
	@echo ""
	docker compose up

# Run backend dev server with hot reload
dev-backend:
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port $(BACKEND_PORT)

# Run frontend dev server
dev-frontend:
	cd frontend && npm run dev

# Run backend pytest suite
test-backend:
	cd backend && poetry run pytest

# Run frontend Playwright tests
test-frontend:
	cd frontend && npx playwright test

# Lint and format-check backend with ruff
lint-backend:
	cd backend && poetry run ruff check . && poetry run ruff format --check .

# Lint frontend with eslint
lint-frontend:
	cd frontend && npx eslint src

# ── Database ──────────────────────────────────────────────────────────────────

# Authenticate with Google Cloud (run once per machine or when token expires)
# login: authenticates the gcloud CLI; application-default: used by cloud-sql-proxy and SDKs
GCLOUD_PROJECT ?= shared-infra-prod-490809
db-auth:
	gcloud auth login
	gcloud auth application-default login
	gcloud config set project $(GCLOUD_PROJECT)

# Start Cloud SQL proxy in the foreground (run in a separate terminal)
db-proxy:
	cloud-sql-proxy $(CLOUDSQL_INSTANCE) --port $(PGPORT)

# Open an interactive psql shell (PG* vars from .env are read automatically)
db-psql:
	psql

# Apply a SQL file — usage: make db-apply FILE=scripts/db/001_schema.sql
db-apply:
	@test -n "$(FILE)" || (echo "Usage: make db-apply FILE=scripts/db/001_schema.sql"; exit 1)
	psql -f "$(FILE)"

# ── Deploy ────────────────────────────────────────────────────────────────────

# Trigger Cloud Run deployment by pushing current HEAD to deploy-gcloud branch
deploy:
	git push --force-with-lease origin HEAD:deploy-gcloud

# ── Versioning ────────────────────────────────────────────────────────────────

# Print current version
version:
	@cd backend && poetry version --short

# Bump patch version and commit
version-patch:
	cd backend && poetry version patch
	cd frontend && npm version patch --no-git-tag-version
	@NEW_VERSION=$$(cd backend && poetry version --short) && \
	  git add backend/pyproject.toml frontend/package.json frontend/package-lock.json && \
	  git commit -m "chore: bump version to v$$NEW_VERSION"

# Bump minor version and commit
version-minor:
	cd backend && poetry version minor
	cd frontend && npm version minor --no-git-tag-version
	@NEW_VERSION=$$(cd backend && poetry version --short) && \
	  git add backend/pyproject.toml frontend/package.json frontend/package-lock.json && \
	  git commit -m "chore: bump version to v$$NEW_VERSION"

# Bump major version and commit
version-major:
	cd backend && poetry version major
	cd frontend && npm version major --no-git-tag-version
	@NEW_VERSION=$$(cd backend && poetry version --short) && \
	  git add backend/pyproject.toml frontend/package.json frontend/package-lock.json && \
	  git commit -m "chore: bump version to v$$NEW_VERSION"
