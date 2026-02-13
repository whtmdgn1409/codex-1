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
