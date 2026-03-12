#!/usr/bin/env bash
set -euo pipefail

# Build and deploy the ComptoxAI static site (Sphinx docs + React app) to S3.
# Usage: ./infra/deploy-site.sh [--invalidate]
#
# Requires: AWS CLI configured, S3_BUCKET env var set.
# Optional: CLOUDFRONT_DIST_ID env var for cache invalidation.

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$REPO_ROOT/docs/build/html"

echo "==> Building Sphinx documentation..."
cd "$REPO_ROOT/docs"
make html

echo "==> Building React data browser app..."
cd "$REPO_ROOT/web/packages/app"
npm ci
npm run build

echo "==> Merging React app into Sphinx output..."
mkdir -p "$BUILD_DIR/browse"
cp -r "$REPO_ROOT/web/packages/app/build/"* "$BUILD_DIR/browse/"

echo "==> Syncing to S3..."
: "${S3_BUCKET:?Set S3_BUCKET env var (e.g. s3://comptox.ai)}"
aws s3 sync "$BUILD_DIR" "$S3_BUCKET" --delete

if [[ "${1:-}" == "--invalidate" ]] && [[ -n "${CLOUDFRONT_DIST_ID:-}" ]]; then
    echo "==> Invalidating CloudFront cache..."
    aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_DIST_ID" \
        --paths "/*"
fi

echo "==> Site deployed successfully."
