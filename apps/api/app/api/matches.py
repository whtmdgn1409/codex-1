from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import extract, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Match, MatchEvent, MatchStat
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.match import (
    MatchDetailResponse,
    MatchEventItem,
    MatchListItem,
    MatchListResponse,
    MatchStatItem,
)

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchListResponse)
def list_matches(
    round: int | None = Query(default=None, ge=1, le=38),
    month: int | None = Query(default=None, ge=1, le=12),
    team_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> MatchListResponse:
    filters = []

    if round is not None:
        filters.append(Match.round == round)

    if month is not None:
        filters.append(extract("month", Match.match_date) == month)

    if team_id is not None:
        filters.append(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))

    count_query = select(func.count(Match.match_id))
    list_query = select(Match).order_by(Match.match_date.desc(), Match.match_id.desc()).limit(limit).offset(offset)

    if filters:
        count_query = count_query.where(*filters)
        list_query = list_query.where(*filters)

    total = db.execute(count_query).scalar_one()
    rows = db.execute(list_query).scalars().all()

    items = [
        MatchListItem(
            match_id=row.match_id,
            round=row.round,
            match_date=row.match_date,
            home_team_id=row.home_team_id,
            away_team_id=row.away_team_id,
            home_score=row.home_score,
            away_score=row.away_score,
            status=row.status,
        )
        for row in rows
    ]

    return MatchListResponse(total=total, items=items)


@router.get(
    "/{match_id}",
    response_model=MatchDetailResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Match not found",
        }
    },
)
def get_match_detail(match_id: int, db: Session = Depends(get_db)) -> MatchDetailResponse:
    row = db.execute(select(Match).where(Match.match_id == match_id)).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="match not found")

    events = db.execute(
        select(MatchEvent)
        .where(MatchEvent.match_id == match_id)
        .order_by(MatchEvent.minute.asc(), MatchEvent.event_id.asc())
    ).scalars().all()

    stats = db.execute(
        select(MatchStat).where(MatchStat.match_id == match_id).order_by(MatchStat.team_id.asc())
    ).scalars().all()

    event_items = [
        MatchEventItem(
            event_id=event.event_id,
            minute=event.minute,
            event_type=event.event_type,
            team_id=event.team_id,
            player_name=event.player_name,
            detail=event.detail,
        )
        for event in events
    ]

    stat_items = [
        MatchStatItem(
            team_id=stat.team_id,
            possession=float(stat.possession) if stat.possession is not None else None,
            shots=stat.shots,
            shots_on_target=stat.shots_on_target,
            fouls=stat.fouls,
            corners=stat.corners,
        )
        for stat in stats
    ]

    return MatchDetailResponse(
        match=MatchListItem(
            match_id=row.match_id,
            round=row.round,
            match_date=row.match_date,
            home_team_id=row.home_team_id,
            away_team_id=row.away_team_id,
            home_score=row.home_score,
            away_score=row.away_score,
            status=row.status,
        ),
        events=event_items,
        stats=stat_items,
    )
