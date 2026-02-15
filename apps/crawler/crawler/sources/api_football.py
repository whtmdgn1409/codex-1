from __future__ import annotations

import json
import ssl
import time
from datetime import datetime, timezone
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from crawler.config import SourceConfig
from crawler.logging_utils import log_event
from crawler.sources.base import DataSource
from crawler.sources.types import MatchPayload, MatchStatPayload, PlayerPayload, StandingPayload, TeamPayload


def _safe_int(value: object) -> int | None:
    try:
        return int(value)  # type: ignore[arg-type]
    except Exception:
        return None


def _derive_short_name(name: str, code: str | None) -> str:
    if code:
        code_norm = code.strip().upper()
        if code_norm:
            return code_norm[:10]
    tokens = [token for token in name.replace("-", " ").split() if token]
    if not tokens:
        return "UNK"
    if len(tokens) >= 2:
        return "".join(token[0] for token in tokens[:3]).upper()
    return tokens[0][:3].upper()


def _to_sql_datetime(timestamp_value: object) -> str:
    timestamp = _safe_int(timestamp_value)
    if timestamp is None:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class ApiFootballDataSource(DataSource):
    def __init__(self, config: SourceConfig) -> None:
        self.config = config
        self._team_id_to_short: dict[int, str] = {}
        self._fixture_contexts: list[dict[str, int | str]] = []

    def load_teams(self) -> list[TeamPayload]:
        payload = self._fetch_dataset("teams", "/teams", {"league": self.config.api_football_league_id, "season": self.config.api_football_season})
        if payload is None:
            return []

        rows = payload.get("response", [])
        teams: list[TeamPayload] = []
        for row in rows:
            team_info = row.get("team", {})
            venue_info = row.get("venue", {})
            team_id = _safe_int(team_info.get("id"))
            name = str(team_info.get("name", "")).strip()
            if not name:
                continue
            short_name = _derive_short_name(name=name, code=team_info.get("code"))
            if team_id is not None:
                self._team_id_to_short[team_id] = short_name
            teams.append(
                {
                    "name": name,
                    "short_name": short_name,
                    "logo_url": str(team_info.get("logo", "") or ""),
                    "stadium": str(venue_info.get("name", "") or ""),
                    "manager": "",
                }
            )

        log_event("INFO", "api_football.parse.teams", rows=len(teams))
        return teams

    def load_players(self) -> list[PlayerPayload]:
        self._prime_team_short_names()

        players_by_id: dict[int, PlayerPayload] = {}
        page = 1
        total_pages = 1

        while page <= total_pages:
            payload = self._fetch_dataset(
                "players",
                "/players",
                {
                    "league": self.config.api_football_league_id,
                    "season": self.config.api_football_season,
                    "page": page,
                },
            )
            if payload is None:
                return list(players_by_id.values())

            paging = payload.get("paging", {})
            total_pages = max(1, _safe_int(paging.get("total")) or 1)
            response_rows = payload.get("response", [])

            for row in response_rows:
                player_info = row.get("player", {})
                player_id = _safe_int(player_info.get("id"))
                name = str(player_info.get("name", "")).strip()
                if player_id is None or not name:
                    continue

                stat_rows = row.get("statistics", [])
                primary_stat = stat_rows[0] if stat_rows else {}

                team_info = primary_stat.get("team", {})
                team_id = _safe_int(team_info.get("id"))
                team_short = self._resolve_team_short_name(
                    team_id=team_id,
                    team_name=str(team_info.get("name", "")),
                    team_code=team_info.get("code"),
                )
                if not team_short:
                    continue

                games = primary_stat.get("games", {})
                position = str(games.get("position", "") or "").strip() or "UNK"

                players_by_id[player_id] = {
                    "player_id": player_id,
                    "team_short_name": team_short,
                    "name": name,
                    "position": position[:10],
                    "jersey_num": _safe_int(games.get("number")),
                    "nationality": str(player_info.get("nationality", "") or ""),
                    "photo_url": str(player_info.get("photo", "") or ""),
                }

            page += 1

        items = list(players_by_id.values())
        log_event("INFO", "api_football.parse.players", rows=len(items))
        return items

    def load_matches(self) -> list[MatchPayload]:
        self._prime_team_short_names()

        payload = self._fetch_dataset("matches", "/fixtures", {"league": self.config.api_football_league_id, "season": self.config.api_football_season})
        if payload is None:
            return []

        rows = payload.get("response", [])
        matches: list[MatchPayload] = []
        for row in rows:
            fixture = row.get("fixture", {})
            league = row.get("league", {})
            teams = row.get("teams", {})
            goals = row.get("goals", {})
            status = fixture.get("status", {})

            home = teams.get("home", {})
            away = teams.get("away", {})
            home_id = _safe_int(home.get("id"))
            away_id = _safe_int(away.get("id"))
            if home_id is None or away_id is None:
                continue

            home_short = self._team_id_to_short.get(home_id)
            away_short = self._team_id_to_short.get(away_id)
            if not home_short:
                home_short = _derive_short_name(name=str(home.get("name", "")), code=home.get("code"))
                self._team_id_to_short[home_id] = home_short
            if not away_short:
                away_short = _derive_short_name(name=str(away.get("name", "")), code=away.get("code"))
                self._team_id_to_short[away_id] = away_short
            if not home_short or not away_short:
                continue

            round_raw = str(league.get("round", "0"))
            round_num = 0
            for token in round_raw.replace("-", " ").split():
                token_num = _safe_int(token)
                if token_num is not None:
                    round_num = token_num
                    break

            short_status = str(status.get("short", "")).upper()
            is_finished = short_status in {"FT", "AET", "PEN", "AWD", "WO"}
            fixture_id = _safe_int(fixture.get("id"))
            if fixture_id is not None:
                self._fixture_contexts.append(
                    {
                        "fixture_id": fixture_id,
                        "round": round_num,
                        "home_team_id": home_id,
                        "away_team_id": away_id,
                        "status": "FINISHED" if is_finished else "SCHEDULED",
                    }
                )
            matches.append(
                {
                    "round": round_num,
                    "match_date": _to_sql_datetime(fixture.get("timestamp")),
                    "home_team_short_name": home_short,
                    "away_team_short_name": away_short,
                    "home_score": _safe_int(goals.get("home")),
                    "away_score": _safe_int(goals.get("away")),
                    "status": "FINISHED" if is_finished else "SCHEDULED",
                }
            )

        log_event("INFO", "api_football.parse.matches", rows=len(matches))
        return matches

    def load_match_stats(self) -> list[MatchStatPayload]:
        self._prime_fixture_contexts()
        if not self._fixture_contexts:
            log_event("WARNING", "api_football.parse.match_stats.empty_fixture_context")
            return []

        payload_rows: list[MatchStatPayload] = []

        for context in self._fixture_contexts:
            if context.get("status") != "FINISHED":
                continue
            fixture_id = int(context["fixture_id"])
            round_num = int(context["round"])
            home_team_id = int(context["home_team_id"])
            away_team_id = int(context["away_team_id"])

            payload = self._fetch_dataset("match_stats", "/fixtures/statistics", {"fixture": fixture_id})
            if payload is None:
                continue

            for row in payload.get("response", []):
                team = row.get("team", {})
                team_id = _safe_int(team.get("id"))
                team_short = self._resolve_team_short_name(
                    team_id=team_id,
                    team_name=str(team.get("name", "")),
                    team_code=team.get("code"),
                )
                if not team_short:
                    continue

                stat_map = self._statistics_map(row.get("statistics", []))
                possession = _to_float_percent(stat_map.get("Ball Possession"))
                shots = _safe_int(stat_map.get("Total Shots")) or 0
                shots_on_target = _safe_int(stat_map.get("Shots on Goal")) or 0
                fouls = _safe_int(stat_map.get("Fouls")) or _safe_int(stat_map.get("Fouls Committed")) or 0
                corners = _safe_int(stat_map.get("Corner Kicks")) or 0

                home_short = self._team_id_to_short.get(home_team_id, "")
                away_short = self._team_id_to_short.get(away_team_id, "")
                if not home_short or not away_short:
                    continue

                payload_rows.append(
                    {
                        "round": round_num,
                        "home_team_short_name": home_short,
                        "away_team_short_name": away_short,
                        "team_short_name": team_short,
                        "possession": possession if possession is not None else 0.0,
                        "shots": shots,
                        "shots_on_target": shots_on_target,
                        "fouls": fouls,
                        "corners": corners,
                    }
                )

        log_event("INFO", "api_football.parse.match_stats", rows=len(payload_rows))
        return payload_rows

    def load_standings(self) -> list[StandingPayload]:
        self._prime_team_short_names()

        payload = self._fetch_dataset("standings", "/standings", {"league": self.config.api_football_league_id, "season": self.config.api_football_season})
        if payload is None:
            return []

        response_rows = payload.get("response", [])
        if not response_rows:
            return []

        standings_groups = response_rows[0].get("league", {}).get("standings", [])
        if not standings_groups:
            return []

        items: list[StandingPayload] = []
        for row in standings_groups[0]:
            team_info = row.get("team", {})
            team_id = _safe_int(team_info.get("id"))
            if team_id is None:
                continue
            short_name = self._team_id_to_short.get(team_id)
            if not short_name:
                short_name = _derive_short_name(name=str(team_info.get("name", "")), code=team_info.get("code"))
                self._team_id_to_short[team_id] = short_name
            if not short_name:
                continue

            all_stats = row.get("all", {})
            goals = all_stats.get("goals", {})
            goals_for = _safe_int(goals.get("for")) or 0
            goals_against = _safe_int(goals.get("against")) or 0

            items.append(
                {
                    "team_short_name": short_name,
                    "rank": _safe_int(row.get("rank")) or 0,
                    "played": _safe_int(all_stats.get("played")) or 0,
                    "won": _safe_int(all_stats.get("win")) or 0,
                    "drawn": _safe_int(all_stats.get("draw")) or 0,
                    "lost": _safe_int(all_stats.get("lose")) or 0,
                    "goals_for": goals_for,
                    "goals_against": goals_against,
                    "goal_diff": _safe_int(row.get("goalsDiff")) or (goals_for - goals_against),
                    "points": _safe_int(row.get("points")) or 0,
                }
            )

        log_event("INFO", "api_football.parse.standings", rows=len(items))
        return items

    def _prime_team_short_names(self) -> None:
        if self._team_id_to_short:
            return
        try:
            self.load_teams()
        except Exception as exc:
            log_event("WARNING", "api_football.team_map.prime_failed", reason=repr(exc))

    def _prime_fixture_contexts(self) -> None:
        if self._fixture_contexts:
            return
        try:
            self.load_matches()
        except Exception as exc:
            log_event("WARNING", "api_football.fixture_context.prime_failed", reason=repr(exc))

    def _resolve_team_short_name(self, *, team_id: int | None, team_name: str, team_code: object) -> str | None:
        if team_id is not None:
            existing = self._team_id_to_short.get(team_id)
            if existing:
                return existing
        derived = _derive_short_name(name=team_name, code=team_code if isinstance(team_code, str) else None)
        if team_id is not None and derived:
            self._team_id_to_short[team_id] = derived
        return derived or None

    def _statistics_map(self, rows: list[dict]) -> dict[str, object]:
        items: dict[str, object] = {}
        for row in rows:
            key = str(row.get("type", "")).strip()
            if not key:
                continue
            items[key] = row.get("value")
        return items

    def _fetch_dataset(self, dataset: str, path: str, params: dict[str, object]) -> dict | None:
        try:
            return self._fetch_with_retry(path=path, params=params, event_name=f"api_football.fetch.{dataset}")
        except Exception as exc:
            policy = self._dataset_policy(dataset)
            log_event("ERROR", "api_football.dataset.failure", dataset=dataset, policy=policy, reason=repr(exc))
            if policy == "abort":
                raise
            return None

    def _fetch_with_retry(self, *, path: str, params: dict[str, object], event_name: str) -> dict:
        last_error: Exception | None = None
        for attempt in range(1, self.config.retry_count + 1):
            try:
                data = self._http_get_json(path=path, params=params)
                log_event("INFO", event_name, path=path, attempt=attempt, status="success")
                return data
            except Exception as exc:
                last_error = exc
                log_event("ERROR", event_name, path=path, attempt=attempt, error=repr(exc))
                if attempt < self.config.retry_count:
                    time.sleep(self.config.retry_backoff_seconds * attempt)
        assert last_error is not None
        raise last_error

    def _dataset_policy(self, dataset: str) -> str:
        if dataset == "teams":
            return self.config.dataset_policy_teams
        if dataset == "players":
            return self.config.dataset_policy_players
        if dataset == "matches":
            return self.config.dataset_policy_matches
        if dataset == "match_stats":
            return self.config.dataset_policy_match_stats
        if dataset == "standings":
            return self.config.dataset_policy_standings
        return "abort"

    def _http_get_json(self, *, path: str, params: dict[str, object]) -> dict:
        if not self.config.api_football_key:
            raise ValueError("API_FOOTBALL_KEY is required")
        query = urlencode({k: v for k, v in params.items() if v is not None})
        url = f"{self.config.api_football_base_url.rstrip('/')}{path}?{query}"
        request = Request(
            url,
            headers={
                "User-Agent": "EPL-Information-Hub-Crawler/1.0",
                "x-apisports-key": self.config.api_football_key,
            },
        )
        if self.config.api_football_host:
            request.add_header("x-apisports-host", self.config.api_football_host)

        if self.config.verify_ssl:
            context = ssl.create_default_context(cafile=self.config.ca_file)
        else:
            context = ssl._create_unverified_context()
            log_event("WARNING", "api_football.http.ssl_verify_disabled", url=url)

        with urlopen(request, timeout=self.config.timeout_seconds, context=context) as response:
            raw = response.read().decode("utf-8", errors="replace")
            return json.loads(raw)


def _to_float_percent(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None
