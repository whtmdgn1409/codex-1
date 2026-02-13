import os
import subprocess
import sys
from pathlib import Path

from crawler.cli import main


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _run_cli_command(command: str, db_url: str) -> bool:
    old_db_url = os.environ.get("DB_URL")
    old_argv = sys.argv

    try:
        os.environ["DB_URL"] = db_url
        sys.argv = ["crawler", command]
        main()
        return True
    except Exception:
        return False
    finally:
        sys.argv = old_argv
        if old_db_url is None:
            os.environ.pop("DB_URL", None)
        else:
            os.environ["DB_URL"] = old_db_url


def _run_daily_batch(db_url: str) -> bool:
    return _run_cli_command("ingest-all", db_url)


def _run_weekly_batch(db_url: str) -> bool:
    return _run_cli_command("ingest-matches", db_url)


def _run_make_target(target: str, db_url: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DB_URL"] = db_url

    return subprocess.run(
        ["make", target],
        cwd=_repo_root(),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_daily_batch_success_returns_true_and_zero_exit(tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'daily_success.db').as_posix()}"

    assert _run_daily_batch(db_url) is True

    make_result = _run_make_target("crawler-daily", db_url)
    assert make_result.returncode == 0


def test_daily_batch_failure_returns_false_and_non_zero_exit(tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'missing_parent' / 'daily_fail.db').as_posix()}"

    assert _run_daily_batch(db_url) is False

    make_result = _run_make_target("crawler-daily", db_url)
    assert make_result.returncode != 0


def test_weekly_batch_success_returns_true_and_zero_exit(tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'weekly_success.db').as_posix()}"

    assert _run_cli_command("ingest-teams", db_url) is True
    assert _run_weekly_batch(db_url) is True

    make_result = _run_make_target("crawler-weekly", db_url)
    assert make_result.returncode == 0


def test_weekly_batch_failure_returns_false_and_non_zero_exit(tmp_path: Path) -> None:
    db_url = f"sqlite:///{(tmp_path / 'weekly_fail.db').as_posix()}"

    assert _run_weekly_batch(db_url) is False

    make_result = _run_make_target("crawler-weekly", db_url)
    assert make_result.returncode != 0
