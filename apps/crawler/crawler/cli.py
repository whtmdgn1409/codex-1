from __future__ import annotations

import argparse
import json

from crawler.config import load_db_config
from crawler.db import Database
from crawler.ingest import ingest_all, summary, upsert_matches, upsert_players, upsert_teams


def main() -> None:
    parser = argparse.ArgumentParser(description="EPL crawler ingestion CLI")
    parser.add_argument(
        "command",
        choices=["ingest-all", "ingest-teams", "ingest-players", "ingest-matches", "summary"],
        help="command to execute",
    )

    args = parser.parse_args()

    config = load_db_config()
    db = Database.connect(config)

    try:
        db.bootstrap()

        if args.command == "ingest-all":
            ingest_all(db)
            db.commit()
        elif args.command == "ingest-teams":
            upsert_teams(db)
            db.commit()
        elif args.command == "ingest-players":
            upsert_players(db)
            db.commit()
        elif args.command == "ingest-matches":
            upsert_matches(db)
            db.commit()

        print(json.dumps(summary(db), ensure_ascii=False))
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
