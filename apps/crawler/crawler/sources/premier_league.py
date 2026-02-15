from __future__ import annotations

import json
import re
import ssl
import time
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from crawler.config import SourceConfig
from crawler.logging_utils import log_event
from crawler.sources.base import DataSource
from crawler.sources.matches_seed import load_seed_matches
from crawler.sources.teams_seed import load_seed_teams
from crawler.sources.types import MatchPayload, MatchStatPayload, PlayerPayload, TeamPayload

Dataset = str

TEAM_ALIASES: dict[str, list[str]] = {
    "team_id": ["team_id", "id"],
    "name": ["name", "club", "team", "team_name", "club_name"],
    "short_name": ["short_name", "abbr", "short", "code", "team_short_name", "abbreviation", "shortname"],
    "logo_url": ["logo_url", "logo", "crest", "image_url", "crest_url", "badge", "badge_url"],
    "stadium": ["stadium", "venue", "ground", "stadium_name", "home_stadium"],
    "manager": ["manager", "coach", "head_coach", "headcoach"],
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
    "round": ["round", "matchweek", "match_week", "week", "gw", "event"],
    "match_date": ["match_date", "date", "kickoff", "kickoff_time", "kickoff_date", "kickoff_datetime", "kickoff_utc", "kickoff_label"],
    "home_team_id": ["home_team_id", "team_h", "home_id"],
    "away_team_id": ["away_team_id", "team_a", "away_id"],
    "home_team_short_name": [
        "home_team_short_name",
        "home_team_shortname",
        "home_team_short",
        "home_team",
        "home_team_code",
        "home",
    ],
    "away_team_short_name": [
        "away_team_short_name",
        "away_team_shortname",
        "away_team_short",
        "away_team",
        "away_team_code",
        "away",
    ],
    "home_score": ["home_score", "home_goals", "score_home", "team_h_score"],
    "away_score": ["away_score", "away_goals", "score_away", "team_a_score"],
    "status": ["status", "match_status", "result_status", "state", "finished"],
}

MATCH_STATS_ALIASES: dict[str, list[str]] = {
    "round": ["round", "matchweek", "match_week", "week", "gw"],
    "home_team_short_name": ["home_team_short_name", "home_team_shortname", "home_team", "home_team_code", "home"],
    "away_team_short_name": ["away_team_short_name", "away_team_shortname", "away_team", "away_team_code", "away"],
    "team_short_name": ["team_short_name", "team_shortname", "team_code", "team", "club"],
    "possession": ["possession", "possession_pct", "possession_percent", "possession_percentage"],
    "shots": ["shots", "total_shots"],
    "shots_on_target": ["shots_on_target", "shots_ot", "sot", "on_target"],
    "fouls": ["fouls", "fouls_committed"],
    "corners": ["corners", "corner_kicks", "corners_won"],
}

def _normalize_key(value: str) -> str:
    normalized = value.strip()
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", normalized)
    normalized = normalized.lower()
    normalized = normalized.replace("%", "pct")
    normalized = re.sub(r"[\s\-\/]+", "_", normalized)
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    return normalized


def _build_seed_short_name_map() -> dict[str, str]:
    seed_map: dict[str, str] = {}
    for team in load_seed_teams():
        raw_name = str(team.get("name", "")).strip()
        short_name = str(team.get("short_name", "")).strip()
        if not raw_name or not short_name:
            continue
        seed_map[_normalize_key(raw_name)] = short_name
        fc_trimmed = re.sub(r"\bfc\b", "", raw_name, flags=re.IGNORECASE).strip()
        if fc_trimmed:
            seed_map[_normalize_key(fc_trimmed)] = short_name
    return seed_map


_SEED_SHORT_NAME_MAP = _build_seed_short_name_map()


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


