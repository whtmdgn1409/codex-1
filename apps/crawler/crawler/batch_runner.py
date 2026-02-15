from __future__ import annotations

import time
from collections.abc import Callable

from crawler.alerts import send_failure_alert
from crawler.config import load_batch_policy_config, load_db_config
from crawler.db import Database
from crawler.ingest import ingest_all, summary, upsert_matches, upsert_standings, upsert_teams
from crawler.logging_utils import log_event
from crawler.sources import get_data_source


def daily_update() -> int:
    return _run_batch(job_name="daily_update", run_fn=_run_daily)


def weekly_sync() -> int:
    return _run_batch(job_name="weekly_sync", run_fn=_run_weekly)


def _run_batch(*, job_name: str, run_fn: Callable[[Database], None]) -> int:
    log_event("INFO", "batch.start", job=job_name)
    policy = load_batch_policy_config()
    last_error: Exception | None = None

    for attempt in range(1, policy.retry_count + 1):
        db: Database | None = None
        try:
            config = load_db_config()
            db = Database.connect(config)
            db.bootstrap()
            run_fn(db)
            db.commit()
            log_event("INFO", "batch.success", job=job_name, attempt=attempt, summary=summary(db))
            return 0
        except Exception as exc:
            last_error = exc
            if db is not None:
                db.rollback()
            log_event("ERROR", "batch.failure", job=job_name, attempt=attempt, error=repr(exc))
            if attempt < policy.retry_count:
                wait_seconds = policy.retry_backoff_seconds * attempt
                log_event("WARNING", "batch.retry", job=job_name, next_attempt=attempt + 1, wait_seconds=wait_seconds)
                time.sleep(wait_seconds)
            else:
                send_failure_alert(job_name=job_name, error=repr(exc), attempts=attempt)
                return 1
        finally:
            if db is not None:
                db.close()

    if last_error is not None:
        send_failure_alert(job_name=job_name, error=repr(last_error), attempts=policy.retry_count)
    return 1


def _run_daily(db: Database) -> None:
    ingest_all(db)


def _run_weekly(db: Database) -> None:
    source = get_data_source()
    upsert_teams(db, source.load_teams())
    upsert_matches(db, source.load_matches())
    upsert_standings(db, source.load_standings())
