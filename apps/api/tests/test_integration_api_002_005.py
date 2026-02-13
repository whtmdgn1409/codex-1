from datetime import datetime

from app.db.models import (
    Match,
    MatchEvent,
    MatchStat,
    Player,
    PlayerSeasonStat,
    Standing,
    Team,
)


def seed_data(session_factory) -> None:
    db = session_factory()
    db.query(MatchEvent).delete()
    db.query(MatchStat).delete()
    db.query(PlayerSeasonStat).delete()
    db.query(Standing).delete()
    db.query(Player).delete()
    db.query(Match).delete()
    db.query(Team).delete()

    teams = [
        Team(team_id=1, name="Arsenal FC", short_name="ARS", manager="Mikel Arteta"),
        Team(team_id=2, name="Liverpool FC", short_name="LIV", manager="Arne Slot"),
        Team(team_id=3, name="Chelsea FC", short_name="CHE", manager="Enzo Maresca"),
    ]
    db.add_all(teams)

    players = [
        Player(player_id=10, team_id=1, name="Bukayo Saka", position="FW", jersey_num=7),
        Player(player_id=11, team_id=1, name="Declan Rice", position="MF", jersey_num=41),
        Player(player_id=20, team_id=2, name="Mohamed Salah", position="FW", jersey_num=11),
        Player(player_id=30, team_id=3, name="Cole Palmer", position="MF", jersey_num=20),
    ]
    db.add_all(players)

    player_stats = [
        PlayerSeasonStat(player_id=10, goals=12, assists=9, attack_points=21, clean_sheets=4),
        PlayerSeasonStat(player_id=11, goals=4, assists=6, attack_points=10, clean_sheets=8),
        PlayerSeasonStat(player_id=20, goals=15, assists=7, attack_points=22, clean_sheets=3),
        PlayerSeasonStat(player_id=30, goals=10, assists=8, attack_points=18, clean_sheets=2),
    ]
    db.add_all(player_stats)

    matches = [
        Match(
            match_id=100,
            round=10,
            match_date=datetime(2025, 10, 1, 20, 0, 0),
            home_team_id=1,
            away_team_id=2,
            home_score=2,
            away_score=1,
            status="FINISHED",
        ),
        Match(
            match_id=101,
            round=11,
            match_date=datetime(2025, 10, 8, 20, 0, 0),
            home_team_id=2,
            away_team_id=1,
            home_score=1,
            away_score=1,
            status="FINISHED",
        ),
        Match(
            match_id=102,
            round=12,
            match_date=datetime(2025, 10, 15, 20, 0, 0),
            home_team_id=3,
            away_team_id=1,
            home_score=0,
            away_score=2,
            status="FINISHED",
        ),
    ]
    db.add_all(matches)

    events = [
        MatchEvent(
            event_id=900,
            match_id=100,
            minute=12,
            event_type="GOAL",
            team_id=1,
            player_name="Bukayo Saka",
            detail="Open play",
        ),
        MatchEvent(
            event_id=901,
            match_id=100,
            minute=83,
            event_type="GOAL",
            team_id=2,
            player_name="Mohamed Salah",
            detail="Penalty",
        ),
    ]
    db.add_all(events)

    match_stats = [
        MatchStat(
            stat_id=700,
            match_id=100,
            team_id=1,
            possession=53.5,
            shots=13,
            shots_on_target=6,
            fouls=11,
            corners=5,
        ),
        MatchStat(
            stat_id=701,
            match_id=100,
            team_id=2,
            possession=46.5,
            shots=10,
            shots_on_target=4,
            fouls=9,
            corners=4,
        ),
    ]
    db.add_all(match_stats)

    standings = [
        Standing(team_id=1, rank=1, played=12, won=9, drawn=2, lost=1, goals_for=28, goals_against=10, goal_diff=18, points=29),
        Standing(team_id=2, rank=2, played=12, won=8, drawn=2, lost=2, goals_for=24, goals_against=11, goal_diff=13, points=26),
        Standing(team_id=3, rank=3, played=12, won=7, drawn=1, lost=4, goals_for=20, goals_against=14, goal_diff=6, points=22),
    ]
    db.add_all(standings)

    db.commit()
    db.close()


def test_integration_api_002_to_005_core_flow(client, session_factory) -> None:
    seed_data(session_factory)

    match_response = client.get("/matches/100")
    assert match_response.status_code == 200
    match_data = match_response.json()
    assert match_data["match"]["match_id"] == 100
    assert len(match_data["events"]) == 2
    assert {item["team_id"] for item in match_data["stats"]} == {1, 2}

    standings_response = client.get("/standings")
    assert standings_response.status_code == 200
    standings_data = standings_response.json()
    assert standings_data["total"] == 3
    assert standings_data["items"][0]["team_id"] == 1

    stats_response = client.get("/stats/top", params={"category": "goals", "limit": 2})
    assert stats_response.status_code == 200
    stats_data = stats_response.json()
    assert stats_data["items"][0]["player_name"] == "Mohamed Salah"
    assert stats_data["items"][0]["value"] == 15

    teams_response = client.get("/teams")
    assert teams_response.status_code == 200
    teams_data = teams_response.json()
    assert teams_data["total"] == 3
    team_ids = {item["team_id"] for item in teams_data["items"]}
    assert 1 in team_ids

    team_detail_response = client.get("/teams/1")
    assert team_detail_response.status_code == 200
    team_detail = team_detail_response.json()
    assert team_detail["team"]["name"] == "Arsenal FC"
    assert team_detail["recent_form"] == ["W", "D", "W"]
    assert len(team_detail["squad"]) == 2


def test_integration_api_002_to_005_not_found_cases(client, session_factory) -> None:
    seed_data(session_factory)

    missing_match = client.get("/matches/9999")
    assert missing_match.status_code == 404
    assert missing_match.json()["detail"] == "match not found"

    missing_team = client.get("/teams/9999")
    assert missing_team.status_code == 404
    assert missing_team.json()["detail"] == "team not found"