def _derive_short_name(team_name: str) -> str:
    normalized_name = _normalize_key(team_name)
    if normalized_name in _SEED_SHORT_NAME_MAP:
        return _SEED_SHORT_NAME_MAP[normalized_name]

    no_fc = re.sub(r"\bfc\b", "", team_name, flags=re.IGNORECASE).strip()
    normalized_no_fc = _normalize_key(no_fc)
    if normalized_no_fc in _SEED_SHORT_NAME_MAP:
        return _SEED_SHORT_NAME_MAP[normalized_no_fc]

    cleaned = re.sub(r"[^A-Za-z0-9\s]", " ", team_name).strip()
    if not cleaned:
        return "UNK"
    parts = [part for part in cleaned.split() if part]
    if len(parts) >= 2:
        initials = "".join(part[0] for part in parts[:3]).upper()
        if len(initials) >= 2:
            return initials[:3]
    compact = "".join(parts)
    return compact[:3].upper() if compact else "UNK"


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


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_anchor = False
        self._current_href = ""
        self._current_text: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        self._current_href = attrs_dict.get("href", "")
        self._current_text = []
        self._in_anchor = True

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or not self._in_anchor:
            return
        text = " ".join("".join(self._current_text).split()).strip()
        self.links.append((self._current_href, text))
        self._in_anchor = False
        self._current_href = ""
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._in_anchor:
            self._current_text.append(data)


