from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from crawler.config import SourceConfig
from crawler.logging_utils import log_event
from crawler.sources.base import DataSource
from crawler.sources.types import MatchPayload, MatchStatPayload, PlayerPayload, TeamPayload

Dataset = str

TEAM_ALIASES: dict[str, list[str]] = {
    "name": ["name", "club", "team", "team_name"],
    "short_name": ["short_name", "abbr", "short", "code", "team_short_name"],
    "logo_url": ["logo_url", "logo", "crest", "image_url"],
    "stadium": ["stadium", "venue", "ground"],
    "manager": ["manager", "coach", "head_coach"],
}

PLAYER_ALIASES: dict[str, list[str]] = {
    "player_id": ["player_id", "id"],
    "team_short_name": ["team_short_name", "team", "club", "team_code"],
    "name": ["name", "player", "player_name"],
    "position": ["position", "pos"],
    "jersey_num": ["jersey_num", "shirt_number", "number"],
    "nationality": ["nationality", "nation", "country"],
    "photo_url": ["photo_url", "photo", "image_url"],
}

MATCH_ALIASES: dict[str, list[str]] = {
    "round": ["round", "matchweek", "week", "gw"],
    "match_date": ["match_date", "date", "kickoff", "kickoff_time"],
    "home_team_short_name": ["home_team_short_name", "home_team", "home"],
    "away_team_short_name": ["away_team_short_name", "away_team", "away"],
    "home_score": ["home_score", "home_goals", "score_home"],
    "away_score": ["away_score", "away_goals", "score_away"],
    "status": ["status", "result_status", "state"],
}

MATCH_STATS_ALIASES: dict[str, list[str]] = {
    "round": ["round", "matchweek", "week", "gw"],
    "home_team_short_name": ["home_team_short_name", "home_team", "home"],
    "away_team_short_name": ["away_team_short_name", "away_team", "away"],
    "team_short_name": ["team_short_name", "team", "club"],
    "possession": ["possession", "possession_pct"],
    "shots": ["shots", "total_shots"],
    "shots_on_target": ["shots_on_target", "shots_ot", "sot"],
    "fouls": ["fouls", "fouls_committed"],
    "corners": ["corners", "corner_kicks"],
}


