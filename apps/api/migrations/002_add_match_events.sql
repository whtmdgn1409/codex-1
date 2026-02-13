CREATE TABLE IF NOT EXISTS match_events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT NOT NULL,
    minute INT NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    team_id INT NULL,
    player_name VARCHAR(50) NULL,
    detail VARCHAR(255) NULL,
    CONSTRAINT fk_match_events_match FOREIGN KEY (match_id) REFERENCES matches(match_id),
    CONSTRAINT fk_match_events_team FOREIGN KEY (team_id) REFERENCES teams(team_id),
    INDEX idx_match_events_match_id (match_id),
    INDEX idx_match_events_minute (minute)
);
