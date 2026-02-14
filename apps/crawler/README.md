# Crawler Service

`CRAWL-001` 초기 수집 파이프라인입니다.
샘플 데이터 소스 기반으로 `teams`, `players`, `matches`, `match_stats`를 멱등 업서트합니다.

## Setup
```bash
make crawler-setup
```

## Run
```bash
make crawler-ingest
make crawler-summary
make crawler-validate
```

## Batch Runner (Skeleton)
```bash
make crawler-daily   # BATCH-001 일배치(수동)
make crawler-weekly  # BATCH-002 주배치(수동)
```

## Batch Scheduler (GitHub Actions)
- 워크플로: `.github/workflows/batch-scheduler.yml`
- 자동 실행:
  - 일배치: 매일 09:00 KST (`cron: 0 0 * * *`, UTC)
  - 주배치: 매주 목요일 12:00 KST (`cron: 0 3 * * 4`, UTC)
- 수동 실행: `workflow_dispatch` 입력값 `all | daily | weekly`
- 재시도/알림(BATCH-003):
  - `BATCH_RETRY_COUNT` (기본 `1`)
  - `BATCH_RETRY_BACKOFF_SECONDS` (기본 `1.0`)
  - `BATCH_ALERT_SLACK_WEBHOOK` (설정 시 최종 실패 알림 전송)

기본 DB는 `DB_URL` 환경변수로 제어합니다.
데이터 소스는 `CRAWLER_DATA_SOURCE`로 제어합니다.
- `sample` (기본): 내장 샘플 데이터
- `pl`: Premier League 공식 사이트 POC 파서

`pl` 사용 시 URL/재시도 설정:
```bash
CRAWLER_DATA_SOURCE=pl
PL_TEAMS_URL=https://www.premierleague.com/en/clubs
PL_MATCHES_URL=https://www.premierleague.com/en/matches
PL_PLAYERS_URL=https://www.premierleague.com/stats/top/players/goals
PL_MATCH_STATS_URL=https://www.premierleague.com/stats
PL_HTTP_RETRY_COUNT=3
PL_HTTP_RETRY_BACKOFF_SECONDS=1.0
PL_HTTP_TIMEOUT_SECONDS=20
PL_PARSE_STRICT=0
PL_POLICY_TEAMS=abort
PL_POLICY_PLAYERS=skip
PL_POLICY_MATCHES=abort
PL_POLICY_MATCH_STATS=skip
BATCH_RETRY_COUNT=3
BATCH_RETRY_BACKOFF_SECONDS=2
# 선택: Slack incoming webhook
# BATCH_ALERT_SLACK_WEBHOOK=https://hooks.slack.com/services/xxx/yyy/zzz
```

파서 실패 정책:
- `PL_PARSE_STRICT=0` (기본): 헤더 불일치 시 로그 남기고 해당 데이터셋 스킵
- `PL_PARSE_STRICT=1`: 헤더 불일치 시 예외 발생(배치 실패 처리)
- 데이터셋별 fallback 정책:
  - `PL_POLICY_TEAMS`: `abort|skip` (기본 `abort`)
  - `PL_POLICY_PLAYERS`: `abort|skip` (기본 `skip`)
  - `PL_POLICY_MATCHES`: `abort|skip` (기본 `abort`)
  - `PL_POLICY_MATCH_STATS`: `abort|skip` (기본 `skip`)
  - 동작: table 파싱 실패 -> JSON fallback 시도 -> 최종 실패 시 dataset 정책 적용

예시 (로컬 sqlite):
```bash
DB_URL=sqlite:///./apps/crawler/dev_crawler.db PYTHONPATH=apps/crawler python3 -m crawler.cli ingest-all
```

예시 (MySQL):
```bash
DB_URL=mysql+pymysql://epl_user:change_me@localhost:3306/epl_hub PYTHONPATH=apps/crawler python3 -m crawler.cli ingest-all
```

## Commands
- `ingest-all`: 전체 적재 (팀/선수/경기/경기스탯)
- `ingest-teams`: 팀만 적재
- `ingest-players`: 선수만 적재
- `ingest-matches`: 경기만 적재
- `summary`: 테이블별 카운트 출력
- `validate_pl_ingest.py`: PL 모드 적재 + 검증 리포트(JSON) 출력

검증 스크립트 사용 예시:
```bash
PYTHONPATH=apps/crawler python3 apps/crawler/scripts/validate_pl_ingest.py \
  --env DB_URL=sqlite:///./apps/crawler/dev_crawler.db \
  --env PL_TEAMS_URL=file:///abs/path/to/teams.html \
  --env PL_PLAYERS_URL=file:///abs/path/to/players.html \
  --env PL_MATCHES_URL=file:///abs/path/to/matches.html \
  --env PL_MATCH_STATS_URL=file:///abs/path/to/match_stats.html \
  --output-json ./apps/crawler/validation_report.json
```

리포트/종료코드 규칙:
- stdout: `ok`, `summary`, `checks`를 포함한 JSON 1줄 출력
- `--output-json`: 동일 JSON을 파일로 저장
- 기본 헬스체크: `teams > 0`, `matches > 0`
- 예외 옵션: `--allow-empty-teams`, `--allow-empty-matches`
- 종료코드: 성공 `0`, 검증 실패 `1`, 실행 오류 `2`

## Idempotency
동일 명령을 반복 실행해도 중복 데이터가 증가하지 않도록 업서트를 사용합니다.
