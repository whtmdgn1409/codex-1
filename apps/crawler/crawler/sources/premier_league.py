from __future__ import annotations

import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from crawler.config import SourceConfig
from crawler.logging_utils import log_event
from crawler.sources.base import DataSource
from crawler.sources.types import MatchPayload, MatchStatPayload, PlayerPayload, TeamPayload


@dataclass
class _Table:
    headers: list[str]
    rows: list[list[str]]


class _SimpleTableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_table = False
        self._in_header = False
        self._in_cell = False
        self._current_headers: list[str] = []
        self._current_rows: list[list[str]] = []
        self._current_row: list[str] = []
        self._current_text: list[str] = []
        self.tables: list[_Table] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "table":
            self._in_table = True
            self._current_headers = []
            self._current_rows = []
            self._current_row = []
            return
        if not self._in_table:
            return
        if tag == "th":
            self._in_header = True
            self._current_text = []
            return
        if tag == "td":
            self._in_cell = True
            self._current_text = []
            return
        if tag == "tr":
            self._current_row = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "table" and self._in_table:
            self._in_table = False
            self.tables.append(_Table(headers=list(self._current_headers), rows=list(self._current_rows)))
            self._current_headers = []
            self._current_rows = []
            return
        if not self._in_table:
            return
        if tag == "th" and self._in_header:
            self._in_header = False
            value = "".join(self._current_text).strip().lower()
            if value:
                self._current_headers.append(value)
            return
        if tag == "td" and self._in_cell:
            self._in_cell = False
            value = "".join(self._current_text).strip()
            self._current_row.append(value)
            return
        if tag == "tr" and self._current_row:
            self._current_rows.append(list(self._current_row))
            self._current_row = []

    def handle_data(self, data: str) -> None:
        if self._in_header or self._in_cell:
            self._current_text.append(data)


def _safe_int(value: str) -> int | None:
    try:
        return int(value.strip())
    except Exception:
        return None


def _safe_float(value: str) -> float | None:
    normalized = value.replace("%", "").strip()
    try:
        return float(normalized)
    except Exception:
        return None


