# Operations Config Guide

## Environment Variables
- 기준 템플릿: `.env.example`
- 로컬/서버 공통 필수:
  - `DB_URL`
  - `CRAWLER_DATA_SOURCE` (`sample` or `pl`)
  - `NEXT_PUBLIC_API_BASE_URL`

## Premier League Source (`CRAWLER_DATA_SOURCE=pl`)
- URL:
  - `PL_TEAMS_URL`
  - `PL_PLAYERS_URL`
  - `PL_MATCHES_URL`
  - `PL_MATCH_STATS_URL`
- HTTP:
  - `PL_HTTP_TIMEOUT_SECONDS`
  - `PL_HTTP_VERIFY_SSL`
  - `PL_HTTP_CA_FILE`
  - `PL_HTTP_RETRY_COUNT`
  - `PL_HTTP_RETRY_BACKOFF_SECONDS`
- 파싱 정책:
  - `PL_PARSE_STRICT` (`0|1`)
  - `PL_POLICY_TEAMS` (`abort|skip`)
  - `PL_POLICY_PLAYERS` (`abort|skip`)
  - `PL_POLICY_MATCHES` (`abort|skip`)
  - `PL_POLICY_MATCH_STATS` (`abort|skip`)

권장 운영값:
- `PL_POLICY_TEAMS=abort`
- `PL_POLICY_MATCHES=abort`
- `PL_POLICY_PLAYERS=skip`
- `PL_POLICY_MATCH_STATS=skip`

## Batch Retry/Alert
- 재시도:
  - `BATCH_RETRY_COUNT`
  - `BATCH_RETRY_BACKOFF_SECONDS`
- 알림:
  - `BATCH_ALERT_SLACK_WEBHOOK`
  - `BATCH_ALERT_TIMEOUT_SECONDS`

## Secrets and Variables Checklist
배치 알림과 크롤러 소스 설정을 아래 기준으로 분리합니다.

### 1) Must Be GitHub Secrets
- `BATCH_ALERT_SLACK_WEBHOOK`
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`

체크리스트:
1. Repository Settings -> Secrets and variables -> Actions에 저장
2. 값이 로그/문서/스크립트 출력에 노출되지 않도록 마스킹 확인
3. `.env`, `docs/`, `scripts/`에 webhook 원문 하드코딩 금지
4. webhook 회전(rotate) 시 구 값 폐기 및 배치 수동 실행으로 알림 테스트

### 2) Non-Secret Config (Repo Variables or env)
- `CRAWLER_DATA_SOURCE` (`sample|pl`)
- `PL_TEAMS_URL`
- `PL_PLAYERS_URL`
- `PL_MATCHES_URL`
- `PL_MATCH_STATS_URL`
- `PL_HTTP_TIMEOUT_SECONDS`
- `PL_HTTP_VERIFY_SSL`
- `PL_HTTP_CA_FILE`
- `PL_HTTP_RETRY_COUNT`
- `PL_HTTP_RETRY_BACKOFF_SECONDS`
- `PL_PARSE_STRICT`
- `PL_POLICY_TEAMS`
- `PL_POLICY_PLAYERS`
- `PL_POLICY_MATCHES`
- `PL_POLICY_MATCH_STATS`
- `NEXT_PUBLIC_SITE_URL`

체크리스트:
1. `CRAWLER_DATA_SOURCE=pl`인 경우 `PL_*_URL` 4개 모두 설정
2. SSL 오류 발생 시 `PL_HTTP_CA_FILE` 우선 지정 후 재검증
3. `PL_HTTP_VERIFY_SSL=0`은 진단용 임시 설정으로만 사용
4. 운영 권장 정책(`teams/matches=abort`, `players/match_stats=skip`) 반영
5. 파서 정책 변경 시 배치 실패/skip 로그를 함께 점검
6. 민감값(토큰/쿠키/사설 엔드포인트)이 필요해지면 Variables가 아닌 Secrets로 승격

## Vercel Deploy Config
- 워크플로: `.github/workflows/vercel-deploy.yml`
- 배포 정책:
  - PR: Deploy Preview 생성 후 PR 코멘트에 URL 기록
  - `main` push: Production 배포

체크리스트:
1. Vercel에서 프로젝트 생성 후 `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`를 GitHub Secrets에 등록
2. Vercel Project Environment Variables에 `NEXT_PUBLIC_API_BASE_URL`(필수), `NEXT_PUBLIC_SITE_URL`(권장) 설정
3. PR 생성 시 `Vercel Deploy / deploy-preview` 성공 및 Preview URL 코멘트 확인
4. `main` 머지 후 `Vercel Deploy / deploy-production` 성공 확인

## Verification Checklist
1. `make crawler-test`
2. `CRAWLER_DATA_SOURCE=sample make crawler-daily`
3. (네트워크 허용 환경) `CRAWLER_DATA_SOURCE=pl make crawler-daily`
4. 실패 시 Slack 알림 수신 확인
5. `DRY_RUN=1 REPO=<owner/repo> BRANCH=main ./scripts/set_branch_protection.sh`로 보호 설정 payload 검증
