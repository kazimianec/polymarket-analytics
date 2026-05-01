#!/bin/bash
# Per-app/per-repo GCP setup.
# Run this for each new repo that deploys to shared-infra-prod-490809.
# Prerequisites: gcp-setup-once.sh must have been run first.
set -euo pipefail

PROJECT=shared-infra-prod-490809
REGION=europe-west1
AR_REPO=cloud-run-images

# ── Required arguments ────────────────────────────────────────────────────────
GITHUB_REPO="${1:-}"      # e.g. kazimianec/my-new-app
SECRET_NAME="${2:-}"      # e.g. my-app-pg-password

if [[ -z "$GITHUB_REPO" || -z "$SECRET_NAME" ]]; then
  echo "Usage: $0 <github-org/repo> <secret-name>"
  echo "Example: $0 kazimianec/my-new-app my-app-pg-password"
  exit 1
fi

SA_EMAIL="github-deploy@${PROJECT}.iam.gserviceaccount.com"

echo "==> Setting default project"
gcloud config set project "$PROJECT"

POOL_ID=$(gcloud iam workload-identity-pools describe github-pool \
  --location=global \
  --format="value(name)")

PROVIDER_ID=$(gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --format="value(name)")

echo "==> Binding repo '${GITHUB_REPO}' to deploy service account"
# This is the only GCP step needed per new repo.
# The WIF provider already allows all repos in the org (set in gcp-setup-once.sh).
# This binding controls which specific repo can impersonate the SA.
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_REPO}"

echo "==> Creating secret '${SECRET_NAME}'"
gcloud secrets create "$SECRET_NAME" \
  --replication-policy=automatic \
  || echo "  (already exists, skipping)"
echo "  Set value with:"
echo "  echo -n 'YOUR_PASSWORD' | gcloud secrets versions add ${SECRET_NAME} --data-file=-"

echo "==> Granting Cloud Run runtime SA access to secret"
# The Cloud Run runtime SA (default Compute Engine SA) reads the secret at container startup.
# The deploy SA configures the service to use the secret, but the runtime SA is what actually reads it.
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT" --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud secrets add-iam-policy-binding "$SECRET_NAME" \
  --member="serviceAccount:${COMPUTE_SA}" \
  --role=roles/secretmanager.secretAccessor

echo ""
echo "==========================================="
echo "Per-app setup complete for: ${GITHUB_REPO}"
echo ""
echo "Configure these in GitHub → Settings → Secrets and variables → Actions"
echo "for the repo: ${GITHUB_REPO}"
echo ""
echo "── Secrets (sensitive) ──"
echo "GCP_WIF_PROVIDER  = ${PROVIDER_ID}"
echo "GCP_SA_EMAIL      = ${SA_EMAIL}"
echo "CLOUDSQL_INSTANCE = ${PROJECT}:${REGION}:<instance-name>  ← fill in instance name"
echo ""
echo "── Variables (non-sensitive) ──"
echo "GCP_PROJECT_ID = ${PROJECT}"
echo "GCP_REGION     = ${REGION}"
echo "GCP_AR_REPO    = ${AR_REPO}"
echo ""
echo "Also update your workflow's service names if different from the defaults:"
echo "  fullstack-backend  → your-app-backend"
echo "  fullstack-frontend → your-app-frontend"
echo "==========================================="
