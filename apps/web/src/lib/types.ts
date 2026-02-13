export interface MatchListItem {
  match_id: number;
  round: number;
  match_date: string;
  home_team_id: number;
  away_team_id: number;
  home_score: number | null;
  away_score: number | null;
  status: string;
}

export interface MatchListResponse {
  total: number;
  items: MatchListItem[];
}

export interface MatchEventItem {
  event_id: number;
  minute: number;
  event_type: string;
  team_id: number | null;
  player_name: string | null;
  detail: string | null;
}

export interface MatchStatItem {
  team_id: number;
  possession: number | null;
  shots: number | null;
  shots_on_target: number | null;
  fouls: number | null;
  corners: number | null;
}

export interface MatchDetailResponse {
  match: MatchListItem;
  events: MatchEventItem[];
  stats: MatchStatItem[];
}

export interface StandingItem {
  team_id: number;
  rank: number;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_diff: number;
  points: number;
}

export interface StandingsResponse {
  total: number;
  items: StandingItem[];
}

export type StatsCategory = "goals" | "assists" | "attack_points" | "clean_sheets";

export interface TopStatItem {
  player_id: number;
  player_name: string;
  team_id: number;
  team_name: string;
  team_short_name: string;
  value: number;
  goals: number;
  assists: number;
  attack_points: number;
  clean_sheets: number;
}

export interface TopStatsResponse {
  category: StatsCategory;
  total: number;
  items: TopStatItem[];
}

export interface TeamItem {
  team_id: number;
  name: string;
  short_name: string;
  logo_url: string | null;
  stadium: string | null;
  manager: string | null;
}

export interface TeamListResponse {
  total: number;
  items: TeamItem[];
}

export interface SquadPlayerItem {
  player_id: number;
  name: string;
  position: string;
  jersey_num: number | null;
  nationality: string | null;
  photo_url: string | null;
}

export interface TeamDetailResponse {
  team: TeamItem;
  recent_form: Array<"W" | "D" | "L">;
  squad: SquadPlayerItem[];
}

export interface ApiErrorResponse {
  detail: string;
}
