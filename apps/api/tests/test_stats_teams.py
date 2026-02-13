from datetime import datetime

from app.db.models import Match, Player, PlayerSeasonStat, Team


def seed_data(session_factory) -> None:
    db = session_factory()
    db.query(PlayerSeasonStat).delete()
    db.query(Player).delete()
    db.query(Match).delete()
    db.query(Team).delete()

    teams = [
        Team(team_id=1, name="Arsenal FC", short_name="ARS", manager="Mikel Arteta"),
        Team(team_id=2, name="Liverpool FC", short_name="LIV", manager="Arne Slot"),
    ]
    db.add_all(teams)

    players = [
        Player(player_id=10, team_id=1, name="Bukayo Saka", position="FW", jersey_num=7, nationality="England"),
        Player(player_id=11, team_id=1, name="Declan Rice", position="MF", jersey_num=41, nationality="England"),
        Player(player_id=20, team_id=2, name="Mohamed Salah", position="FW", jersey_num=11, nationality="Egypt"),
    ]
    db.add_all(players)

    player_stats = [
        PlayerSeasonStat(player_id=10, goals=12, assists=9, attack_points=21, clean_sheets=4),
        PlayerSeasonStat(player_id=11, goals=4, assists=6, attack_points=10, clean_sheets=8),
        PlayerSeasonStat(player_id=20, goals=15, assists=7, attack_points=22, clean_sheets=3),
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
            home_team_id=1,
            away_team_id=2,
            home_score=0,
            away_score=2,
            status="FINISHED",
        ),
    ]
    db.add_all(matches)

    db.commit()
    db.close()


def test_top_stats_goals(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/stats/top", params={"category": "goals", "limit": 2})

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "goals"
    assert data["total"] == 2
    assert data["items"][0]["player_name"] == "Mohamed Salah"
    assert data["items"][0]["value"] == 15


def test_top_stats_attack_points(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/stats/top", params={"category": "attack_points", "limit": 3})

    assert response.status_code == 200
    data = response.json()
    assert data["items"][0]["value"] == 22
    assert data["items"][1]["value"] == 21


def test_list_teams(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/teams")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["items"][0]["name"] == "Arsenal FC"


def test_team_detail(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/teams/1")

    assert response.status_code == 200
    data = response.json()
    assert data["team"]["short_name"] == "ARS"
    assert data["recent_form"] == ["L", "D", "W"]
    assert len(data["squad"]) == 2


def test_team_detail_not_found(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/teams/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "team not found"
