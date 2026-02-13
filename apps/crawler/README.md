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
```

기본 DB는 `DB_URL` 환경변수로 제어합니다.

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

## Idempotency
동일 명령을 반복 실행해도 중복 데이터가 증가하지 않도록 업서트를 사용합니다.
