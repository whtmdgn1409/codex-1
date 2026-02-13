# Migrations

## Files
- `001_init_schema.sql`: teams/players/matches/match_stats/standings 생성
- `002_add_match_events.sql`: match_events 생성
- `003_add_player_season_stats.sql`: player_season_stats 생성

## Apply (MySQL)
```bash
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < apps/api/migrations/001_init_schema.sql
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < apps/api/migrations/002_add_match_events.sql
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < apps/api/migrations/003_add_player_season_stats.sql
```

## Idempotency / Upsert Strategy
- 참조 데이터(`teams`, `players`)는 `INSERT ... ON DUPLICATE KEY UPDATE`
- 경기 데이터(`matches`)는 `uq_matches_fixture` 기준 업서트
- 경기 통계(`match_stats`)는 `uq_match_stats_match_team` 기준 업서트
- 순위(`standings`)는 `team_id` PK 기준 업서트
- 이벤트(`match_events`)는 원천 이벤트 ID가 있으면 이를 키로 사용하고, 없으면 `(match_id, minute, event_type, player_name)` 조합으로 dedupe
- 선수 시즌 통계(`player_season_stats`)는 `player_id` PK 기준 업서트
