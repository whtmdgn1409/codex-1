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
    verify_ssl: bool
    ca_file: str | None
    retry_count: int
    retry_backoff_seconds: float
    parse_strict: bool
    dataset_policy_teams: str
    dataset_policy_players: str
    dataset_policy_matches: str
    dataset_policy_match_stats: str


@dataclass
class BatchPolicyConfig:
    retry_count: int
    retry_backoff_seconds: float


@dataclass
class AlertConfig:
    slack_webhook_url: str | None
    timeout_seconds: int


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
    parse_strict_raw = os.getenv("PL_PARSE_STRICT", "0").strip().lower()
    verify_ssl_raw = os.getenv("PL_HTTP_VERIFY_SSL", "1").strip().lower()
    ca_file_raw = os.getenv("PL_HTTP_CA_FILE", "").strip()
    return SourceConfig(
        source=os.getenv("CRAWLER_DATA_SOURCE", "sample").strip().lower(),
        teams_url=os.getenv("PL_TEAMS_URL", "https://www.premierleague.com/en/clubs"),
        players_url=os.getenv("PL_PLAYERS_URL", "https://www.premierleague.com/stats/top/players/goals"),
        matches_url=os.getenv("PL_MATCHES_URL", "https://www.premierleague.com/en/matches"),
        match_stats_url=os.getenv("PL_MATCH_STATS_URL", "https://www.premierleague.com/stats"),
        timeout_seconds=int(os.getenv("PL_HTTP_TIMEOUT_SECONDS", "20")),
        verify_ssl=verify_ssl_raw in {"1", "true", "yes", "on"},
        ca_file=ca_file_raw or None,
        retry_count=int(os.getenv("PL_HTTP_RETRY_COUNT", "3")),
        retry_backoff_seconds=float(os.getenv("PL_HTTP_RETRY_BACKOFF_SECONDS", "1.0")),
        parse_strict=parse_strict_raw in {"1", "true", "yes", "on"},
        dataset_policy_teams=os.getenv("PL_POLICY_TEAMS", "abort").strip().lower(),
        dataset_policy_players=os.getenv("PL_POLICY_PLAYERS", "skip").strip().lower(),
        dataset_policy_matches=os.getenv("PL_POLICY_MATCHES", "abort").strip().lower(),
        dataset_policy_match_stats=os.getenv("PL_POLICY_MATCH_STATS", "skip").strip().lower(),
    )


def load_batch_policy_config() -> BatchPolicyConfig:
    retry_count = int(os.getenv("BATCH_RETRY_COUNT", "1"))
    if retry_count < 1:
        retry_count = 1
    return BatchPolicyConfig(
        retry_count=retry_count,
        retry_backoff_seconds=float(os.getenv("BATCH_RETRY_BACKOFF_SECONDS", "1.0")),
    )


def load_alert_config() -> AlertConfig:
    webhook = os.getenv("BATCH_ALERT_SLACK_WEBHOOK")
    return AlertConfig(
        slack_webhook_url=webhook.strip() if webhook and webhook.strip() else None,
        timeout_seconds=int(os.getenv("BATCH_ALERT_TIMEOUT_SECONDS", "10")),
    )
