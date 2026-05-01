# Cloud Run Deployment Pipeline

## Context

The app runs in Docker containers locally. We need a GitHub Actions pipeline to deploy both services (backend + frontend) to Google Cloud Run, triggered by pushing to a `deploy-gcloud` branch. All GCP resources (Cloud SQL, Cloud Run, Artifact Registry, Secret Manager) live in a single project: `shared-infra-prod-490809`. Auth via Workload Identity Federation.

### Key concepts

- **Cloud Run** — Google's serverless container platform. You give it a Docker image, it runs it and gives you a URL. Scales to zero when idle, scales up on traffic. No servers to manage.
- **Artifact Registry** — Google's private Docker Hub. Stores our built images. Cloud Run pulls from it during deploy. Same GCP network = fast pulls, no egress cost.
- **Workload Identity Federation (WIF)** — Lets GitHub Actions authenticate with GCP without storing service account keys. GitHub proves its identity via an OIDC token, GCP exchanges it for short-lived credentials. More secure than static JSON keys.
- **Cloud SQL Auth Proxy** — A sidecar that runs alongside the backend in Cloud Run. It creates a Unix domain socket at `/cloudsql/INSTANCE` — the app connects via that socket, not TCP. No VPC peering or SSH needed.
- **Secret Manager** — GCP's secrets vault. Stores `pg_password` securely. Cloud Run mounts it as an env var at runtime, so the secret never appears in code, images, or GitHub.

### GCP project layout

```
shared-infra-prod-490809          ← everything lives here (demos/small projects)
  ├─ Cloud SQL (Postgres)
  │   └─ DB: cities
  ├─ Artifact Registry repo       ← stores Docker images for all apps
  ├─ Cloud Run: fullstack-backend
  ├─ Cloud Run: fullstack-frontend
  └─ Secret Manager               ← runtime secrets (pg_password, etc.)
```

Single-project layout: Cloud Run, Artifact Registry, Cloud SQL, and Secret Manager all
live in the same project. No cross-project IAM grants needed — the Auth Proxy sidecar
connects to Cloud SQL within the same project without extra wiring.

## Architecture

```
Developer runs: make deploy (or git push --force-with-lease origin HEAD:deploy-gcloud)
  │
  ▼
GitHub Actions workflow (.github/workflows/deploy-gcloud.yml)
  │
  ├─ 1. Authenticate with GCP via WIF (no stored keys)
  │     GitHub OIDC token → GCP short-lived credentials
  │
  ├─ 2. Build Docker images and push to Artifact Registry
  │     backend:$SHA  → europe-west1-docker.pkg.dev/shared-infra-prod-490809/cloud-run-images/backend:sha
  │     frontend:$SHA → europe-west1-docker.pkg.dev/shared-infra-prod-490809/cloud-run-images/frontend:sha
  │
  ├─ 3. Deploy backend to Cloud Run
  │     - Cloud SQL Auth Proxy sidecar via --add-cloudsql-instances
  │     - Proxy creates Unix socket at /cloudsql/INSTANCE (not TCP)
  │     - backend connects via socket path set in deploy.toml [production]
  │     - --port=8000 tells Cloud Run which port uvicorn listens on
  │     - APP_CORS_ORIGINS=[] seeds an empty list so the app starts before
  │       the frontend URL is known (overwritten in step 5)
  │     - APP_PG_PASSWORD injected from Secret Manager at runtime
  │     → outputs: backend URL (e.g. https://fullstack-backend-xxxxx.run.app)
  │
  ├─ 4. Deploy frontend to Cloud Run
  │     - nginx serves static build from dist/
  │     - nginx proxies /api/* to backend URL (from step 3)
  │     - BACKEND_URL env var injected into nginx config at container start
  │     → outputs: frontend URL (e.g. https://fullstack-frontend-xxxxx.run.app)
  │
  └─ 5. Update backend CORS
        - Sets APP_CORS_ORIGINS=["<frontend-url>"] (JSON array — dynaconf parses as list)
        - Resolves circular dependency: backend needs frontend URL for CORS,
          but frontend needs backend URL for proxying
```

