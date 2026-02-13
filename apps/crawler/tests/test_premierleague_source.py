import pytest

from crawler.config import SourceConfig
from crawler.sources import get_data_source
from crawler.sources.premier_league import PremierLeagueDataSource
from crawler.sources.sample_data import SampleDataSource


def _source_config() -> SourceConfig:
    return SourceConfig(
        source="pl",
        teams_url="https://example.com/teams",
        players_url="https://example.com/players",
        matches_url="https://example.com/matches",
        match_stats_url="https://example.com/match-stats",
        timeout_seconds=1,
        retry_count=3,
        retry_backoff_seconds=0.0,
        parse_strict=False,
    )


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


def test_premierleague_parse_teams_from_html(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html><body>
    <table>
      <tr><th>name</th><th>short_name</th><th>logo_url</th><th>stadium</th><th>manager</th></tr>
      <tr><td>Arsenal FC</td><td>ARS</td><td>https://logo/ars.png</td><td>Emirates</td><td>Mikel Arteta</td></tr>
    </table>
    </body></html>
    """
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: html)

    teams = source.load_teams()
    assert len(teams) == 1
    assert teams[0]["short_name"] == "ARS"
    assert teams[0]["manager"] == "Mikel Arteta"


def test_premierleague_parse_matches_from_html(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html><body>
    <table>
      <tr><th>round</th><th>match_date</th><th>home_team_short_name</th><th>away_team_short_name</th><th>home_score</th><th>away_score</th><th>status</th></tr>
      <tr><td>1</td><td>2025-08-10 20:00:00</td><td>ARS</td><td>CHE</td><td>2</td><td>1</td><td>FINISHED</td></tr>
    </table>
    </body></html>
    """
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: html)

    matches = source.load_matches()
    assert len(matches) == 1
    assert matches[0]["round"] == 1
    assert matches[0]["home_score"] == 2
    assert matches[0]["away_team_short_name"] == "CHE"


def test_premierleague_fetch_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    attempts = {"count": 0}
    html = """
    <html><body>
    <table>
      <tr><th>name</th><th>short_name</th><th>stadium</th><th>manager</th></tr>
      <tr><td>Liverpool FC</td><td>LIV</td><td>Anfield</td><td>Arne Slot</td></tr>
    </table>
    </body></html>
    """

    def flaky(_: str) -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("transient")
        return html

    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", flaky)

    teams = source.load_teams()
    assert len(teams) == 1
    assert attempts["count"] == 3


def test_premierleague_parse_non_strict_returns_empty_on_missing_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html><body>
    <table>
      <tr><th>club</th><th>abbr</th></tr>
      <tr><td>Arsenal FC</td><td>ARS</td></tr>
    </table>
    </body></html>
    """
    source = PremierLeagueDataSource(_source_config())
    monkeypatch.setattr(source, "_http_get", lambda _: html)

    teams = source.load_teams()
    assert teams == []


def test_premierleague_parse_strict_raises_on_missing_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    html = """
    <html><body>
    <table>
      <tr><th>club</th><th>abbr</th></tr>
      <tr><td>Arsenal FC</td><td>ARS</td></tr>
    </table>
    </body></html>
    """
    config = _source_config()
    config.parse_strict = True
    source = PremierLeagueDataSource(config)
    monkeypatch.setattr(source, "_http_get", lambda _: html)

    with pytest.raises(ValueError):
        source.load_teams()
