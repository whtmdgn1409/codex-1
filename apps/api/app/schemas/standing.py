from pydantic import BaseModel


class StandingItem(BaseModel):
    team_id: int
    rank: int
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_diff: int
    points: int


class StandingsResponse(BaseModel):
    total: int
    items: list[StandingItem]
