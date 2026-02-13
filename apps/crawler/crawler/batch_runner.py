from __future__ import annotations

from collections.abc import Callable

from crawler.config import load_db_config
from crawler.db import Database
from crawler.ingest import ingest_all, summary, upsert_matches, upsert_teams
from crawler.logging_utils import log_event


def daily_update() -> int:
    return _run_batch(job_name="daily_update", run_fn=_run_daily)


def weekly_sync() -> int:
    return _run_batch(job_name="weekly_sync", run_fn=_run_weekly)


def _run_batch(*, job_name: str, run_fn: Callable[[Database], None]) -> int:
    log_event("INFO", "batch.start", job=job_name)
    db: Database | None = None

    try:
        config = load_db_config()
        db = Database.connect(config)
        db.bootstrap()
        run_fn(db)
        db.commit()
        log_event("INFO", "batch.success", job=job_name, summary=summary(db))
        return 0
    except Exception as exc:
        if db is not None:
            db.rollback()
        log_event("ERROR", "batch.failure", job=job_name, error=repr(exc))
        return 1
    finally:
        if db is not None:
            db.close()


def _run_daily(db: Database) -> None:
    ingest_all(db)


def _run_weekly(db: Database) -> None:
    upsert_teams(db)
    upsert_matches(db)
