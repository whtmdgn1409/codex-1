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


TEAMS: list[TeamPayload] = [
    {
        "name": "Arsenal FC",
        "short_name": "ARS",
        "logo_url": "https://example.com/logos/ars.png",
        "stadium": "Emirates Stadium",
        "manager": "Mikel Arteta",
    },
    {
        "name": "Liverpool FC",
        "short_name": "LIV",
        "logo_url": "https://example.com/logos/liv.png",
        "stadium": "Anfield",
        "manager": "Arne Slot",
    },
    {
        "name": "Chelsea FC",
        "short_name": "CHE",
        "logo_url": "https://example.com/logos/che.png",
        "stadium": "Stamford Bridge",
        "manager": "Enzo Maresca",
    },
]

PLAYERS: list[PlayerPayload] = [
    {
        "player_id": 101,
        "team_short_name": "ARS",
        "name": "Bukayo Saka",
        "position": "FW",
        "jersey_num": 7,
        "nationality": "England",
        "photo_url": "https://example.com/players/saka.png",
    },
    {
        "player_id": 102,
        "team_short_name": "ARS",
        "name": "Declan Rice",
        "position": "MF",
        "jersey_num": 41,
        "nationality": "England",
        "photo_url": "https://example.com/players/rice.png",
    },
    {
        "player_id": 201,
        "team_short_name": "LIV",
        "name": "Mohamed Salah",
        "position": "FW",
        "jersey_num": 11,
        "nationality": "Egypt",
        "photo_url": "https://example.com/players/salah.png",
    },
]

MATCHES: list[MatchPayload] = [
    {
        "round": 1,
        "match_date": "2025-08-10 20:00:00",
        "home_team_short_name": "ARS",
        "away_team_short_name": "CHE",
        "home_score": 2,
        "away_score": 1,
        "status": "FINISHED",
    },
    {
        "round": 1,
        "match_date": "2025-08-11 20:00:00",
        "home_team_short_name": "LIV",
        "away_team_short_name": "ARS",
        "home_score": None,
        "away_score": None,
        "status": "SCHEDULED",
    },
]

MATCH_STATS: list[MatchStatPayload] = [
    {
        "round": 1,
        "home_team_short_name": "ARS",
        "away_team_short_name": "CHE",
        "team_short_name": "ARS",
        "possession": 56.4,
        "shots": 14,
        "shots_on_target": 6,
        "fouls": 10,
        "corners": 7,
    },
    {
        "round": 1,
        "home_team_short_name": "ARS",
        "away_team_short_name": "CHE",
        "team_short_name": "CHE",
        "possession": 43.6,
        "shots": 9,
        "shots_on_target": 4,
        "fouls": 12,
        "corners": 3,
    },
]