class PremierLeagueDataSource(DataSource):
    def __init__(self, config: SourceConfig) -> None:
        self.config = config
        self._team_id_to_short: dict[int, str] = {}

    def load_teams(self) -> list[TeamPayload]:
        html = self._fetch_html_for_dataset("teams", self.config.teams_url, "pl.fetch.teams")
        if html is None:
            if self.config.teams_seed_fallback:
                seed_payload = load_seed_teams()
                log_event("WARNING", "pl.parse.teams_seed_fallback", rows=len(seed_payload))
                return seed_payload
            return []
        records = self._extract_from_table(html=html, aliases=TEAM_ALIASES, required=["name"])
        if records:
            log_event("INFO", "pl.parse.strategy", dataset="teams", strategy="table", rows=len(records))
        if not records:
            records = self._extract_from_json(html=html, aliases=TEAM_ALIASES, required=["name"])
            if records:
                log_event("INFO", "pl.parse.strategy", dataset="teams", strategy="json", rows=len(records))
        if not records:
            records = self._extract_teams_from_links(html)
            if records:
                log_event("INFO", "pl.parse.strategy", dataset="teams", strategy="links", rows=len(records))
        if not records:
            if self.config.teams_seed_fallback:
                seed_payload = load_seed_teams()
                log_event("WARNING", "pl.parse.teams_seed_fallback", rows=len(seed_payload))
                return seed_payload
            records = self._handle_dataset_issue("teams", reason="no_records_after_all_strategies")

        payload: list[TeamPayload] = []
        for row in records:
            name = row["name"].strip()
            short_name = row.get("short_name", "").strip() or _derive_short_name(name)
            team_id = _safe_int(row.get("team_id", ""))
            if team_id is not None and team_id > 0:
                self._team_id_to_short[team_id] = short_name
            payload.append(
                {
                    "name": name,
                    "short_name": short_name,
                    "logo_url": row.get("logo_url", ""),
                    "stadium": row.get("stadium", ""),
                    "manager": row.get("manager", ""),
                }
            )
        log_event("INFO", "pl.parse.teams", rows=len(payload))
        return payload

    def _extract_teams_from_links(self, html: str) -> list[dict[str, str]]:
        parser = _AnchorParser()
        parser.feed(html)
        items: list[dict[str, str]] = []
        seen_names: set[str] = set()

        for href, text in parser.links:
            href_lower = href.lower()
            if "/clubs/" not in href_lower:
                continue

            team_name = text.strip()
            if not team_name or team_name.lower() in {"clubs", "all clubs", "club"}:
                team_name = self._name_from_club_href(href)
            if not team_name:
                continue

            normalized_name = " ".join(team_name.split()).strip()
            if not normalized_name:
                continue
            key = normalized_name.lower()
            if key in seen_names:
                continue
            seen_names.add(key)

            items.append(
                {
                    "name": normalized_name,
                    "short_name": _derive_short_name(normalized_name),
                    "logo_url": "",
                    "stadium": "",
                    "manager": "",
                }
            )
        return items

    def _name_from_club_href(self, href: str) -> str:
        patterns = [
            r"/clubs/\d+/([^/?#]+)/",
            r"/clubs/\d+/([^/?#]+)$",
            r"/clubs/([^/?#]+)/",
            r"/clubs/([^/?#]+)$",
        ]
        for pattern in patterns:
            matched = re.search(pattern, href, flags=re.IGNORECASE)
            if not matched:
                continue
            slug = matched.group(1).strip("-_ ")
            if not slug:
                continue
            words = [segment for segment in re.split(r"[-_]+", slug) if segment]
            if not words:
                continue
            return " ".join(word.capitalize() for word in words)
        return ""

    def load_players(self) -> list[PlayerPayload]:
        html = self._fetch_html_for_dataset("players", self.config.players_url, "pl.fetch.players")
        if html is None:
            return []
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
        try:
            html = self._fetch_with_retry(self.config.matches_url, "pl.fetch.matches")
        except Exception as exc:
            if self.config.matches_seed_fallback:
                seed_payload = load_seed_matches()
                log_event("WARNING", "pl.parse.matches_seed_fallback", rows=len(seed_payload), reason=type(exc).__name__)
                return seed_payload
            self._handle_dataset_issue("matches", reason=f"fetch_failed:{type(exc).__name__}")
            return []

        records = self._extract_from_table(
            html=html,
            aliases=MATCH_ALIASES,
            required=["round", "match_date"],
        )
        if records:
            log_event("INFO", "pl.parse.strategy", dataset="matches", strategy="table", rows=len(records))
        if not records:
            records = self._extract_from_json(
                html=html,
                aliases=MATCH_ALIASES,
                required=["round", "match_date"],
            )
            if records:
                log_event("INFO", "pl.parse.strategy", dataset="matches", strategy="json", rows=len(records))
        if not records and self.config.matches_seed_fallback:
            seed_payload = load_seed_matches()
            log_event("WARNING", "pl.parse.matches_seed_fallback", rows=len(seed_payload), reason="no_records_after_all_strategies")
            return seed_payload
        if not records:
            records = self._handle_dataset_issue("matches", reason="no_records_after_all_strategies")

        payload: list[MatchPayload] = []
        for row in records:
            home_short = row.get("home_team_short_name", "").strip()
            away_short = row.get("away_team_short_name", "").strip()
            if not home_short:
                home_team_id = _safe_int(row.get("home_team_id", ""))
                if home_team_id is not None:
                    home_short = self._team_id_to_short.get(home_team_id, "")
            if not away_short:
                away_team_id = _safe_int(row.get("away_team_id", ""))
                if away_team_id is not None:
                    away_short = self._team_id_to_short.get(away_team_id, "")
            if not home_short or not away_short:
                continue

            status_raw = row.get("status", "").strip().upper()
            if status_raw in {"TRUE", "1", "YES"}:
                status = "FINISHED"
            elif status_raw in {"FALSE", "0", "NO", ""}:
                status = "SCHEDULED"
            elif "FIN" in status_raw:
                status = "FINISHED"
            else:
                status = "SCHEDULED"

            payload.append(
                {
                    "round": _safe_int(row["round"]) or 0,
                    "match_date": row["match_date"],
                    "home_team_short_name": home_short,
                    "away_team_short_name": away_short,
                    "home_score": _safe_int(row.get("home_score", "")),
                    "away_score": _safe_int(row.get("away_score", "")),
                    "status": status,
                }
            )
        log_event("INFO", "pl.parse.matches", rows=len(payload))
        return payload

    def load_match_stats(self) -> list[MatchStatPayload]:
        html = self._fetch_html_for_dataset("match_stats", self.config.match_stats_url, "pl.fetch.match_stats")
        if html is None:
            return []
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

    def _fetch_html_for_dataset(self, dataset: Dataset, url: str, event_name: str) -> str | None:
        try:
            return self._fetch_with_retry(url, event_name)
        except Exception as exc:
            reason = f"fetch_failed:{type(exc).__name__}"
            self._handle_dataset_issue(dataset, reason=reason)
            return None

    def _http_get(self, url: str) -> str:
        request = Request(url, headers={"User-Agent": "EPL-Information-Hub-Crawler/1.0"})
        if self.config.verify_ssl:
            context = ssl.create_default_context(cafile=self.config.ca_file)
        else:
            context = ssl._create_unverified_context()
            log_event("WARNING", "pl.http.ssl_verify_disabled", url=url)

        with urlopen(request, timeout=self.config.timeout_seconds, context=context) as response:
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
        stripped = html.strip()
        values: list[object] = []
        if stripped.startswith("{") or stripped.startswith("["):
            direct = self._json_load(stripped)
            if direct is not None:
                values.append(direct)

        parser = _ScriptJsonParser()
        parser.feed(html)

        for block in parser.json_blocks:
            obj = self._json_load(block)
            if obj is not None:
                values.append(obj)

        for block in parser.script_blocks:
            for variable in (
                "__NEXT_DATA__",
                "__PRELOADED_STATE__",
                "__INITIAL_STATE__",
                "window.__NEXT_DATA__",
                "window.PULSE.envPaths",
                "PULSE.envPaths",
                "window.PULSE.app",
                "PULSE.app",
            ):
                raw = self._extract_assigned_json(block, variable)
                if raw is None:
                    continue
                obj = self._json_load(raw)
                if obj is not None:
                    values.append(obj)
            values.extend(self._extract_inline_json_objects(block))
        return values

    def _extract_assigned_json(self, script_block: str, variable: str) -> str | None:
        marker_index = script_block.find(variable)
        if marker_index < 0:
            return None
        eq_index = script_block.find("=", marker_index)
        if eq_index < 0:
            return None
        start = eq_index + 1
        while start < len(script_block) and script_block[start].isspace():
            start += 1
        if start >= len(script_block) or script_block[start] not in "{[":
            return None
        return self._extract_balanced(script_block, start)

    def _extract_inline_json_objects(self, script_block: str) -> list[object]:
        values: list[object] = []
        for opening in ("{", "["):
            start = 0
            while start < len(script_block):
                idx = script_block.find(opening, start)
                if idx < 0:
                    break
                raw = self._extract_balanced(script_block, idx)
                if raw is None:
                    start = idx + 1
                    continue
                parsed = self._json_load(raw)
                if parsed is not None:
                    values.append(parsed)
                start = idx + 1
        return values

    def _extract_balanced(self, text: str, start: int) -> str | None:
        opening = text[start]
        closing = "}" if opening == "{" else "]"
        stack = [closing]

        in_string = False
        escaped = False
        for idx in range(start + 1, len(text)):
            char = text[idx]
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == "{":
                stack.append("}")
                continue
            if char == "[":
                stack.append("]")
                continue
            if char == stack[-1]:
                stack.pop()
                if not stack:
                    return text[start : idx + 1]
        return None

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
            normalized = self._flatten_record_values(record)
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

    def _flatten_record_values(self, record: dict[str, object]) -> dict[str, str]:
        values: dict[str, str] = {}

        def _set_value(path: str, value: object) -> None:
            text = str(value).strip()
            if not text:
                return
            segments = [segment for segment in path.split("_") if segment]
            if path not in values:
                values[path] = text
            if len(segments) >= 2:
                tail_two = "_".join(segments[-2:])
                if tail_two and tail_two not in values:
                    values[tail_two] = text
            tail_one = segments[-1] if segments else ""
            if tail_one and tail_one not in values:
                values[tail_one] = text

        queue: list[tuple[str, object]] = [("", record)]
        while queue:
            prefix, current = queue.pop(0)
            if isinstance(current, dict):
                for raw_key, raw_value in current.items():
                    if raw_value is None:
                        continue
                    key = _normalize_key(str(raw_key))
                    if not key:
                        continue
                    next_prefix = f"{prefix}_{key}" if prefix else key
                    queue.append((next_prefix, raw_value))
                continue
            if isinstance(current, list):
                for item in current:
                    if isinstance(item, (dict, list)):
                        queue.append((prefix, item))
                    elif prefix:
                        _set_value(prefix, item)
                continue
            if prefix:
                _set_value(prefix, current)
        return values

    def _flatten_dict_records(self, obj: object) -> list[dict[str, object]]:
        queue = [obj]
        records: list[dict[str, object]] = []
        while queue:
            current = queue.pop(0)
            if isinstance(current, dict):
                has_scalar_value = any(
                    value is not None and not isinstance(value, (dict, list)) for value in current.values()
                )
                if has_scalar_value:
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
