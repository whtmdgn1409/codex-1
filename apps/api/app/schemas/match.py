from datetime import datetime

from pydantic import BaseModel


class MatchListItem(BaseModel):
    match_id: int
    round: int
    match_date: datetime
    home_team_id: int
    away_team_id: int
    home_score: int | None
    away_score: int | None
    status: str


class MatchListResponse(BaseModel):
    total: int
    items: list[MatchListItem]


class MatchEventItem(BaseModel):
    event_id: int
    minute: int
    event_type: str
    team_id: int | None
    player_name: str | None
    detail: str | None


class MatchStatItem(BaseModel):
    team_id: int
    possession: float | None
    shots: int | None
    shots_on_target: int | None
    fouls: int | None
    corners: int | None


class MatchDetailResponse(BaseModel):
    match: MatchListItem
    events: list[MatchEventItem]
    stats: list[MatchStatItem]
