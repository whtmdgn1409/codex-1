from __future__ import annotations

import pytest

from crawler.config import SourceConfig
from crawler.sources.api_football import ApiFootballDataSource
from crawler.sources.types import MatchPayload, StandingPayload, TeamPayload


def _source_config() -> SourceConfig:
    return SourceConfig(
        source="api_football",
        teams_url="",
        players_url="",
        matches_url="",
        match_stats_url="",
        timeout_seconds=1,
        verify_ssl=True,
        ca_file=None,
        retry_count=2,
        retry_backoff_seconds=0.0,
        parse_strict=False,
        dataset_policy_teams="abort",
        dataset_policy_players="skip",
        dataset_policy_matches="abort",
        dataset_policy_match_stats="skip",
        dataset_policy_standings="abort",
        teams_seed_fallback=False,
        matches_seed_fallback=False,
        api_football_base_url="https://v3.football.api-sports.io",
        api_football_key="test-key",
        api_football_host=None,
        api_football_league_id=39,
        api_football_season=2025,
    )


def _fake_response(path: str) -> dict:
    if path == "/teams":
        return {
            "response": [
                {
                    "team": {"id": 42, "name": "Arsenal", "code": "ARS", "logo": "https://example.com/ars.png"},
                    "venue": {"name": "Emirates Stadium"},
                },
                {
                    "team": {"id": 40, "name": "Liverpool", "code": "LIV", "logo": "https://example.com/liv.png"},
                    "venue": {"name": "Anfield"},
                },
            ]
        }
    if path == "/fixtures":
        return {
            "response": [
                {
                    "fixture": {"id": 9001, "timestamp": 1765406400, "status": {"short": "FT"}},
                    "league": {"round": "Regular Season - 19"},
                    "teams": {
                        "home": {"id": 42, "name": "Arsenal", "code": "ARS"},
                        "away": {"id": 40, "name": "Liverpool", "code": "LIV"},
                    },
                    "goals": {"home": 2, "away": 1},
                },
                {
                    "fixture": {"id": 9002, "timestamp": 1766000000, "status": {"short": "NS"}},
                    "league": {"round": "Regular Season - 20"},
                    "teams": {
                        "home": {"id": 40, "name": "Liverpool", "code": "LIV"},
                        "away": {"id": 42, "name": "Arsenal", "code": "ARS"},
                    },
                    "goals": {"home": None, "away": None},
                },
            ]
        }
    if path == "/players":
        return {
            "paging": {"current": 1, "total": 1},
            "response": [
                {
                    "player": {
                        "id": 1001,
                        "name": "Bukayo Saka",
                        "nationality": "England",
                        "photo": "https://example.com/saka.png",
                    },
                    "statistics": [
                        {
                            "team": {"id": 42, "name": "Arsenal"},
                            "games": {"position": "Attacker", "number": 7},
                        }
                    ],
                },
                {
                    "player": {
                        "id": 1002,
                        "name": "Mohamed Salah",
                        "nationality": "Egypt",
                        "photo": "https://example.com/salah.png",
                    },
                    "statistics": [
                        {
                            "team": {"id": 40, "name": "Liverpool"},
                            "games": {"position": "Attacker", "number": 11},
                        }
                    ],
                },
            ],
        }
    if path == "/fixtures/statistics":
        return {
            "response": [
                {
                    "team": {"id": 42, "name": "Arsenal"},
                    "statistics": [
                        {"type": "Ball Possession", "value": "55%"},
                        {"type": "Total Shots", "value": 14},
                        {"type": "Shots on Goal", "value": 6},
                        {"type": "Fouls", "value": 10},
                        {"type": "Corner Kicks", "value": 7},
                    ],
                },
                {
                    "team": {"id": 40, "name": "Liverpool"},
                    "statistics": [
                        {"type": "Ball Possession", "value": "45%"},
                        {"type": "Total Shots", "value": 9},
                        {"type": "Shots on Goal", "value": 4},
                        {"type": "Fouls", "value": 12},
                        {"type": "Corner Kicks", "value": 3},
                    ],
                },
            ]
        }
    if path == "/standings":
        return {
            "response": [
                {
                    "league": {
                        "standings": [
                            [
                                {
                                    "rank": 1,
                                    "points": 58,
                                    "goalsDiff": 35,
                                    "team": {"id": 42},
                                    "all": {"played": 24, "win": 18, "draw": 4, "lose": 2, "goals": {"for": 55, "against": 20}},
                                },
                                {
                                    "rank": 2,
                                    "points": 56,
                                    "goalsDiff": 31,
                                    "team": {"id": 40},
                                    "all": {"played": 24, "win": 17, "draw": 5, "lose": 2, "goals": {"for": 53, "against": 22}},
                                },
                            ]
                        ]
                    }
                }
            ]
        }
    return {"response": []}


