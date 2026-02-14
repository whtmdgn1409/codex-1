# CI Required Checks

브랜치 보호 규칙(예: `main`)에서 아래 Job/Step이 반드시 통과하도록 설정합니다.

## Workflow
- `CI / api`
- `CI / web-e2e`

## Required Step Intent
- `OpenAPI Snapshot Test (Required)`
- `API Integration Test (API-002~005) (Required)`

참고: GitHub Branch Protection은 Step 단위가 아닌 Job 단위 강제입니다.
따라서 `CI / api`를 Required Check로 지정하면 위 두 필수 step 실패 시 머지가 차단됩니다.

## PR-Only Enforcement (Required)
`main` 브랜치에는 직접 push가 불가능하고 PR 머지만 가능해야 합니다.

필수 보호 설정:
- Require a pull request before merging: `ON`
- Required approvals: `1+`
- Dismiss stale pull request approvals when new commits are pushed: `ON`
- Require conversation resolution before merging: `ON`
- Require status checks to pass before merging: `ON`
- Required status checks: `CI / api`
- Required status checks: `CI / api`, `CI / web-e2e`
- Require branches to be up to date before merging: `ON` (`strict=true`)
- Require linear history: `ON`
- Allow force pushes: `OFF`
- Allow deletions: `OFF`
- Include administrators: `ON` (`enforce_admins=true`)

검증 포인트:
- 관리자 계정도 `main` 직접 push가 거부되어야 함
- PR에서 `CI / api` 실패 시 merge 버튼이 비활성화되어야 함

## One-shot Commands
```bash
REPO=<owner/repo> BRANCH=main DRY_RUN=1 ./scripts/set_branch_protection.sh
REPO=<owner/repo> BRANCH=main ENFORCE_ADMINS=true ./scripts/set_branch_protection.sh
REPO=<owner/repo> BRANCH=main ./scripts/run_ci_once.sh
```
