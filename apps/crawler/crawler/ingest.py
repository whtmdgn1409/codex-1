from __future__ import annotations

from crawler.db import Database
from crawler.sources import get_data_source
from crawler.sources.types import MatchPayload, MatchStatPayload, PlayerPayload, TeamPayload


def upsert_teams(db: Database, teams: list[TeamPayload] | None = None) -> None:
    if teams is None:
        teams = get_data_source().load_teams()
    for team in teams:
        if db.config.engine == "sqlite":
            db.execute(
                """
                INSERT INTO teams(name, short_name, logo_url, stadium, manager)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(short_name) DO UPDATE SET
                  name=excluded.name,
                  logo_url=excluded.logo_url,
                  stadium=excluded.stadium,
                  manager=excluded.manager
                """,
                (
                    team["name"],
                    team["short_name"],
                    team["logo_url"],
                    team["stadium"],
                    team["manager"],
                ),
            )
        else:
            db.execute(
                """
                INSERT INTO teams(name, short_name, logo_url, stadium, manager)
                VALUES(%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  name=VALUES(name),
                  logo_url=VALUES(logo_url),
                  stadium=VALUES(stadium),
                  manager=VALUES(manager)
                """,
                (
                    team["name"],
                    team["short_name"],
                    team["logo_url"],
                    team["stadium"],
                    team["manager"],
                ),
            )


def _team_id_map(db: Database) -> dict[str, int]:
    rows = db.fetchall("SELECT team_id, short_name FROM teams")
    return {str(row["short_name"]): int(row["team_id"]) for row in rows}


def upsert_players(db: Database, players: list[PlayerPayload] | None = None) -> None:
    if players is None:
        players = get_data_source().load_players()
    team_map = _team_id_map(db)

    for player in players:
        team_id = team_map[player["team_short_name"]]

        if db.config.engine == "sqlite":
            db.execute(
                """
                INSERT INTO players(player_id, team_id, name, position, jersey_num, nationality, photo_url)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_id) DO UPDATE SET
                  team_id=excluded.team_id,
                  name=excluded.name,
                  position=excluded.position,
                  jersey_num=excluded.jersey_num,
                  nationality=excluded.nationality,
                  photo_url=excluded.photo_url
                """,
                (
                    player["player_id"],
                    team_id,
                    player["name"],
                    player["position"],
                    player["jersey_num"],
                    player["nationality"],
                    player["photo_url"],
                ),
            )
        else:
            db.execute(
                """
                INSERT INTO players(player_id, team_id, name, position, jersey_num, nationality, photo_url)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  team_id=VALUES(team_id),
                  name=VALUES(name),
                  position=VALUES(position),
                  jersey_num=VALUES(jersey_num),
                  nationality=VALUES(nationality),
                  photo_url=VALUES(photo_url)
                """,
                (
                    player["player_id"],
                    team_id,
                    player["name"],
                    player["position"],
                    player["jersey_num"],
                    player["nationality"],
                    player["photo_url"],
                ),
            )


def upsert_matches(db: Database, matches: list[MatchPayload] | None = None) -> None:
    if matches is None:
        matches = get_data_source().load_matches()
    team_map = _team_id_map(db)

    for match in matches:
        home_team_id = team_map[match["home_team_short_name"]]
        away_team_id = team_map[match["away_team_short_name"]]

        if db.config.engine == "sqlite":
            db.execute(
                """
                INSERT INTO matches(round, match_date, home_team_id, away_team_id, home_score, away_score, status)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(round, home_team_id, away_team_id) DO UPDATE SET
                  match_date=excluded.match_date,
                  home_score=excluded.home_score,
                  away_score=excluded.away_score,
                  status=excluded.status
                """,
                (
                    match["round"],
                    match["match_date"],
                    home_team_id,
                    away_team_id,
                    match["home_score"],
                    match["away_score"],
                    match["status"],
                ),
            )
        else:
            db.execute(
                """
                INSERT INTO matches(round, match_date, home_team_id, away_team_id, home_score, away_score, status)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  match_date=VALUES(match_date),
                  home_score=VALUES(home_score),
                  away_score=VALUES(away_score),
                  status=VALUES(status)
                """,
                (
                    match["round"],
                    match["match_date"],
                    home_team_id,
                    away_team_id,
                    match["home_score"],
                    match["away_score"],
                    match["status"],
                ),
            )


def _match_id_map(db: Database) -> dict[tuple[int, int, int], int]:
    rows = db.fetchall("SELECT match_id, round, home_team_id, away_team_id FROM matches")
    return {(int(r["round"]), int(r["home_team_id"]), int(r["away_team_id"])): int(r["match_id"]) for r in rows}


def upsert_match_stats(db: Database, match_stats: list[MatchStatPayload] | None = None) -> None:
    if match_stats is None:
        match_stats = get_data_source().load_match_stats()
    team_map = _team_id_map(db)
    match_map = _match_id_map(db)

    for stat in match_stats:
        home_team_id = team_map[stat["home_team_short_name"]]
        away_team_id = team_map[stat["away_team_short_name"]]
        key = (int(stat["round"]), home_team_id, away_team_id)
        match_id = match_map[key]
        team_id = team_map[stat["team_short_name"]]

        if db.config.engine == "sqlite":
            db.execute(
                """
                INSERT INTO match_stats(match_id, team_id, possession, shots, shots_on_target, fouls, corners)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_id, team_id) DO UPDATE SET
                  possession=excluded.possession,
                  shots=excluded.shots,
                  shots_on_target=excluded.shots_on_target,
                  fouls=excluded.fouls,
                  corners=excluded.corners
                """,
                (
                    match_id,
                    team_id,
                    stat["possession"],
                    stat["shots"],
                    stat["shots_on_target"],
                    stat["fouls"],
                    stat["corners"],
                ),
            )
        else:
            db.execute(
                """
                INSERT INTO match_stats(match_id, team_id, possession, shots, shots_on_target, fouls, corners)
                VALUES(%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  possession=VALUES(possession),
                  shots=VALUES(shots),
                  shots_on_target=VALUES(shots_on_target),
                  fouls=VALUES(fouls),
                  corners=VALUES(corners)
                """,
                (
                    match_id,
                    team_id,
                    stat["possession"],
                    stat["shots"],
                    stat["shots_on_target"],
                    stat["fouls"],
                    stat["corners"],
                ),
            )


def ingest_all(db: Database) -> None:
    source = get_data_source()
    upsert_teams(db, source.load_teams())
    upsert_players(db, source.load_players())
    upsert_matches(db, source.load_matches())
    upsert_match_stats(db, source.load_match_stats())


def summary(db: Database) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in ("teams", "players", "matches", "match_stats"):
        row = db.fetchone(f"SELECT COUNT(*) AS cnt FROM {table}")
        counts[table] = int(row["cnt"]) if row else 0
    return counts
