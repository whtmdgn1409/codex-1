from fastapi import APIRouter

from app.api.matches import router as matches_router
from app.api.standings import router as standings_router
from app.api.stats import router as stats_router
from app.api.teams import router as teams_router

api_router = APIRouter()
api_router.include_router(matches_router)
api_router.include_router(standings_router)
api_router.include_router(stats_router)
api_router.include_router(teams_router)
