CREATE TABLE IF NOT EXISTS player_season_stats (
    player_id INT PRIMARY KEY,
    goals INT NOT NULL DEFAULT 0,
    assists INT NOT NULL DEFAULT 0,
    attack_points INT NOT NULL DEFAULT 0,
    clean_sheets INT NOT NULL DEFAULT 0,
    CONSTRAINT fk_player_season_stats_player FOREIGN KEY (player_id) REFERENCES players(player_id),
    INDEX idx_player_stats_goals (goals),
    INDEX idx_player_stats_assists (assists),
    INDEX idx_player_stats_attack_points (attack_points),
    INDEX idx_player_stats_clean_sheets (clean_sheets)
);
