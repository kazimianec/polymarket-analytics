# New Project Setup

Instructions for creating a new project from this template.

---

## Prerequisites

- [pyenv](https://github.com/pyenv/pyenv) + Python 3.12 (`pyenv install 3.12`)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Node.js 22+](https://nodejs.org/) + npm
- `make`
- `lsof` — used by `make stop` and `make docker-rebuild` to find processes by port. Built-in on macOS. On Linux/WSL: `sudo apt-get install -y lsof`
- For database access: `gcloud` CLI, `cloud-sql-proxy`, `psql` (see [Database Tools](#database-tools) below)

---

## Quickstart

```bash
# 1. Create a new repo from this template
# Go to https://github.com/kazimianec/fullstack-template, click "Use this template",
# then go to the new repo, click "Code", copy the clone URL, and clone it:
git clone <your-repo-url> my-project
cd my-project
# Or use the GitHub CLI:
# gh repo create my-project --template kazimianec/fullstack-template --clone
# cd my-project

# 2. Rename the backend package (so Poetry creates a unique virtualenv)
# In backend/pyproject.toml, find the line:
#   name = "fullstack-template"
# and change it to:
#   name = "my-project"
# Or use sed:
# macOS:
sed -i '' 's/name = "fullstack-template"/name = "my-project"/' backend/pyproject.toml
# Linux:
sed -i 's/name = "fullstack-template"/name = "my-project"/' backend/pyproject.toml

# 3. IMPORTANT: Set the env var prefix for dynaconf (avoids conflicts if you
#    run multiple projects built from this template in the same shell or CI)
# In backend/src/app/config.py, find the line:
#   envvar_prefix="APP"
# and change it to:
#   envvar_prefix="MY_PROJECT"  (use your project name, uppercase)
# This prefix namespaces all backend env vars, e.g. MY_PROJECT_DATABASE_URL
# in .env or CI maps to settings.database_url in code.
# Or use sed:
# macOS:
sed -i '' 's/envvar_prefix="APP"/envvar_prefix="MY_PROJECT"/' backend/src/app/config.py
# Linux:
sed -i 's/envvar_prefix="APP"/envvar_prefix="MY_PROJECT"/' backend/src/app/config.py

# 4. Set up environment
pyenv local 3.12
cp .env.example .env
# Edit .env to set your local environment and change default ports if needed

# 5. Install dependencies
cd backend && poetry install && cd ..
cd frontend && npm install && cd ..

# 6. Start dev servers
make dev
```

Open `http://localhost:5173/health` to confirm everything is running (port from `VITE_PORT` in `.env`).

> **Team setup reminder:** update `pg_db`, `pg_user`, and `pg_password` to match your actual database in `backend/settings.toml` (dev sections), `backend/deploy.toml` (deployment targets), `backend/.secrets.toml` (passwords), and `.env` (`PGDATABASE`, `PGUSER`, `PGPASSWORD` for psql tooling). The template ships with placeholder values — every team member needs to fill these in locally.

---

## Claude Auto Review Setup

This template includes a GitHub Actions workflow that automatically posts an AI code review on every pull request. You must add one secret to each new repo for it to work.

1. Run locally to generate a token (requires Claude Pro or Max):
   ```bash
   claude setup-token
   ```
2. In your new repo on GitHub: **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `CLAUDE_CODE_OAUTH_TOKEN`
   - Value: paste the token from step 1

> If you're on a Team or Enterprise plan, use `ANTHROPIC_API_KEY` instead and update the workflow's `claude_code_oauth_token:` field to `anthropic_api_key:`.

---

## Environment Configuration

Configuration is split across three files in `backend/`:

| File | Purpose | Committed? |
|------|---------|-----------|
| `settings.toml` | Local dev environments — one `[section]` per developer/machine, plus `[testing]` | ✅ Yes |
| `deploy.toml` | Deployment targets — `[docker]`, `[ci]`, `[production]` | ✅ Yes |
| `.secrets.toml` | Passwords and API keys | ❌ No (gitignored) |

Copy the example secrets file and fill in values:

```bash
cp backend/.secrets.toml.example backend/.secrets.toml
```

Two variables in `.env` control which sections are active:

```
# Local dev server (make dev) — pick your section in settings.toml
ENV_FOR_DYNACONF=dev_ak_mac

# Docker-compose target (make docker-up) — pick your section in deploy.toml
DEPLOY_ENV=docker
```

To add your own developer environment, add a `[dev_yourname]` section to `settings.toml` and set `ENV_FOR_DYNACONF=dev_yourname` in your `.env`.

> `.secrets.toml` and `.env` are gitignored — never commit secrets.

---

## Database Tools

Install these once per machine. They are needed to run the Cloud SQL proxy and connect via psql.

### 1. gcloud CLI

**macOS**
```bash
brew install --cask google-cloud-sdk
```

**Linux / WSL (Ubuntu)**
```bash
sudo apt-get install -y apt-transport-https ca-certificates gnupg curl
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" \
  | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install -y google-cloud-cli
```

After installing, authenticate:

```bash
gcloud auth application-default login
```

> On WSL, the browser will open on the Windows side. Complete login there; the token is written back into WSL automatically.

To update:

```bash
# macOS
gcloud components update

# Linux / WSL
sudo apt-get update && sudo apt-get upgrade google-cloud-cli
```

### 2. cloud-sql-proxy

**macOS**
```bash
brew install cloud-sql-proxy
```

**Linux / WSL (Ubuntu, x86-64)**
```bash
curl -o cloud-sql-proxy https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.15.2/cloud-sql-proxy.linux.amd64
chmod +x cloud-sql-proxy
sudo mv cloud-sql-proxy /usr/local/bin/
```

> Check for the latest version at https://github.com/GoogleCloudPlatform/cloud-sql-proxy/releases

To update:

```bash
# macOS
brew upgrade cloud-sql-proxy

# Linux / WSL — re-run the curl commands above with the new version number
```

### 3. psql

**macOS** — installs the client only, no server:
```bash
brew install libpq
brew link --force libpq
```

**Linux / WSL (Ubuntu)**
```bash
sudo apt-get install -y postgresql-client
```

To update:

```bash
# macOS
brew upgrade libpq

# Linux / WSL
sudo apt-get update && sudo apt-get upgrade postgresql-client
```

### 4. Start the proxy

Run this in a separate terminal before connecting to the database:

```bash
cloud-sql-proxy shared-infra-prod-490809:europe-west1:main-postgres-dev --port 5435
```

### 5. Configure credentials

Add your database password to `backend/.secrets.toml`:

```toml
[dev_ak_mac]     # macOS — or [dev_ak_linux] for Linux / WSL
pg_password = "..."   # password for cities_ro / cities_dba / postgres
```

Add the matching variables to `.env` for `make db-psql` / `make db-apply`:

```
PGPORT=5435
PGDATABASE=cities
PGUSER=cities_dba
PGPASSWORD=...
```

### 6. Verify

With the proxy running:

```bash
make db-psql   # should open an interactive psql shell
```

---

## Next Steps

Once your project is set up, see [README.md](README.md) for day-to-day development workflows, commands, and Docker usage.
