from __future__ import annotations

from crawler.sources.types import MatchPayload

# Fallback fixtures used when official matches parsing fails in live environments.
SEED_MATCHES: list[MatchPayload] = [
    {
        "round": 1,
        "match_date": "2026-08-15 20:00:00",
        "home_team_short_name": "ARS",
        "away_team_short_name": "LIV",
        "home_score": 2,
        "away_score": 1,
        "status": "FINISHED",
    },
    {
        "round": 2,
        "match_date": "2026-08-22 20:00:00",
        "home_team_short_name": "LIV",
        "away_team_short_name": "ARS",
        "home_score": None,
        "away_score": None,
        "status": "SCHEDULED",
    },
]


def load_seed_matches() -> list[MatchPayload]:
    return list(SEED_MATCHES)