def _normalize_key(value: str) -> str:
    normalized = value.strip().lower()
    normalized = normalized.replace("%", "pct")
    normalized = re.sub(r"[\s\-\/]+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    return normalized


def _safe_int(value: str) -> int | None:
    try:
        return int(str(value).strip())
    except Exception:
        return None


def _safe_float(value: str) -> float | None:
    normalized = str(value).replace("%", "").strip()
    try:
        return float(normalized)
    except Exception:
        return None


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
            value = "".join(self._current_text).strip()
            if value:
                self._current_headers.append(_normalize_key(value))
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


class _ScriptJsonParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._script_type: str | None = None
        self._script_data: list[str] = []
        self.json_blocks: list[str] = []
        self.script_blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "script":
            return
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        self._script_type = attrs_dict.get("type", "").lower()
        self._script_data = []

    def handle_endtag(self, tag: str) -> None:
        if tag != "script":
            return
        payload = "".join(self._script_data).strip()
        if not payload:
            return
        self.script_blocks.append(payload)
        if "json" in (self._script_type or ""):
            self.json_blocks.append(payload)
        self._script_type = None
        self._script_data = []

    def handle_data(self, data: str) -> None:
        if self._script_type is not None:
            self._script_data.append(data)


class PremierLeagueDataSource(DataSource):
    def __init__(self, config: SourceConfig) -> None:
        self.config = config

    def load_teams(self) -> list[TeamPayload]:
        html = self._fetch_with_retry(self.config.teams_url, "pl.fetch.teams")
        records = self._extract_records(
            dataset="teams",
            html=html,
            aliases=TEAM_ALIASES,
            required=["name", "short_name", "stadium", "manager"],
        )
        payload: list[TeamPayload] = []
        for row in records:
            payload.append(
                {
                    "name": row["name"],
                    "short_name": row["short_name"],
                    "logo_url": row.get("logo_url", ""),
                    "stadium": row["stadium"],
                    "manager": row["manager"],
                }
            )
        log_event("INFO", "pl.parse.teams", rows=len(payload))
        return payload

    def load_players(self) -> list[PlayerPayload]:
        html = self._fetch_with_retry(self.config.players_url, "pl.fetch.players")
        records = self._extract_records(
            dataset="players",
            html=html,
            aliases=PLAYER_ALIASES,
            required=["player_id", "team_short_name", "name", "position", "jersey_num", "nationality"],
        )
        payload: list[PlayerPayload] = []
        for row in records:
            payload.append(
                {
                    "player_id": _safe_int(row["player_id"]) or 0,
                    "team_short_name": row["team_short_name"],
                    "name": row["name"],
                    "position": row["position"],
                    "jersey_num": _safe_int(row["jersey_num"]) or 0,
                    "nationality": row["nationality"],
                    "photo_url": row.get("photo_url", ""),
                }
            )
        log_event("INFO", "pl.parse.players", rows=len(payload))
        return payload

    def load_matches(self) -> list[MatchPayload]:
        html = self._fetch_with_retry(self.config.matches_url, "pl.fetch.matches")
        records = self._extract_records(
            dataset="matches",
            html=html,
            aliases=MATCH_ALIASES,
            required=["round", "match_date", "home_team_short_name", "away_team_short_name", "status"],
        )
        payload: list[MatchPayload] = []
        for row in records:
            payload.append(
                {
                    "round": _safe_int(row["round"]) or 0,
                    "match_date": row["match_date"],
                    "home_team_short_name": row["home_team_short_name"],
                    "away_team_short_name": row["away_team_short_name"],
                    "home_score": _safe_int(row.get("home_score", "")),
                    "away_score": _safe_int(row.get("away_score", "")),
                    "status": row["status"],
                }
            )
        log_event("INFO", "pl.parse.matches", rows=len(payload))
        return payload

    def load_match_stats(self) -> list[MatchStatPayload]:
        html = self._fetch_with_retry(self.config.match_stats_url, "pl.fetch.match_stats")
        records = self._extract_records(
            dataset="match_stats",
            html=html,
            aliases=MATCH_STATS_ALIASES,
            required=[
                "round",
                "home_team_short_name",
                "away_team_short_name",
                "team_short_name",
                "possession",
                "shots",
                "shots_on_target",
                "fouls",
                "corners",
            ],
        )
        payload: list[MatchStatPayload] = []
        for row in records:
            payload.append(
                {
                    "round": _safe_int(row["round"]) or 0,
                    "home_team_short_name": row["home_team_short_name"],
                    "away_team_short_name": row["away_team_short_name"],
                    "team_short_name": row["team_short_name"],
                    "possession": _safe_float(row["possession"]) or 0.0,
                    "shots": _safe_int(row["shots"]) or 0,
                    "shots_on_target": _safe_int(row["shots_on_target"]) or 0,
                    "fouls": _safe_int(row["fouls"]) or 0,
                    "corners": _safe_int(row["corners"]) or 0,
                }
            )
        log_event("INFO", "pl.parse.match_stats", rows=len(payload))
        return payload

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

    def _extract_records(
        self,
        *,
        dataset: Dataset,
        html: str,
        aliases: dict[str, list[str]],
        required: list[str],
    ) -> list[dict[str, str]]:
        from_table = self._extract_from_table(html=html, aliases=aliases, required=required)
        if from_table:
            log_event("INFO", "pl.parse.strategy", dataset=dataset, strategy="table", rows=len(from_table))
            return from_table

        from_json = self._extract_from_json(html=html, aliases=aliases, required=required)
        if from_json:
            log_event("INFO", "pl.parse.strategy", dataset=dataset, strategy="json", rows=len(from_json))
            return from_json

        return self._handle_dataset_issue(dataset, reason="no_records_after_all_strategies")

    def _extract_from_table(
        self,
        *,
        html: str,
        aliases: dict[str, list[str]],
        required: list[str],
    ) -> list[dict[str, str]]:
        parser = _SimpleTableParser()
        parser.feed(html)
        for table in parser.tables:
            if not table.headers or not table.rows:
                continue
            mapped = self._map_table_rows(table.headers, table.rows, aliases, required)
            if mapped:
                return mapped
        return []

    def _map_table_rows(
        self,
        headers: list[str],
        rows: list[list[str]],
        aliases: dict[str, list[str]],
        required: list[str],
    ) -> list[dict[str, str]]:
        index = self._build_alias_index(headers, aliases)
        missing = [key for key in required if key not in index]
        if missing:
            if self.config.parse_strict:
                raise ValueError(f"missing required headers: {missing}")
            return []

        mapped: list[dict[str, str]] = []
        for row in rows:
            item: dict[str, str] = {}
            for canonical, col in index.items():
                if col < len(row):
                    item[canonical] = row[col]
            if all(item.get(key, "").strip() for key in required):
                mapped.append(item)
        return mapped

    def _extract_from_json(
        self,
        *,
        html: str,
        aliases: dict[str, list[str]],
        required: list[str],
    ) -> list[dict[str, str]]:
        candidates = self._extract_json_candidates(html)
        mapped: list[dict[str, str]] = []
        for candidate in candidates:
            mapped.extend(self._map_json_candidate(candidate, aliases, required))
            if mapped:
                return mapped
        return []

    def _extract_json_candidates(self, html: str) -> list[object]:
        parser = _ScriptJsonParser()
        parser.feed(html)
        values: list[object] = []

        for block in parser.json_blocks:
            obj = self._json_load(block)
            if obj is not None:
                values.append(obj)

        for block in parser.script_blocks:
            for pattern in (
                r"__NEXT_DATA__\s*=\s*(\{.*?\})\s*;",
                r"__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;",
            ):
                match = re.search(pattern, block, re.DOTALL)
                if not match:
                    continue
                obj = self._json_load(match.group(1))
                if obj is not None:
                    values.append(obj)
        return values

    def _json_load(self, raw: str) -> object | None:
        try:
            return json.loads(raw)
        except Exception:
            return None

    def _map_json_candidate(
        self,
        candidate: object,
        aliases: dict[str, list[str]],
        required: list[str],
    ) -> list[dict[str, str]]:
        records = self._flatten_dict_records(candidate)
        mapped: list[dict[str, str]] = []
        for record in records:
            normalized = {_normalize_key(str(k)): str(v) for k, v in record.items() if v is not None}
            item: dict[str, str] = {}
            for canonical, candidates in aliases.items():
                for alias in candidates:
                    key = _normalize_key(alias)
                    if key in normalized:
                        item[canonical] = normalized[key]
                        break
            if all(item.get(key, "").strip() for key in required):
                mapped.append(item)
        return mapped

    def _flatten_dict_records(self, obj: object) -> list[dict[str, object]]:
        queue = [obj]
        records: list[dict[str, object]] = []
        while queue:
            current = queue.pop(0)
            if isinstance(current, dict):
                records.append(current)
                for value in current.values():
                    if isinstance(value, (dict, list)):
                        queue.append(value)
            elif isinstance(current, list):
                for value in current:
                    if isinstance(value, (dict, list)):
                        queue.append(value)
        return records

    def _build_alias_index(self, headers: list[str], aliases: dict[str, list[str]]) -> dict[str, int]:
        index: dict[str, int] = {}
        header_index = {h: idx for idx, h in enumerate(headers)}
        for canonical, candidates in aliases.items():
            for alias in candidates:
                key = _normalize_key(alias)
                if key in header_index:
                    index[canonical] = header_index[key]
                    break
        return index

    def _handle_dataset_issue(self, dataset: Dataset, *, reason: str) -> list[dict[str, str]]:
        policy = self._policy_for(dataset)
        log_event("WARNING", "pl.parse.dataset_issue", dataset=dataset, policy=policy, reason=reason)
        if policy == "abort":
            raise ValueError(f"{dataset} parse failed: {reason}")
        return []

    def _policy_for(self, dataset: Dataset) -> str:
        if dataset == "teams":
            return self.config.dataset_policy_teams
        if dataset == "players":
            return self.config.dataset_policy_players
        if dataset == "matches":
            return self.config.dataset_policy_matches
        if dataset == "match_stats":
            return self.config.dataset_policy_match_stats
        return "abort"
