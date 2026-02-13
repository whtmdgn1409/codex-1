from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db.models import Player, PlayerSeasonStat, Team
from app.db.session import get_db
from app.schemas.stats import TopStatItem, TopStatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/top", response_model=TopStatsResponse)
def top_stats(
    category: Literal["goals", "assists", "attack_points", "clean_sheets"] = Query(default="goals"),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> TopStatsResponse:
    metric = getattr(PlayerSeasonStat, category)

    rows = db.execute(
        select(PlayerSeasonStat, Player, Team)
        .join(Player, Player.player_id == PlayerSeasonStat.player_id)
        .join(Team, Team.team_id == Player.team_id)
        .order_by(desc(metric), Player.player_id.asc())
        .limit(limit)
    ).all()

    items = [
        TopStatItem(
            player_id=player.player_id,
            player_name=player.name,
            team_id=team.team_id,
            team_name=team.name,
            team_short_name=team.short_name,
            value=getattr(stat, category),
            goals=stat.goals,
            assists=stat.assists,
            attack_points=stat.attack_points,
            clean_sheets=stat.clean_sheets,
        )
        for stat, player, team in rows
    ]

    return TopStatsResponse(category=category, total=len(items), items=items)
