from pydantic import BaseModel


class TeamItem(BaseModel):
    team_id: int
    name: str
    short_name: str
    logo_url: str | None
    stadium: str | None
    manager: str | None


class TeamListResponse(BaseModel):
    total: int
    items: list[TeamItem]


class SquadPlayerItem(BaseModel):
    player_id: int
    name: str
    position: str
    jersey_num: int | None
    nationality: str | None
    photo_url: str | None


class TeamDetailResponse(BaseModel):
    team: TeamItem
    recent_form: list[str]
    squad: list[SquadPlayerItem]
