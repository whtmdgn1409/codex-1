from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Match, Player, Team
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.team import SquadPlayerItem, TeamDetailResponse, TeamItem, TeamListResponse

router = APIRouter(prefix="/teams", tags=["teams"])


def _match_result_for_team(match: Match, team_id: int) -> str:
    if match.home_score is None or match.away_score is None:
        return "D"

    if match.home_team_id == team_id:
        if match.home_score > match.away_score:
            return "W"
        if match.home_score < match.away_score:
            return "L"
        return "D"

    if match.away_team_id == team_id:
        if match.away_score > match.home_score:
            return "W"
        if match.away_score < match.home_score:
            return "L"
        return "D"

    return "D"


@router.get("", response_model=TeamListResponse)
def list_teams(db: Session = Depends(get_db)) -> TeamListResponse:
    rows = db.execute(select(Team).order_by(Team.name.asc())).scalars().all()
    items = [
        TeamItem(
            team_id=row.team_id,
            name=row.name,
            short_name=row.short_name,
            logo_url=row.logo_url,
            stadium=row.stadium,
            manager=row.manager,
        )
        for row in rows
    ]
    return TeamListResponse(total=len(items), items=items)


@router.get(
    "/{team_id}",
    response_model=TeamDetailResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Team not found",
        }
    },
)
def get_team_detail(team_id: int, db: Session = Depends(get_db)) -> TeamDetailResponse:
    team = db.execute(select(Team).where(Team.team_id == team_id)).scalar_one_or_none()
    if team is None:
        raise HTTPException(status_code=404, detail="team not found")

    recent_matches = db.execute(
        select(Match)
        .where(
            Match.status == "FINISHED",
            or_(Match.home_team_id == team_id, Match.away_team_id == team_id),
        )
        .order_by(Match.match_date.desc(), Match.match_id.desc())
        .limit(5)
    ).scalars().all()

    recent_form = [_match_result_for_team(match, team_id) for match in recent_matches]

    squad_rows = db.execute(
        select(Player)
        .where(Player.team_id == team_id)
        .order_by(Player.position.asc(), func.coalesce(Player.jersey_num, 999).asc(), Player.name.asc())
    ).scalars().all()

    squad = [
        SquadPlayerItem(
            player_id=player.player_id,
            name=player.name,
            position=player.position,
            jersey_num=player.jersey_num,
            nationality=player.nationality,
            photo_url=player.photo_url,
        )
        for player in squad_rows
    ]

    return TeamDetailResponse(
        team=TeamItem(
            team_id=team.team_id,
            name=team.name,
            short_name=team.short_name,
            logo_url=team.logo_url,
            stadium=team.stadium,
            manager=team.manager,
        ),
        recent_form=recent_form,
        squad=squad,
    )