def test_api_football_parses_teams_matches_and_standings(monkeypatch: pytest.MonkeyPatch) -> None:
    source = ApiFootballDataSource(_source_config())

    def fake_http_get_json(*, path: str, params: dict[str, object]) -> dict:
        if path in {"/teams", "/fixtures", "/standings", "/players"}:
            assert params["league"] == 39
            assert params["season"] == 2025
        if path == "/players":
            assert params["page"] == 1
        if path == "/fixtures/statistics":
            assert params["fixture"] == 9001
        return _fake_response(path)

    monkeypatch.setattr(source, "_http_get_json", fake_http_get_json)

    teams: list[TeamPayload] = source.load_teams()
    players = source.load_players()
    matches: list[MatchPayload] = source.load_matches()
    match_stats = source.load_match_stats()
    standings: list[StandingPayload] = source.load_standings()

    assert len(teams) == 2
    assert teams[0]["short_name"] == "ARS"
    assert len(players) == 2
    assert players[0]["team_short_name"] == "ARS"
    assert len(matches) == 2
    assert matches[0]["status"] == "FINISHED"
    assert matches[1]["status"] == "SCHEDULED"
    assert len(match_stats) == 2
    assert match_stats[0]["round"] == 19
    assert match_stats[0]["possession"] == 55.0
    assert len(standings) == 2
    assert standings[0]["team_short_name"] == "ARS"
    assert standings[0]["points"] == 58


def test_api_football_honors_skip_policy_for_standings(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _source_config()
    config.dataset_policy_standings = "skip"
    source = ApiFootballDataSource(config)

    def failing_http_get_json(*, path: str, params: dict[str, object]) -> dict:
        raise RuntimeError(f"boom:{path}")

    monkeypatch.setattr(source, "_http_get_json", failing_http_get_json)
    assert source.load_standings() == []


def test_api_football_honors_skip_policy_for_players_and_match_stats(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _source_config()
    config.dataset_policy_players = "skip"
    config.dataset_policy_match_stats = "skip"
    source = ApiFootballDataSource(config)

    def failing_http_get_json(*, path: str, params: dict[str, object]) -> dict:
        if path in {"/players", "/fixtures/statistics"}:
            raise RuntimeError(f"boom:{path}")
        return _fake_response(path)

    monkeypatch.setattr(source, "_http_get_json", failing_http_get_json)

    assert source.load_players() == []
    assert source.load_match_stats() == []


def test_api_football_builds_standings_from_matches_when_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    source = ApiFootballDataSource(_source_config())

    def fake_http_get_json(*, path: str, params: dict[str, object]) -> dict:
        if path == "/standings":
            return {"response": []}
        return _fake_response(path)

    monkeypatch.setattr(source, "_http_get_json", fake_http_get_json)
    standings = source.load_standings()

    assert len(standings) == 2
    assert standings[0]["team_short_name"] == "ARS"
    assert standings[0]["points"] == 3
