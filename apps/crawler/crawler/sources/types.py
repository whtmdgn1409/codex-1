from __future__ import annotations

from typing import TypedDict


class TeamPayload(TypedDict):
    name: str
    short_name: str
    logo_url: str
    stadium: str
    manager: str


class PlayerPayload(TypedDict):
    player_id: int
    team_short_name: str
    name: str
    position: str
    jersey_num: int
    nationality: str
    photo_url: str


class MatchPayload(TypedDict):
    round: int
    match_date: str
    home_team_short_name: str
    away_team_short_name: str
    home_score: int | None
    away_score: int | None
    status: str


class MatchStatPayload(TypedDict):
    round: int
    home_team_short_name: str
    away_team_short_name: str
    team_short_name: str
    possession: float
    shots: int
    shots_on_target: int
    fouls: int
    corners: int