---

## Files Created/Modified

### 1. `backend/Dockerfile` — no changes needed

`poetry install` (without `--no-root`) installs the package itself, making `app` importable without `PYTHONPATH`. Verified working locally and in Cloud Run.

### 2. `backend/deploy.toml` — modified

In `[production]` section:
- `pg_host = "/cloudsql/shared-infra-prod-490809:europe-west1:main-postgres-dev"` — Unix socket path for Cloud SQL Auth Proxy (not TCP)
- `pg_db = "cities"` — was missing, causing fallback to `"appdb"` default

### 3. `backend/src/app/database.py` — modified

`_build_database_url()` detects if `pg_host` starts with `/` and builds a Unix socket URL using asyncpg's `host` query parameter instead of TCP host/port. Local dev is unaffected (still uses TCP via `127.0.0.1`).

### 4. `frontend/Dockerfile.prod` — created

Multi-stage production Dockerfile. Separate from dev `Dockerfile` so `docker-compose` keeps working as-is.

- **Stage 1 (build):** `node:22-slim` → `npm ci` → `npm run build` → produces `dist/`
- **Stage 2 (serve):** `nginx:1.27-alpine` → copies `dist/`, nginx template, entrypoint
- **Port 8080** — Cloud Run's default port for frontend

### 5. `frontend/nginx.conf.template` — created

nginx config with `${BACKEND_URL}` placeholder substituted at container startup.

- `proxy_http_version 1.1` + `Connection ""` — enables keepalive to backend
- `proxy_set_header Host $proxy_host` — sends backend's hostname (not frontend's) so Cloud Run routes correctly
- `location /api/` → reverse proxy to `${BACKEND_URL}`
- `location /` → SPA fallback (`try_files $uri $uri/ /index.html`) for React Router

### 6. `frontend/docker-entrypoint.sh` — created

- Guards `BACKEND_URL` with `: "${BACKEND_URL:?BACKEND_URL is required}"` — fails fast with clear error
- `envsubst '${BACKEND_URL}'` — explicit variable list prevents nginx's own `$host`, `$uri` etc. from being clobbered
- `exec nginx -g 'daemon off;'`

### 7. `frontend/.dockerignore` — created

Excludes `node_modules`, `dist`, `.env` from Docker build context.

### 8. `.github/workflows/deploy-gcloud.yml` — created

Trigger: `push` to `deploy-gcloud` branch. Service names (`BACKEND_SERVICE`, `FRONTEND_SERVICE`) defined as top-level env vars for easy templating.

### 9. `Makefile` — modified

`make deploy` → `git push --force-with-lease origin HEAD:deploy-gcloud`
(`--force-with-lease` is correct: `deploy-gcloud` is a trigger branch, not a development branch)

### 10. `scripts/deploy/gcp-setup-once.sh` — created

Run once as project owner. Never repeated for new apps or repos.

What it does (all in `shared-infra-prod-490809`):
- Enable APIs — Cloud Run, Artifact Registry, IAM, Secret Manager, Cloud SQL Admin
- Create Artifact Registry repo — `cloud-run-images`, Docker, `europe-west1`
- Create WIF pool + OIDC provider — org-level condition (`repository_owner=='kazimianec'`)
- Create deploy SA — `github-deploy@...` with roles: `run.admin`, `artifactregistry.writer`, `secretmanager.secretAccessor`, `cloudsql.client`
- Grant `roles/iam.serviceAccountUser` on the default Compute Engine SA — required for the deploy SA to create/update Cloud Run services (which use the Compute SA as runtime identity)

### 11. `scripts/deploy/gcp-setup-per-app.sh` — created

Run for each new repo/app: `./gcp-setup-per-app.sh kazimianec/my-new-app my-app-pg-password`

