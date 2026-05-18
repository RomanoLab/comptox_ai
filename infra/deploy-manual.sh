#!/usr/bin/env bash
# Manual deploy from your laptop to the EC2 app host.
# Use this until the OIDC + GitHub Actions deploy role exist and
# .github/workflows/deploy.yml can run.
#
# Prereqs:
#   - publish-images.yml has finished pushing sha-<commit> tags to GHCR
#     (it uses GITHUB_TOKEN; no AWS needed, runs on every push to master)
#   - You can SSH to the app host as ec2-user with your key
#
# Usage:
#   APP_HOST=<app_eip> ./infra/deploy-manual.sh
#   APP_HOST=<app_eip> IMAGE_TAG=sha-abc1234 ./infra/deploy-manual.sh
#
# Defaults to IMAGE_TAG=sha-<current local HEAD short SHA>.
set -euo pipefail

: "${APP_HOST:?Set APP_HOST to the app instance public IP or DNS name}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/comptoxai.pem}"
IMAGE_TAG="${IMAGE_TAG:-sha-$(git rev-parse --short=7 HEAD)}"

echo "==> Deploying ${IMAGE_TAG} to ${APP_HOST}"

ssh -i "${SSH_KEY}" -o StrictHostKeyChecking=accept-new "ec2-user@${APP_HOST}" bash -se <<EOF
set -euo pipefail
cd /opt/comptox_ai
git fetch --all
git reset --hard origin/master
IMAGE_TAG="${IMAGE_TAG}" docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod-app.yml \
  pull
IMAGE_TAG="${IMAGE_TAG}" docker compose \
  -f docker-compose.yml \
  -f docker-compose.prod-app.yml \
  up -d --remove-orphans
docker compose -f docker-compose.yml -f docker-compose.prod-app.yml ps
EOF

echo "==> Verifying /health..."
for i in $(seq 1 20); do
  if curl -fsS "https://api.comptox.ai/health" >/dev/null 2>&1; then
    echo "Healthy."
    curl -fsS "https://api.comptox.ai/health"
    echo
    exit 0
  fi
  sleep 3
done
echo "::error::API /health did not respond within 60s" >&2
exit 1
