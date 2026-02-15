from __future__ import annotations

from crawler.sources.types import TeamPayload

# Fallback dataset used when the official clubs page cannot be parsed reliably.
# Keep short_name aligned with match/standing payload conventions.
SEED_TEAMS: list[TeamPayload] = [
    {"name": "Arsenal FC", "short_name": "ARS", "logo_url": "", "stadium": "Emirates Stadium", "manager": ""},
    {"name": "Aston Villa", "short_name": "AVL", "logo_url": "", "stadium": "Villa Park", "manager": ""},
    {"name": "Bournemouth", "short_name": "BOU", "logo_url": "", "stadium": "Vitality Stadium", "manager": ""},
    {"name": "Brentford", "short_name": "BRE", "logo_url": "", "stadium": "Gtech Community Stadium", "manager": ""},
    {"name": "Brighton & Hove Albion", "short_name": "BHA", "logo_url": "", "stadium": "Amex Stadium", "manager": ""},
    {"name": "Burnley", "short_name": "BUR", "logo_url": "", "stadium": "Turf Moor", "manager": ""},
    {"name": "Chelsea FC", "short_name": "CHE", "logo_url": "", "stadium": "Stamford Bridge", "manager": ""},
    {"name": "Crystal Palace", "short_name": "CRY", "logo_url": "", "stadium": "Selhurst Park", "manager": ""},
    {"name": "Everton", "short_name": "EVE", "logo_url": "", "stadium": "Goodison Park", "manager": ""},
    {"name": "Fulham", "short_name": "FUL", "logo_url": "", "stadium": "Craven Cottage", "manager": ""},
    {"name": "Leeds United", "short_name": "LEE", "logo_url": "", "stadium": "Elland Road", "manager": ""},
    {"name": "Liverpool FC", "short_name": "LIV", "logo_url": "", "stadium": "Anfield", "manager": ""},
    {"name": "Manchester City", "short_name": "MCI", "logo_url": "", "stadium": "Etihad Stadium", "manager": ""},
    {"name": "Manchester United", "short_name": "MUN", "logo_url": "", "stadium": "Old Trafford", "manager": ""},
    {"name": "Newcastle United", "short_name": "NEW", "logo_url": "", "stadium": "St James' Park", "manager": ""},
    {"name": "Nottingham Forest", "short_name": "NFO", "logo_url": "", "stadium": "City Ground", "manager": ""},
    {"name": "Sunderland", "short_name": "SUN", "logo_url": "", "stadium": "Stadium of Light", "manager": ""},
    {"name": "Tottenham Hotspur", "short_name": "TOT", "logo_url": "", "stadium": "Tottenham Hotspur Stadium", "manager": ""},
    {"name": "West Ham United", "short_name": "WHU", "logo_url": "", "stadium": "London Stadium", "manager": ""},
    {"name": "Wolverhampton Wanderers", "short_name": "WOL", "logo_url": "", "stadium": "Molineux Stadium", "manager": ""},
]


def load_seed_teams() -> list[TeamPayload]:
    return list(SEED_TEAMS)
