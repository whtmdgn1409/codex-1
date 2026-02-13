#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   REPO="owner/repo" BRANCH="main" ./scripts/set_branch_protection.sh
# or:
#   ./scripts/set_branch_protection.sh owner/repo main

REPO="${REPO:-${1:-}}"
BRANCH="${BRANCH:-${2:-main}}"

if [[ -z "${REPO}" ]]; then
  echo "[error] repo is required (owner/repo)."
  echo "example: REPO=acme/epl-hub BRANCH=main ./scripts/set_branch_protection.sh"
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "[error] gh CLI not found"
  exit 1
fi

# Requires authenticated gh session with repo admin rights.
# Enforces CI job check name: "CI / api"

echo "[info] applying branch protection to ${REPO}:${BRANCH}"

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  -f required_status_checks.strict=true \
  -f enforce_admins=false \
  -F required_status_checks.contexts[]='CI / api' \
  -f required_pull_request_reviews.dismiss_stale_reviews=true \
  -f required_pull_request_reviews.require_code_owner_reviews=false \
  -f required_pull_request_reviews.required_approving_review_count=1 \
  -f required_conversation_resolution=true \
  -f restrictions= \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f required_linear_history=true \
  -f block_creations=false \
  -f required_signatures=false

echo "[done] branch protection updated"
