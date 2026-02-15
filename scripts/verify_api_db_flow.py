#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _run_crawler_ingest(*, repo_root: Path, db_url: str, source: str) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo_root / "apps" / "crawler")
    env["DB_URL"] = db_url
    env["CRAWLER_DATA_SOURCE"] = source

    cmd = [sys.executable, "-m", "crawler.cli", "ingest-all"]
    subprocess.run(cmd, cwd=repo_root, env=env, check=True)


def _verify_api_endpoints(*, repo_root: Path, api_db_url: str) -> dict[str, object]:
    os.environ["DB_URL"] = api_db_url
    sys.path.insert(0, str(repo_root / "apps" / "api"))

    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        teams = client.get("/teams")
        matches = client.get("/matches")
        standings = client.get("/standings")
        stats = client.get("/stats/top", params={"category": "goals", "limit": 5})

        teams_json = teams.json()
        matches_json = matches.json()
        standings_json = standings.json()
        stats_json = stats.json()

        first_match_id = matches_json["items"][0]["match_id"] if matches_json.get("items") else None
        first_team_id = teams_json["items"][0]["team_id"] if teams_json.get("items") else None

        match_detail_status = client.get(f"/matches/{first_match_id}").status_code if first_match_id is not None else None
        team_detail_status = client.get(f"/teams/{first_team_id}").status_code if first_team_id is not None else None

    return {
        "teams_total": teams_json.get("total", 0),
        "matches_total": matches_json.get("total", 0),
        "standings_total": standings_json.get("total", 0),
        "stats_total": stats_json.get("total", 0),
        "match_detail_status": match_detail_status,
        "team_detail_status": team_detail_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify API responses directly from crawler-ingested DB.")
    parser.add_argument("--source", choices=["sample", "pl", "api_football"], default="sample")
    parser.add_argument("--db-path", default="./apps/crawler/dev_crawler_verify.db")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    db_path = (repo_root / args.db_path).resolve()
    if db_path.exists():
        db_path.unlink()

    crawler_db_url = f"sqlite:///{db_path.as_posix()}"
    api_db_url = f"sqlite+pysqlite:///{db_path.as_posix()}"

    _run_crawler_ingest(repo_root=repo_root, db_url=crawler_db_url, source=args.source)
    result = _verify_api_endpoints(repo_root=repo_root, api_db_url=api_db_url)

    checks = {
        "teams>0": result["teams_total"] > 0,
        "matches>0": result["matches_total"] > 0,
        "standings>0": result["standings_total"] > 0,
        "stats>=0": result["stats_total"] >= 0,
        "match_detail_200": result["match_detail_status"] == 200 if result["match_detail_status"] is not None else False,
        "team_detail_200": result["team_detail_status"] == 200 if result["team_detail_status"] is not None else False,
    }
    output = {"ok": all(checks.values()), "source": args.source, "db_path": str(db_path), "summary": result, "checks": checks}
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
