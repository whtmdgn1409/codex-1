#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   REPO="owner/repo" BRANCH="main" ./scripts/set_branch_protection.sh
# or:
#   ./scripts/set_branch_protection.sh owner/repo main
#
# Optional:
#   ENFORCE_ADMINS=true|false   (default: true)
#   DRY_RUN=1                   (print payload only, no remote call)

REPO="${REPO:-${1:-}}"
BRANCH="${BRANCH:-${2:-main}}"
ENFORCE_ADMINS="${ENFORCE_ADMINS:-true}"
DRY_RUN="${DRY_RUN:-0}"

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
echo "[info] enforce_admins=${ENFORCE_ADMINS} dry_run=${DRY_RUN}"

read -r -d '' PAYLOAD <<JSON || true
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["CI / api"]
  },
  "enforce_admins": ${ENFORCE_ADMINS},
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

if [[ "${ENFORCE_ADMINS}" != "true" && "${ENFORCE_ADMINS}" != "false" ]]; then
  echo "[error] ENFORCE_ADMINS must be true or false"
  exit 1
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "[dry-run] gh api --method PUT /repos/${REPO}/branches/${BRANCH}/protection"
  echo "${PAYLOAD}"
  exit 0
fi

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<<"${PAYLOAD}"

echo "[done] branch protection updated"
