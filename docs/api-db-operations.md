# API/DB Operations Guidelines

## API Principles
- 엔드포인트는 읽기 중심으로 시작하고, 쓰기 API는 내부 배치 전용으로 분리한다.
- 응답은 일관된 스키마를 유지한다 (`total`, `items` 등).
- 필터/페이지네이션 파라미터는 유효성 검사(범위/타입)를 강제한다.
- 변경이 필요한 경우 버저닝(`/v1`) 도입 전까지는 하위호환을 우선한다.

## DB Principles
- 기준 DB는 MySQL이며, 스키마 변경은 SQL 마이그레이션 파일로만 관리한다.
- 외래키/유니크 키/인덱스를 명시적으로 선언한다.
- 참조성 있는 배치 데이터는 업서트(`ON DUPLICATE KEY UPDATE`)로 멱등성 보장.
- 통계성 데이터(`standings`, `match_stats`)는 재계산 가능성을 고려해 overwrite-safe하게 설계.

## Data Integrity Checklist
- `matches.home_team_id != away_team_id`
- `status=FINISHED`일 때 스코어 NULL 금지
- `match_stats`는 `(match_id, team_id)` 유니크
- `standings.rank`는 1~20 유효 범위

## Runtime & Monitoring
- API 헬스체크: `GET /health`
- 배치 실패 시 알림(Slack/Email) + 재시도 정책 필수
- 배포 전: 마이그레이션 dry-run 및 롤백 계획 검토
