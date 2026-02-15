import os
from pathlib import Path

from crawler.cli import main
from crawler.config import load_db_config
from crawler.db import Database
from crawler.ingest import summary


def _run_ingest_all_with_sqlite(db_path: Path) -> dict[str, int]:
    os.environ["DB_URL"] = f"sqlite:///{db_path.as_posix()}"

    # CLI entry behavior for ingestion.
    import sys

    old_argv = sys.argv
    try:
        sys.argv = ["crawler", "ingest-all"]
        main()
    finally:
        sys.argv = old_argv

    db = Database.connect(load_db_config())
    try:
        return summary(db)
    finally:
        db.close()


def test_ingest_all_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "crawler_test.db"

    first = _run_ingest_all_with_sqlite(db_path)
    second = _run_ingest_all_with_sqlite(db_path)

    assert first == second
    assert first["teams"] >= 1
    assert first["players"] >= 1
    assert first["matches"] >= 1
    assert first["match_stats"] >= 1
    assert first["standings"] >= 1
