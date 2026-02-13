from datetime import datetime

from app.db.models import Match, MatchEvent, MatchStat, Standing, Team


def seed_data(session_factory) -> None:
    db = session_factory()
    db.query(MatchEvent).delete()
    db.query(MatchStat).delete()
    db.query(Standing).delete()
    db.query(Match).delete()
    db.query(Team).delete()

    teams = [
        Team(team_id=1, name="Arsenal FC", short_name="ARS"),
        Team(team_id=2, name="Chelsea FC", short_name="CHE"),
        Team(team_id=3, name="Liverpool FC", short_name="LIV"),
    ]
    db.add_all(teams)

    matches = [
        Match(
            match_id=1,
            round=1,
            match_date=datetime(2025, 8, 10, 20, 0, 0),
            home_team_id=1,
            away_team_id=2,
            home_score=2,
            away_score=1,
            status="FINISHED",
        ),
        Match(
            match_id=2,
            round=2,
            match_date=datetime(2025, 9, 1, 20, 0, 0),
            home_team_id=2,
            away_team_id=3,
            home_score=None,
            away_score=None,
            status="SCHEDULED",
        ),
        Match(
            match_id=3,
            round=2,
            match_date=datetime(2025, 9, 15, 20, 0, 0),
            home_team_id=1,
            away_team_id=3,
            home_score=0,
            away_score=0,
            status="FINISHED",
        ),
    ]
    db.add_all(matches)

    events = [
        MatchEvent(
            event_id=11,
            match_id=1,
            minute=24,
            event_type="GOAL",
            team_id=1,
            player_name="Saka",
            detail="Right-footed finish",
        ),
        MatchEvent(
            event_id=12,
            match_id=1,
            minute=67,
            event_type="GOAL",
            team_id=2,
            player_name="Jackson",
            detail="Header",
        ),
    ]
    db.add_all(events)

    stats = [
        MatchStat(
            stat_id=21,
            match_id=1,
            team_id=1,
            possession=56.4,
            shots=14,
            shots_on_target=6,
            fouls=10,
            corners=7,
        ),
        MatchStat(
            stat_id=22,
            match_id=1,
            team_id=2,
            possession=43.6,
            shots=9,
            shots_on_target=4,
            fouls=12,
            corners=3,
        ),
    ]
    db.add_all(stats)

    standings = [
        Standing(
            team_id=1,
            rank=1,
            played=20,
            won=14,
            drawn=4,
            lost=2,
            goals_for=42,
            goals_against=18,
            goal_diff=24,
            points=46,
        ),
        Standing(
            team_id=3,
            rank=2,
            played=20,
            won=13,
            drawn=5,
            lost=2,
            goals_for=40,
            goals_against=20,
            goal_diff=20,
            points=44,
        ),
    ]
    db.add_all(standings)

    db.commit()
    db.close()


def test_list_matches_without_filters(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/matches")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_matches_by_round(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/matches", params={"round": 2})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert all(item["round"] == 2 for item in data["items"])


def test_list_matches_by_month_and_team(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/matches", params={"month": 9, "team_id": 1})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["match_id"] == 3


def test_get_match_detail(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/matches/1")

    assert response.status_code == 200
    data = response.json()
    assert data["match"]["match_id"] == 1
    assert len(data["events"]) == 2
    assert data["events"][0]["minute"] == 24
    assert len(data["stats"]) == 2


def test_get_match_detail_not_found(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/matches/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "match not found"


def test_list_standings(client, session_factory) -> None:
    seed_data(session_factory)
    response = client.get("/standings")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert data["items"][0]["rank"] == 1
    assert data["items"][1]["rank"] == 2
