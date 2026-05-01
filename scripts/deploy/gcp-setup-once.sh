#!/bin/bash
# One-time GCP setup for the shared-infra-prod-490809 project.
# Run once as a project owner — never needs repeating for new apps or repos.
# For per-app/per-repo setup, run gcp-setup-per-app.sh instead.
set -euo pipefail

PROJECT=shared-infra-prod-490809
REGION=europe-west1
AR_REPO=cloud-run-images
SA_NAME=github-deploy
SA_EMAIL="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
GITHUB_ORG=kazimianec   # GitHub org or username — all repos under this org are allowed

echo "==> Setting default project"
gcloud config set project "$PROJECT"

echo "==> Enabling APIs"
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  secretmanager.googleapis.com \
  sqladmin.googleapis.com

echo "==> Creating Artifact Registry repo (Docker, ${REGION})"
gcloud artifacts repositories create "$AR_REPO" \
  --repository-format=docker \
  --location="$REGION" \
  --description="Cloud Run images for all apps" \
  || echo "  (already exists, skipping)"

echo "==> Creating deploy service account"
gcloud iam service-accounts create "$SA_NAME" \
  --display-name="GitHub Actions deploy" \
  || echo "  (already exists, skipping)"

echo "==> Granting roles to service account"
for ROLE in roles/run.admin roles/artifactregistry.writer roles/secretmanager.secretAccessor roles/cloudsql.client; do
  gcloud projects add-iam-policy-binding "$PROJECT" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="$ROLE" \
    --condition=None \
    --quiet
done

echo "==> Granting actAs on default Compute Engine SA (required to deploy Cloud Run services)"
# Cloud Run uses the default Compute Engine SA as the runtime identity for new services.
# The deploy SA needs iam.serviceAccountUser on it to be allowed to create/update services.
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT" --format="value(projectNumber)")
COMPUTE_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud iam service-accounts add-iam-policy-binding "$COMPUTE_SA" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role=roles/iam.serviceAccountUser

echo "==> Creating Workload Identity pool"
gcloud iam workload-identity-pools create github-pool \
  --location=global \
  --display-name="GitHub Actions pool" \
  || echo "  (already exists, skipping)"

echo "==> Creating OIDC provider scoped to org: ${GITHUB_ORG}"
# Condition is org-level — individual repo access is controlled by per-repo SA bindings
# (see gcp-setup-per-app.sh). This means adding a new repo never requires touching the provider.
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner" \
  --attribute-condition="attribute.repository_owner=='${GITHUB_ORG}'" \
  || echo "  (already exists, skipping)"

POOL_ID=$(gcloud iam workload-identity-pools describe github-pool \
  --location=global \
  --format="value(name)")

PROVIDER_ID=$(gcloud iam workload-identity-pools providers describe github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --format="value(name)")

echo ""
echo "==========================================="
echo "One-time setup complete."
echo ""
echo "These values are needed when running gcp-setup-per-app.sh:"
echo "  POOL_ID      = ${POOL_ID}"
echo "  PROVIDER_ID  = ${PROVIDER_ID}"
echo "  SA_EMAIL     = ${SA_EMAIL}"
echo ""
echo "GitHub variables (non-sensitive) — same for every repo using this project:"
echo "  GCP_PROJECT_ID = ${PROJECT}"
echo "  GCP_REGION     = ${REGION}"
echo "  GCP_AR_REPO    = ${AR_REPO}"
echo "==========================================="
