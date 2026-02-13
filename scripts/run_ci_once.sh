#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   REPO="owner/repo" BRANCH="main" ./scripts/run_ci_once.sh
# or:
#   ./scripts/run_ci_once.sh owner/repo main

REPO="${REPO:-${1:-}}"
BRANCH="${BRANCH:-${2:-main}}"
WORKFLOW="CI"

if [[ -z "${REPO}" ]]; then
  echo "[error] repo is required (owner/repo)."
  exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
  echo "[error] gh CLI not found"
  exit 1
fi

echo "[info] triggering workflow '${WORKFLOW}' on ${REPO} @ ${BRANCH}"
gh workflow run "${WORKFLOW}" --repo "${REPO}" --ref "${BRANCH}"

echo "[info] latest run summary"
gh run list --repo "${REPO}" --workflow "${WORKFLOW}" --limit 1

echo "[info] watching latest run (Ctrl+C to stop)"
RUN_ID="$(gh run list --repo "${REPO}" --workflow "${WORKFLOW}" --limit 1 --json databaseId -q '.[0].databaseId')"
gh run watch "${RUN_ID}" --repo "${REPO}"
