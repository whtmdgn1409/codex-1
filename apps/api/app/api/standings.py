from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Standing
from app.db.session import get_db
from app.schemas.standing import StandingItem, StandingsResponse

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("", response_model=StandingsResponse)
def list_standings(db: Session = Depends(get_db)) -> StandingsResponse:
    rows = db.execute(select(Standing).order_by(Standing.rank.asc(), Standing.team_id.asc())).scalars().all()

    items = [
        StandingItem(
            team_id=row.team_id,
            rank=row.rank,
            played=row.played,
            won=row.won,
            drawn=row.drawn,
            lost=row.lost,
            goals_for=row.goals_for,
            goals_against=row.goals_against,
            goal_diff=row.goal_diff,
            points=row.points,
        )
        for row in rows
    ]

    return StandingsResponse(total=len(items), items=items)
