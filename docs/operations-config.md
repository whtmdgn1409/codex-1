# Operations Config Guide

## Environment Variables
- 기준 템플릿: `.env.example`
- 로컬/서버 공통 필수:
  - `DB_URL`
  - `CRAWLER_DATA_SOURCE` (`sample` or `pl`)

## Premier League Source (`CRAWLER_DATA_SOURCE=pl`)
- URL:
  - `PL_TEAMS_URL`
  - `PL_PLAYERS_URL`
  - `PL_MATCHES_URL`
  - `PL_MATCH_STATS_URL`
- HTTP:
  - `PL_HTTP_TIMEOUT_SECONDS`
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

## GitHub Actions Secrets
- `BATCH_ALERT_SLACK_WEBHOOK`
- 설정 위치:
  - Repository Settings -> Secrets and variables -> Actions -> New repository secret

## Verification Checklist
1. `make crawler-test`
2. `CRAWLER_DATA_SOURCE=sample make crawler-daily`
3. (네트워크 허용 환경) `CRAWLER_DATA_SOURCE=pl make crawler-daily`
4. 실패 시 Slack 알림 수신 확인
