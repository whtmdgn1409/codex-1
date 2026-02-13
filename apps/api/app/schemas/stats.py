from pydantic import BaseModel


class TopStatItem(BaseModel):
    player_id: int
    player_name: str
    team_id: int
    team_name: str
    team_short_name: str
    value: int
    goals: int
    assists: int
    attack_points: int
    clean_sheets: int


class TopStatsResponse(BaseModel):
    category: str
    total: int
    items: list[TopStatItem]
