from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class DbConfig:
    engine: str
    path: str | None
    host: str | None
    port: int | None
    user: str | None
    password: str | None
    database: str | None


@dataclass
class SourceConfig:
    source: str
    teams_url: str
    players_url: str
    matches_url: str
    match_stats_url: str
    timeout_seconds: int
    retry_count: int
    retry_backoff_seconds: float


def load_db_config() -> DbConfig:
    db_url = os.getenv("DB_URL", "sqlite:///./apps/crawler/dev_crawler.db")
    parsed = urlparse(db_url)

    if parsed.scheme.startswith("sqlite"):
        raw_path = parsed.path or "./apps/crawler/dev_crawler.db"
        if db_url.startswith("sqlite:////"):
            normalized = raw_path
        else:
            trimmed = raw_path.lstrip("/")
            if not trimmed:
                trimmed = "apps/crawler/dev_crawler.db"
            if trimmed.startswith("."):
                normalized = trimmed
            else:
                normalized = f"./{trimmed}"
        return DbConfig(
            engine="sqlite",
            path=normalized,
            host=None,
            port=None,
            user=None,
            password=None,
            database=None,
        )

    if parsed.scheme.startswith("mysql"):
        return DbConfig(
            engine="mysql",
            path=None,
            host=parsed.hostname or "localhost",
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=(parsed.path or "").lstrip("/"),
        )

    raise ValueError(f"unsupported DB_URL scheme: {parsed.scheme}")


def load_source_config() -> SourceConfig:
    return SourceConfig(
        source=os.getenv("CRAWLER_DATA_SOURCE", "sample").strip().lower(),
        teams_url=os.getenv("PL_TEAMS_URL", "https://www.premierleague.com/en/clubs"),
        players_url=os.getenv("PL_PLAYERS_URL", "https://www.premierleague.com/stats/top/players/goals"),
        matches_url=os.getenv("PL_MATCHES_URL", "https://www.premierleague.com/en/matches"),
        match_stats_url=os.getenv("PL_MATCH_STATS_URL", "https://www.premierleague.com/stats"),
        timeout_seconds=int(os.getenv("PL_HTTP_TIMEOUT_SECONDS", "20")),
        retry_count=int(os.getenv("PL_HTTP_RETRY_COUNT", "3")),
        retry_backoff_seconds=float(os.getenv("PL_HTTP_RETRY_BACKOFF_SECONDS", "1.0")),
    )
