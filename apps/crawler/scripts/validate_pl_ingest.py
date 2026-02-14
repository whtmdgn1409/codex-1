#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from crawler.config import load_db_config
from crawler.db import Database
from crawler.ingest import ingest_all, summary


@contextmanager
def _temporary_env(overrides: dict[str, str]) -> Iterator[None]:
    previous: dict[str, str | None] = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            os.environ[key] = value
        yield
    finally:
        for key, old_value in previous.items():
            if old_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old_value


def _parse_env_overrides(raw_values: list[str]) -> dict[str, str]:
    overrides: dict[str, str] = {}
    for raw in raw_values:
        if "=" not in raw:
            raise ValueError(f"invalid --env value '{raw}': expected KEY=VALUE")
        key, value = raw.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"invalid --env value '{raw}': key is empty")
        overrides[key] = value
    return overrides


def _build_report(
    counts: dict[str, int],
    *,
    allow_empty_teams: bool,
    allow_empty_matches: bool,
) -> dict[str, object]:
    team_count = counts.get("teams", 0)
    match_count = counts.get("matches", 0)

    checks = [
        {
            "name": "teams_non_zero",
            "enabled": not allow_empty_teams,
            "ok": allow_empty_teams or team_count > 0,
            "actual": team_count,
            "expected": ">=1",
        },
        {
            "name": "matches_non_zero",
            "enabled": not allow_empty_matches,
            "ok": allow_empty_matches or match_count > 0,
            "actual": match_count,
            "expected": ">=1",
        },
    ]

    return {
        "ok": all(bool(check["ok"]) for check in checks),
        "summary": counts,
        "checks": checks,
    }


def run_validation(
    *,
    env_overrides: dict[str, str],
    allow_empty_teams: bool,
    allow_empty_matches: bool,
) -> dict[str, object]:
    with _temporary_env(env_overrides):
        db = Database.connect(load_db_config())
        try:
            db.bootstrap()
            ingest_all(db)
            db.commit()
            counts = summary(db)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    return _build_report(
        counts,
        allow_empty_teams=allow_empty_teams,
        allow_empty_matches=allow_empty_matches,
    )


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run PL-mode ingest and validate basic health checks")
    parser.add_argument(
        "--env",
        action="append",
        default=[],
        help="Environment override (KEY=VALUE). Repeatable.",
    )
    parser.add_argument(
        "--output-json",
        help="Optional path to write the validation JSON report.",
    )
    parser.add_argument(
        "--allow-empty-teams",
        action="store_true",
        help="Skip teams>0 validation check.",
    )
    parser.add_argument(
        "--allow-empty-matches",
        action="store_true",
        help="Skip matches>0 validation check.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    try:
        env_overrides = _parse_env_overrides(args.env)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    env_overrides["CRAWLER_DATA_SOURCE"] = "pl"

    try:
        report = run_validation(
            env_overrides=env_overrides,
            allow_empty_teams=args.allow_empty_teams,
            allow_empty_matches=args.allow_empty_matches,
        )
    except Exception as exc:
        report = {
            "ok": False,
            "error": repr(exc),
            "summary": {},
            "checks": [],
        }
        print(json.dumps(report, ensure_ascii=False))
        if args.output_json:
            Path(args.output_json).write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        return 2

    payload = json.dumps(report, ensure_ascii=False)
    print(payload)

    if args.output_json:
        Path(args.output_json).write_text(payload, encoding="utf-8")

    return 0 if bool(report.get("ok")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