What it does:
- Bind repo to deploy SA via WIF (`principalSet` with `attribute.repository`) — one `gcloud` command
- Create app secret in Secret Manager
- Grant `roles/secretmanager.secretAccessor` on the secret to the default Compute Engine SA (the Cloud Run runtime identity that actually reads the secret at container startup)
- Print GitHub secrets/variables to configure

---

## IAM — Three Service Accounts Involved

This is the most confusing part. There are three distinct identities:

| SA | Who | Needs |
|----|-----|-------|
| `github-deploy@...` | Runs the GitHub Actions workflow | `run.admin`, `artifactregistry.writer`, `secretmanager.secretAccessor`, `cloudsql.client`, `iam.serviceAccountUser` on Compute SA |
| `127051910492-compute@developer.gserviceaccount.com` | Cloud Run runtime identity (default Compute SA) | `secretmanager.secretAccessor` on each secret it reads at container startup |
| WIF principal | GitHub Actions OIDC token | `iam.workloadIdentityUser` on deploy SA (set by per-repo `principalSet` binding) |

The `iam.serviceAccountUser` grant is needed because when Cloud Run creates a new service revision, GCP requires the caller (deploy SA) to prove it can act as the runtime SA.

---

## Key Design Decisions

1. **Separate `Dockerfile.prod`** — keeps dev `docker-compose` workflow untouched. No risk of breaking local development.
2. **Deploy order: backend → frontend → update CORS** — resolves the circular URL dependency. Backend needs frontend URL for CORS; frontend needs backend URL for proxying. Three-step deploy handles both.
3. **`APP_CORS_ORIGINS=[]` seed** — `get_cors_origins()` raises `RuntimeError` if cors_origins is completely absent. Seeding an empty list lets the app start; the CORS update step overwrites it with the real frontend URL.
4. **Single GCP project** — all resources in `shared-infra-prod-490809`. Eliminates cross-project IAM grants. Right-sized for demos and small projects.
5. **Unix socket for Cloud SQL** — Cloud Run's `--add-cloudsql-instances` creates a Unix domain socket, not a TCP listener. `database.py` detects `pg_host` starting with `/` and builds the asyncpg connection URL accordingly.
6. **`APP_CORS_ORIGINS` as JSON array** — dynaconf parses env vars as strings unless they look like JSON. `["https://..."]` is parsed as `list[str]`; a plain URL string would be iterated character by character by `tuple()`.
7. **`envsubst` with explicit var list** — prevents nginx's own `$host`, `$uri` etc. from being clobbered.
8. **Image tags = git SHA** — every deploy is traceable to an exact commit.

---

## Live URLs

- **Frontend:** https://fullstack-frontend-mxcbhoy6iq-ew.a.run.app
- **Backend API:** https://fullstack-backend-mxcbhoy6iq-ew.a.run.app/docs
- **Health (direct):** https://fullstack-backend-mxcbhoy6iq-ew.a.run.app/api/v1/health
- **Health (via proxy):** https://fullstack-frontend-mxcbhoy6iq-ew.a.run.app/api/v1/health

---

## Verification

1. **Local build test:** `docker build backend/` and `docker build -f frontend/Dockerfile.prod frontend/` should succeed
2. **GCP setup (once):** Run `scripts/deploy/gcp-setup-once.sh` as project owner
3. **Per-app setup:** Run `scripts/deploy/gcp-setup-per-app.sh kazimianec/fullstack-template pg-password`, set secret value, configure GitHub secrets/variables
4. **Trigger deploy:** `make deploy`
5. **Check workflow:** GitHub → Actions tab → "Deploy to Cloud Run" → all steps green
6. **Smoke test:** `curl https://fullstack-backend-mxcbhoy6iq-ew.a.run.app/api/v1/health` → `{"status":"ok"}`
7. **Cross-service proxy:** `curl https://fullstack-frontend-mxcbhoy6iq-ew.a.run.app/api/v1/health` → same response via nginx
