# API Service

## Run
```bash
make setup
make dev
```

## Test & Lint
```bash
make lint
make test
make test-openapi
make test-integration
make test-unit
# OpenAPI snapshot 갱신이 필요하면
UPDATE_OPENAPI_SNAPSHOT=1 PYTHONPATH=apps/api python3 -m pytest -q apps/api/tests/test_openapi_snapshot.py
```

## API
- `GET /health`
- `GET /matches?round=2&month=9&team_id=1&limit=50&offset=0`
- `GET /matches/{match_id}`
- `GET /standings`
- `GET /stats/top?category=goals&limit=10`
- `GET /teams`
- `GET /teams/{team_id}`

## Local DB
기본 DB URL은 `sqlite+pysqlite:///./epl.db`입니다.
MySQL 연동 시 `.env` 또는 환경변수로 `DB_URL`을 지정하세요.
