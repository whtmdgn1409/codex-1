from __future__ import annotations

from pathlib import Path

import pytest

from crawler.config import SourceConfig
from crawler.sources import get_data_source
from crawler.sources.premier_league import PremierLeagueDataSource
from crawler.sources.sample_data import SampleDataSource


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "premier_league"


def _source_config() -> SourceConfig:
    return SourceConfig(
        source="pl",
        teams_url="https://example.com/teams",
        players_url="https://example.com/players",
        matches_url="https://example.com/matches",
        match_stats_url="https://example.com/match-stats",
        timeout_seconds=1,
        verify_ssl=True,
        ca_file=None,
        retry_count=3,
        retry_backoff_seconds=0.0,
        parse_strict=False,
        dataset_policy_teams="skip",
        dataset_policy_players="skip",
        dataset_policy_matches="skip",
        dataset_policy_match_stats="skip",
        teams_seed_fallback=True,
    )


def _fixture_html(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


def test_get_data_source_default_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CRAWLER_DATA_SOURCE", raising=False)
    source = get_data_source()
    assert isinstance(source, SampleDataSource)


def test_get_data_source_premierleague(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRAWLER_DATA_SOURCE", "pl")
    source = get_data_source()
    assert isinstance(source, PremierLeagueDataSource)


def test_get_data_source_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CRAWLER_DATA_SOURCE", "unknown")
    with pytest.raises(ValueError):
        get_data_source()


def test_premierleague_parse_teams_aliases_from_official_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: _fixture_html("teams_official.html"))

    teams = source.load_teams()

    assert len(teams) == 2
    assert teams[0]["name"] == "Arsenal FC"
    assert teams[0]["short_name"] == "ARS"
    assert teams[0]["manager"] == "Mikel Arteta"
    assert teams[1]["stadium"] == "Anfield"


def test_premierleague_parse_teams_from_pulse_assignment_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: _fixture_html("teams_pulse_assignment.html"))

    teams = source.load_teams()

    assert len(teams) == 2
    assert teams[0]["name"] == "Arsenal FC"
    assert teams[0]["short_name"] == "ARS"
    assert teams[0]["manager"] == "Mikel Arteta"
    assert teams[1]["stadium"] == "Anfield"


def test_premierleague_parse_teams_from_links_fallback_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: _fixture_html("teams_links_fallback.html"))

    teams = source.load_teams()

    assert len(teams) == 3
    assert teams[0]["name"] == "Arsenal"
    assert teams[0]["short_name"] == "ARS"
    assert teams[1]["name"] == "Liverpool"
    assert teams[2]["name"] == "Manchester City"


def test_premierleague_json_fallback_for_matches_from_next_data_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: _fixture_html("matches_official.html"))

    matches = source.load_matches()

    assert len(matches) == 2
    assert matches[0]["round"] == 24
    assert matches[0]["match_date"] == "2026-02-08 20:00:00"
    assert matches[0]["home_team_short_name"] == "ARS"
    assert matches[0]["away_team_short_name"] == "CHE"
    assert matches[0]["home_score"] == 2
    assert matches[0]["away_score"] == 1
    assert matches[1]["status"] == "SCHEDULED"
    assert matches[1]["home_score"] is None


def test_premierleague_json_fallback_for_match_stats_nested_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: _fixture_html("match_stats_official.html"))

    stats = source.load_match_stats()

    assert len(stats) == 2
    assert stats[0]["round"] == 24
    assert stats[0]["team_short_name"] == "ARS"
    assert stats[0]["possession"] == pytest.approx(61.2)
    assert stats[0]["shots"] == 14
    assert stats[0]["shots_on_target"] == 6
    assert stats[1]["team_short_name"] == "CHE"
    assert stats[1]["corners"] == 3


def test_dataset_policy_skip_returns_empty_when_no_records(monkeypatch: pytest.MonkeyPatch) -> None:
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: "<html><body><div>empty</div></body></html>")

    assert source.load_matches() == []


def test_dataset_policy_abort_raises_when_no_records(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _source_config()
    config.dataset_policy_match_stats = "abort"
    source = PremierLeagueDataSource(config)
    monkeypatch.setattr(source, "_http_get", lambda _: "<html><body><div>empty</div></body></html>")

    with pytest.raises(ValueError):
        source.load_match_stats()


def test_teams_seed_fallback_returns_seed_when_parse_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _source_config()
    config.dataset_policy_teams = "abort"
    config.teams_seed_fallback = True
    source = PremierLeagueDataSource(config)
    monkeypatch.setattr(source, "_http_get", lambda _: "<html><body><div>empty</div></body></html>")

    teams = source.load_teams()

    assert len(teams) >= 20
    assert any(team["short_name"] == "ARS" for team in teams)


def test_teams_seed_fallback_disabled_honors_abort_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _source_config()
    config.dataset_policy_teams = "abort"
    config.teams_seed_fallback = False
    source = PremierLeagueDataSource(config)
    monkeypatch.setattr(source, "_http_get", lambda _: "<html><body><div>empty</div></body></html>")

    with pytest.raises(ValueError):
        source.load_teams()


def test_premierleague_fetch_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = {"count": 0}
    html = _fixture_html("teams_official.html")

    def flaky(_: str) -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("transient")
        return html

    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", flaky)

    teams = source.load_teams()
    assert len(teams) == 2
    assert attempts["count"] == 3
