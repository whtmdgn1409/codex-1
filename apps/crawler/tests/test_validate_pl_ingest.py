from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "ingest_validation"
REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "apps" / "crawler" / "scripts" / "validate_pl_ingest.py"


def _run_script(tmp_path: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    db_url = f"sqlite:///{(tmp_path / 'validate.db').as_posix()}"
    args = [
        sys.executable,
        str(SCRIPT_PATH),
        "--env",
        f"DB_URL={db_url}",
        "--env",
        f"PL_TEAMS_URL={(FIXTURE_DIR / 'teams.html').resolve().as_uri()}",
        "--env",
        f"PL_PLAYERS_URL={(FIXTURE_DIR / 'players.html').resolve().as_uri()}",
        "--env",
        f"PL_MATCHES_URL={(FIXTURE_DIR / 'matches.html').resolve().as_uri()}",
        "--env",
        f"PL_MATCH_STATS_URL={(FIXTURE_DIR / 'match_stats.html').resolve().as_uri()}",
        "--env",
        "PL_POLICY_TEAMS=abort",
        "--env",
        "PL_POLICY_PLAYERS=skip",
        "--env",
        "PL_POLICY_MATCHES=abort",
        "--env",
        "PL_POLICY_MATCH_STATS=skip",
    ]
    args.extend(extra_args)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "apps" / "crawler")
    return subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True, check=False, env=env)


def _last_json_line(stdout: str) -> dict[str, object]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    assert lines, "expected JSON line in stdout"
    return json.loads(lines[-1])


def test_validate_pl_ingest_success_and_export(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"

    result = _run_script(tmp_path, "--output-json", str(report_path))

    assert result.returncode == 0
    payload = _last_json_line(result.stdout)
    assert payload["ok"] is True
    assert payload["summary"]["teams"] == 2
    assert payload["summary"]["matches"] == 1

    written = json.loads(report_path.read_text(encoding="utf-8"))
    assert written == payload


def test_validate_pl_ingest_fails_health_check_when_matches_empty(tmp_path: Path) -> None:
    result = _run_script(
        tmp_path,
        "--env",
        f"PL_MATCHES_URL={(FIXTURE_DIR / 'matches_empty.html').resolve().as_uri()}",
        "--env",
        "PL_POLICY_MATCHES=skip",
        "--env",
        f"PL_MATCH_STATS_URL={(FIXTURE_DIR / 'matches_empty.html').resolve().as_uri()}",
        "--env",
        "PL_POLICY_MATCH_STATS=skip",
    )

    assert result.returncode == 1
    payload = _last_json_line(result.stdout)
    assert payload["ok"] is False
    assert payload["summary"]["matches"] == 0
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["matches_non_zero"]["ok"] is False


def test_validate_pl_ingest_allows_empty_matches_when_configured(tmp_path: Path) -> None:
    result = _run_script(
        tmp_path,
        "--env",
        f"PL_MATCHES_URL={(FIXTURE_DIR / 'matches_empty.html').resolve().as_uri()}",
        "--env",
        "PL_POLICY_MATCHES=skip",
        "--env",
        f"PL_MATCH_STATS_URL={(FIXTURE_DIR / 'matches_empty.html').resolve().as_uri()}",
        "--env",
        "PL_POLICY_MATCH_STATS=skip",
        "--allow-empty-matches",
    )

    assert result.returncode == 0
    payload = _last_json_line(result.stdout)
    assert payload["ok"] is True
    checks = {check["name"]: check for check in payload["checks"]}
    assert checks["matches_non_zero"]["enabled"] is False
    assert checks["matches_non_zero"]["ok"] is True
