# Premier League Crawling POC

## Goal
- 공식 사이트(`https://www.premierleague.com/en`)를 데이터 소스로 사용할 수 있는지 기술 검증한다.
- 기존 샘플 소스와 호환되는 `teams`, `players`, `matches`, `match_stats` 적재 포맷을 유지한다.

## Scope (POC)
- 데이터소스 선택:
  - `CRAWLER_DATA_SOURCE=sample` (기본값)
  - `CRAWLER_DATA_SOURCE=pl` (공식 사이트)
- HTTP 수집:
  - 대상 URL 환경변수화 (`PL_TEAMS_URL`, `PL_PLAYERS_URL`, `PL_MATCHES_URL`, `PL_MATCH_STATS_URL`)
  - 재시도: `PL_HTTP_RETRY_COUNT`
  - 백오프: `PL_HTTP_RETRY_BACKOFF_SECONDS`
  - 타임아웃: `PL_HTTP_TIMEOUT_SECONDS`
- 파싱:
  - 다중 파싱 전략:
    - 1차: HTML table 파싱(헤더 alias 매핑)
    - 2차: Script JSON(`application/json`, `__NEXT_DATA__`, `__PRELOADED_STATE__`) fallback
  - 필드 매핑 실패 시 정책 분기:
    - `PL_PARSE_STRICT=0` -> 다음 전략으로 진행
    - `PL_PARSE_STRICT=1` -> 즉시 예외
  - 최종 실패 시 데이터셋 정책 분기:
    - `PL_POLICY_TEAMS=abort|skip` (기본 `abort`)
    - `PL_POLICY_PLAYERS=abort|skip` (기본 `skip`)
    - `PL_POLICY_MATCHES=abort|skip` (기본 `abort`)
    - `PL_POLICY_MATCH_STATS=abort|skip` (기본 `skip`)
  - Teams seed fallback:
    - `PL_TEAMS_SEED_FALLBACK=1` (기본): teams 파싱 실패 시 seed 팀 목록으로 대체
    - `PL_TEAMS_SEED_FALLBACK=0`: seed fallback 비활성화(정책값 그대로 abort/skip 적용)

## Field Mapping (Crawler Payload)
- `teams`: `name`, `short_name`, `logo_url`, `stadium`, `manager`
- `players`: `player_id`, `team_short_name`, `name`, `position`, `jersey_num`, `nationality`, `photo_url`
- `matches`: `round`, `match_date`, `home_team_short_name`, `away_team_short_name`, `home_score`, `away_score`, `status`
- `match_stats`: `round`, `home_team_short_name`, `away_team_short_name`, `team_short_name`, `possession`, `shots`, `shots_on_target`, `fouls`, `corners`

## Validation Plan
1. 단위 테스트:
- 소스 선택(`sample`/`pl`)
- 파싱(teams/matches) fixture
- retry 동작(실패 후 성공)

2. 통합 실행:
- `make crawler-test`
- `CRAWLER_DATA_SOURCE=sample make crawler-daily`
- (네트워크 허용 환경) `CRAWLER_DATA_SOURCE=pl make crawler-daily`

## Risks
- 공식 사이트 구조가 JS 중심이라 정적 HTML table 의존 파서는 깨질 수 있다.
- 약관/라이선스 제한 검토가 선행되어야 운영 사용 가능하다.

## Current Decision
- 운영 안정성 기준:
  - 핵심 데이터셋(`teams`, `matches`)은 `abort`
  - 부가 데이터셋(`players`, `match_stats`)은 `skip`
  - 단, `teams`는 공식 페이지 파싱 실패 대비 seed fallback을 기본 활성화
