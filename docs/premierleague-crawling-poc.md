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
  - HTML table 기반 1차 파서(POC)
  - 필드 매핑 실패 시 빈 리스트 반환 + 오류 로그

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
