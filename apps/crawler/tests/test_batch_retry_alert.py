from __future__ import annotations

from pathlib import Path

from crawler.batch_runner import _run_batch
from crawler.db import Database


def _sqlite_db_url(tmp_path: Path, name: str) -> str:
    return f"sqlite:///{(tmp_path / name).as_posix()}"


def test_run_batch_retries_and_recovers(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DB_URL", _sqlite_db_url(tmp_path, "retry_success.db"))
    monkeypatch.setenv("BATCH_RETRY_COUNT", "2")
    monkeypatch.setenv("BATCH_RETRY_BACKOFF_SECONDS", "0")

    attempts = {"count": 0}
    alerts = {"count": 0}

    def run_fn(_: Database) -> None:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise RuntimeError("fail once")

    monkeypatch.setattr("crawler.batch_runner.send_failure_alert", lambda **_: alerts.__setitem__("count", alerts["count"] + 1))

    code = _run_batch(job_name="retry_success", run_fn=run_fn)
    assert code == 0
    assert attempts["count"] == 2
    assert alerts["count"] == 0


def test_run_batch_sends_alert_when_retries_exhausted(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("DB_URL", _sqlite_db_url(tmp_path, "retry_fail.db"))
    monkeypatch.setenv("BATCH_RETRY_COUNT", "2")
    monkeypatch.setenv("BATCH_RETRY_BACKOFF_SECONDS", "0")

    attempts = {"count": 0}
    alert_payload: dict[str, object] = {}

    def run_fn(_: Database) -> None:
        attempts["count"] += 1
        raise RuntimeError("always fail")

    def fake_alert(**kwargs):
        alert_payload.update(kwargs)
        return True

    monkeypatch.setattr("crawler.batch_runner.send_failure_alert", fake_alert)

    code = _run_batch(job_name="retry_fail", run_fn=run_fn)
    assert code == 1
    assert attempts["count"] == 2
    assert alert_payload["job_name"] == "retry_fail"
    assert alert_payload["attempts"] == 2
