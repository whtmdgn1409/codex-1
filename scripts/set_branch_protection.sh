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
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["CI / api"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "required_conversation_resolution": true,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_linear_history": true,
  "block_creations": false,
  "required_signatures": false
}
JSON

echo "[done] branch protection updated"
