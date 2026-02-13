CREATE TABLE IF NOT EXISTS teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    short_name VARCHAR(10) NOT NULL UNIQUE,
    logo_url VARCHAR(255),
    stadium VARCHAR(100),
    manager VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    team_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    position VARCHAR(10) NOT NULL,
    jersey_num INT,
    nationality VARCHAR(50),
    photo_url VARCHAR(255),
    CONSTRAINT fk_players_team FOREIGN KEY (team_id) REFERENCES teams(team_id),
    INDEX idx_players_team_id (team_id),
    UNIQUE KEY uq_players_team_jersey (team_id, jersey_num)
);

CREATE TABLE IF NOT EXISTS matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    round INT NOT NULL,
    match_date DATETIME NOT NULL,
    home_team_id INT NOT NULL,
    away_team_id INT NOT NULL,
    home_score INT NULL,
    away_score INT NULL,
    status VARCHAR(20) NOT NULL,
    CONSTRAINT fk_matches_home_team FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    CONSTRAINT fk_matches_away_team FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    INDEX idx_matches_round (round),
    INDEX idx_matches_date (match_date),
    INDEX idx_matches_home_team (home_team_id),
    INDEX idx_matches_away_team (away_team_id),
    UNIQUE KEY uq_matches_fixture (round, home_team_id, away_team_id)
);

CREATE TABLE IF NOT EXISTS match_stats (
    stat_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    team_id INT NOT NULL,
    possession DECIMAL(5,2),
    shots INT,
    shots_on_target INT,
    fouls INT,
    corners INT,
    CONSTRAINT fk_match_stats_match FOREIGN KEY (match_id) REFERENCES matches(match_id),
    CONSTRAINT fk_match_stats_team FOREIGN KEY (team_id) REFERENCES teams(team_id),
    INDEX idx_match_stats_match_id (match_id),
    UNIQUE KEY uq_match_stats_match_team (match_id, team_id)
);

CREATE TABLE IF NOT EXISTS standings (
    team_id INT PRIMARY KEY,
    rank INT NOT NULL,
    played INT NOT NULL,
    won INT NOT NULL,
    drawn INT NOT NULL,
    lost INT NOT NULL,
    goals_for INT NOT NULL,
    goals_against INT NOT NULL,
    goal_diff INT NOT NULL,
    points INT NOT NULL,
    CONSTRAINT fk_standings_team FOREIGN KEY (team_id) REFERENCES teams(team_id),
    INDEX idx_standings_rank (rank),
    INDEX idx_standings_points (points)
);
