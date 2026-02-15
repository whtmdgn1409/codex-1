from __future__ import annotations

from crawler.db import Database
from crawler.logging_utils import log_event
from crawler.sources import get_data_source
from crawler.sources.types import MatchPayload, MatchStatPayload, PlayerPayload, StandingPayload, TeamPayload


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
        team_id = team_map.get(player["team_short_name"])
        if team_id is None:
            log_event("WARNING", "ingest.players.skip_unknown_team", team_short_name=player["team_short_name"], player_id=player["player_id"])
            continue

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
            db.execute(
                """
                INSERT INTO player_season_stats(player_id, goals, assists, attack_points, clean_sheets)
                VALUES(?, 0, 0, 0, 0)
                ON CONFLICT(player_id) DO NOTHING
                """,
                (player["player_id"],),
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
            db.execute(
                """
                INSERT IGNORE INTO player_season_stats(player_id, goals, assists, attack_points, clean_sheets)
                VALUES(%s, 0, 0, 0, 0)
                """,
                (player["player_id"],),
            )


def upsert_matches(db: Database, matches: list[MatchPayload] | None = None) -> None:
    if matches is None:
        matches = get_data_source().load_matches()
    team_map = _team_id_map(db)

    for match in matches:
        home_team_id = team_map.get(match["home_team_short_name"])
        away_team_id = team_map.get(match["away_team_short_name"])
        if home_team_id is None or away_team_id is None:
            log_event(
                "WARNING",
                "ingest.matches.skip_unknown_team",
                home_team_short_name=match["home_team_short_name"],
                away_team_short_name=match["away_team_short_name"],
            )
            continue

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
        home_team_id = team_map.get(stat["home_team_short_name"])
        away_team_id = team_map.get(stat["away_team_short_name"])
        if home_team_id is None or away_team_id is None:
            log_event(
                "WARNING",
                "ingest.match_stats.skip_unknown_match_team",
                home_team_short_name=stat["home_team_short_name"],
                away_team_short_name=stat["away_team_short_name"],
            )
            continue
        key = (int(stat["round"]), home_team_id, away_team_id)
        match_id = match_map.get(key)
        if match_id is None:
            log_event(
                "WARNING",
                "ingest.match_stats.skip_missing_match",
                round=stat["round"],
                home_team_short_name=stat["home_team_short_name"],
                away_team_short_name=stat["away_team_short_name"],
            )
            continue
        team_id = team_map.get(stat["team_short_name"])
        if team_id is None:
            log_event("WARNING", "ingest.match_stats.skip_unknown_team", team_short_name=stat["team_short_name"])
            continue

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


def upsert_standings(db: Database, standings: list[StandingPayload] | None = None) -> None:
    if standings is None:
        standings = get_data_source().load_standings()
    team_map = _team_id_map(db)

    for item in standings:
        team_id = team_map.get(item["team_short_name"])
        if team_id is None:
            continue

        if db.config.engine == "sqlite":
            db.execute(
                """
                INSERT INTO standings(team_id, rank, played, won, drawn, lost, goals_for, goals_against, goal_diff, points)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(team_id) DO UPDATE SET
                  rank=excluded.rank,
                  played=excluded.played,
                  won=excluded.won,
                  drawn=excluded.drawn,
                  lost=excluded.lost,
                  goals_for=excluded.goals_for,
                  goals_against=excluded.goals_against,
                  goal_diff=excluded.goal_diff,
                  points=excluded.points
                """,
                (
                    team_id,
                    item["rank"],
                    item["played"],
                    item["won"],
                    item["drawn"],
                    item["lost"],
                    item["goals_for"],
                    item["goals_against"],
                    item["goal_diff"],
                    item["points"],
                ),
            )
        else:
            db.execute(
                """
                INSERT INTO standings(team_id, rank, played, won, drawn, lost, goals_for, goals_against, goal_diff, points)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  rank=VALUES(rank),
                  played=VALUES(played),
                  won=VALUES(won),
                  drawn=VALUES(drawn),
                  lost=VALUES(lost),
                  goals_for=VALUES(goals_for),
                  goals_against=VALUES(goals_against),
                  goal_diff=VALUES(goal_diff),
                  points=VALUES(points)
                """,
                (
                    team_id,
                    item["rank"],
                    item["played"],
                    item["won"],
                    item["drawn"],
                    item["lost"],
                    item["goals_for"],
                    item["goals_against"],
                    item["goal_diff"],
                    item["points"],
                ),
            )


def ingest_all(db: Database) -> None:
    source = get_data_source()
    upsert_teams(db, source.load_teams())
    upsert_players(db, source.load_players())
    upsert_matches(db, source.load_matches())
    upsert_match_stats(db, source.load_match_stats())
    upsert_standings(db, source.load_standings())


def summary(db: Database) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in ("teams", "players", "matches", "match_stats", "standings"):
        row = db.fetchone(f"SELECT COUNT(*) AS cnt FROM {table}")
        counts[table] = int(row["cnt"]) if row else 0
    return counts
