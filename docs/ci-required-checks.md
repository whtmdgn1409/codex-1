# CI Required Checks

브랜치 보호 규칙(예: `main`)에서 아래 Job/Step이 반드시 통과하도록 설정합니다.

## Workflow
- `CI / api`

## Required Step Intent
- `OpenAPI Snapshot Test (Required)`
- `API Integration Test (API-002~005) (Required)`

참고: GitHub Branch Protection은 Step 단위가 아닌 Job 단위 강제입니다.
따라서 `CI / api`를 Required Check로 지정하면 위 두 필수 step 실패 시 머지가 차단됩니다.

## One-shot Commands
```bash
REPO=<owner/repo> BRANCH=main ./scripts/set_branch_protection.sh
REPO=<owner/repo> BRANCH=main ./scripts/run_ci_once.sh
```
