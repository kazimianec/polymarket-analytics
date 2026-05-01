# GCloud & Cloud Run — Quick Notes

## Workload Identity Federation (WIF)
- Trust bridge between GitHub Actions and GCP — no stored service account keys
- GitHub proves identity via OIDC token, GCP exchanges it for short-lived credentials
- One WIF pool can serve multiple repos — configured per deploy project, not per app
- Provider condition is org-level (`repository_owner=='kazimianec'`) — adding a new repo never requires touching the provider
- Per-repo access is controlled by SA bindings (`principalSet` with `attribute.repository`)
- Developers don't need GCP access to deploy — just push to `deploy-gcloud` branch

## Secret Manager
- GCP's vault for runtime secrets (DB passwords, API keys)
- Cloud Run injects secrets as env vars at container start — value never in code or images
- Two SAs need access: the deploy SA (to configure the service) and the Compute Engine runtime SA (to read the secret at container startup) — grant per-secret in `gcp-setup-per-app.sh`
- GitHub Secrets = build time (CI); Secret Manager = runtime (containers)

## Artifact Registry
- GCP's private Docker Hub — stores built images, Cloud Run pulls from it
- One repo can store images for all apps
- Same GCP network = fast pulls, no egress cost

## Cloud SQL Auth Proxy
- When using `--add-cloudsql-instances` in Cloud Run, the proxy creates a **Unix domain socket** at `/cloudsql/PROJECT:REGION:INSTANCE` — it does NOT listen on TCP
- The app must connect via the socket path, not `127.0.0.1:5432`
- In `database.py`: detect `pg_host` starting with `/` and use asyncpg's `host` query parameter
- In `deploy.toml [production]`: set `pg_host = "/cloudsql/PROJECT:REGION:INSTANCE"`
- Local dev still uses TCP (`127.0.0.1`) via the separately run `cloud-sql-proxy --port 5435`

## IAM Gotchas
- Deploy SA needs `iam.serviceAccountUser` on the default Compute Engine SA (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`) — required to create/update Cloud Run services
- Cloud Run runtime SA (default Compute SA) needs `secretmanager.secretAccessor` on each secret it reads — separate from the deploy SA's access
- Both grants are easy to miss and cause cryptic errors at deploy time

## GCP Projects Layout
- Single project (`shared-infra-prod-490809`): Cloud SQL, Cloud Run, Artifact Registry, Secret Manager — all resources for all apps
- Right-sized for demos and small projects — no cross-project IAM grants needed
- If projects multiply or teams diverge, split into infra + deploy projects then

## One-time vs Per-app Setup
- **One-time:** APIs, Artifact Registry, WIF pool + provider, deploy SA + roles, Compute SA actAs grant
- **Per-app:** WIF SA binding for the repo, Secret Manager entry + per-secret IAM for runtime SA, GitHub secrets/variables, deploy.toml `pg_host` socket path

## CORS + dynaconf
- dynaconf parses env var values as JSON if they look like JSON, otherwise as string
- `APP_CORS_ORIGINS=https://example.com` → `str` → `tuple()` iterates characters → broken
- `APP_CORS_ORIGINS=["https://example.com"]` → `list[str]` → correct
- On first deploy, seed `APP_CORS_ORIGINS=[]` in the backend deploy step so the app starts before the frontend URL is known; overwrite with the real URL in the CORS update step

## GCloud CLI
- Communicates over HTTPS (REST/gRPC) — no SSH
- `--project=X` overrides default project — no need to switch constantly
- `gcloud config configurations` for named project profiles if needed