class PremierLeagueDataSource(DataSource):
    def __init__(self, config: SourceConfig) -> None:
        self.config = config

    def load_teams(self) -> list[TeamPayload]:
        html = self._fetch_with_retry(self.config.teams_url, "pl.fetch.teams")
        return self._parse_teams(html)

    def load_players(self) -> list[PlayerPayload]:
        html = self._fetch_with_retry(self.config.players_url, "pl.fetch.players")
        return self._parse_players(html)

    def load_matches(self) -> list[MatchPayload]:
        html = self._fetch_with_retry(self.config.matches_url, "pl.fetch.matches")
        return self._parse_matches(html)

    def load_match_stats(self) -> list[MatchStatPayload]:
        html = self._fetch_with_retry(self.config.match_stats_url, "pl.fetch.match_stats")
        return self._parse_match_stats(html)

    def _fetch_with_retry(self, url: str, event_name: str) -> str:
        last_error: Exception | None = None
        for attempt in range(1, self.config.retry_count + 1):
            try:
                html = self._http_get(url)
                log_event("INFO", event_name, url=url, attempt=attempt, status="success")
                return html
            except Exception as exc:
                last_error = exc
                log_event("ERROR", event_name, url=url, attempt=attempt, error=repr(exc))
                if attempt < self.config.retry_count:
                    time.sleep(self.config.retry_backoff_seconds * attempt)
        assert last_error is not None
        raise last_error

    def _http_get(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": "EPL-Information-Hub-Crawler/1.0"})
        with urlopen(request, timeout=self.config.timeout_seconds) as response:
            return response.read().decode("utf-8", errors="replace")

    def _extract_table_rows(self, html: str) -> tuple[list[str], list[list[str]]]:
        parser = _SimpleTableParser()
        parser.feed(html)
        for table in parser.tables:
            if table.headers and table.rows:
                return table.headers, table.rows
        return [], []

    def _validate_headers(self, dataset: str, headers: list[str], required: list[str]) -> bool:
        missing = [item for item in required if item not in headers]
        if not missing:
            return True
        message = f"missing required headers for {dataset}: {missing}"
        log_event("WARNING", "pl.parse.headers_missing", dataset=dataset, missing=missing, headers=headers)
        if self.config.parse_strict:
            raise ValueError(message)
        return False

    def _parse_teams(self, html: str) -> list[TeamPayload]:
        headers, rows = self._extract_table_rows(html)
        if not rows:
            return []
        idx = {h: i for i, h in enumerate(headers)}
        required = ["name", "short_name", "stadium", "manager"]
        if not self._validate_headers("teams", headers, required):
            return []

        payload: list[TeamPayload] = []
        for row in rows:
            payload.append(
                {
                    "name": row[idx["name"]],
                    "short_name": row[idx["short_name"]],
                    "logo_url": row[idx["logo_url"]] if "logo_url" in idx and idx["logo_url"] < len(row) else "",
                    "stadium": row[idx["stadium"]],
                    "manager": row[idx["manager"]],
                }
            )
        log_event("INFO", "pl.parse.teams", rows=len(payload))
        return payload

    def _parse_players(self, html: str) -> list[PlayerPayload]:
        headers, rows = self._extract_table_rows(html)
        if not rows:
            return []
        idx = {h: i for i, h in enumerate(headers)}
        required = ["player_id", "team_short_name", "name", "position", "jersey_num", "nationality"]
        if not self._validate_headers("players", headers, required):
            return []

        payload: list[PlayerPayload] = []
        for row in rows:
            player_id = _safe_int(row[idx["player_id"]]) or 0
            jersey_num = _safe_int(row[idx["jersey_num"]]) or 0
            payload.append(
                {
                    "player_id": player_id,
                    "team_short_name": row[idx["team_short_name"]],
                    "name": row[idx["name"]],
                    "position": row[idx["position"]],
                    "jersey_num": jersey_num,
                    "nationality": row[idx["nationality"]],
                    "photo_url": row[idx["photo_url"]] if "photo_url" in idx and idx["photo_url"] < len(row) else "",
                }
            )
        log_event("INFO", "pl.parse.players", rows=len(payload))
        return payload

    def _parse_matches(self, html: str) -> list[MatchPayload]:
        headers, rows = self._extract_table_rows(html)
        if not rows:
            return []
        idx = {h: i for i, h in enumerate(headers)}
        required = ["round", "match_date", "home_team_short_name", "away_team_short_name", "status"]
        if not self._validate_headers("matches", headers, required):
            return []

        payload: list[MatchPayload] = []
        for row in rows:
            home_score = _safe_int(row[idx["home_score"]]) if "home_score" in idx and idx["home_score"] < len(row) else None
            away_score = _safe_int(row[idx["away_score"]]) if "away_score" in idx and idx["away_score"] < len(row) else None
            payload.append(
                {
                    "round": _safe_int(row[idx["round"]]) or 0,
                    "match_date": row[idx["match_date"]],
                    "home_team_short_name": row[idx["home_team_short_name"]],
                    "away_team_short_name": row[idx["away_team_short_name"]],
                    "home_score": home_score,
                    "away_score": away_score,
                    "status": row[idx["status"]],
                }
            )
        log_event("INFO", "pl.parse.matches", rows=len(payload))
        return payload

    def _parse_match_stats(self, html: str) -> list[MatchStatPayload]:
        headers, rows = self._extract_table_rows(html)
        if not rows:
            return []
        idx = {h: i for i, h in enumerate(headers)}
        required = [
            "round",
            "home_team_short_name",
            "away_team_short_name",
            "team_short_name",
            "possession",
            "shots",
            "shots_on_target",
            "fouls",
            "corners",
        ]
        if not self._validate_headers("match_stats", headers, required):
            return []

        payload: list[MatchStatPayload] = []
        for row in rows:
            payload.append(
                {
                    "round": _safe_int(row[idx["round"]]) or 0,
                    "home_team_short_name": row[idx["home_team_short_name"]],
                    "away_team_short_name": row[idx["away_team_short_name"]],
                    "team_short_name": row[idx["team_short_name"]],
                    "possession": _safe_float(row[idx["possession"]]) or 0.0,
                    "shots": _safe_int(row[idx["shots"]]) or 0,
                    "shots_on_target": _safe_int(row[idx["shots_on_target"]]) or 0,
                    "fouls": _safe_int(row[idx["fouls"]]) or 0,
                    "corners": _safe_int(row[idx["corners"]]) or 0,
                }
            )
        log_event("INFO", "pl.parse.match_stats", rows=len(payload))
        return payload
