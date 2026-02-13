import {
  MatchDetailResponse,
  MatchListResponse,
  StandingsResponse,
  StatsCategory,
  TeamDetailResponse,
  TeamListResponse,
  TopStatsResponse
} from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

class ApiClientError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

function withQuery(path: string, params: Record<string, string | number | undefined>): string {
  const qs = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      qs.set(key, String(value));
    }
  });

  const q = qs.toString();
  return q ? `${path}?${q}` : path;
}

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  const text = await response.text();
  let data: unknown = {};

  if (text) {
    try {
      data = JSON.parse(text) as unknown;
    } catch {
      data = {};
    }
  }

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? String((data as { detail?: unknown }).detail ?? "request failed")
        : "request failed";

    throw new ApiClientError(detail, response.status);
  }

  return data as T;
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

export async function listMatches(params: {
  round?: number;
  month?: number;
  team_id?: number;
  limit?: number;
  offset?: number;
}): Promise<MatchListResponse> {
  return fetchJson<MatchListResponse>(
    withQuery("/matches", {
      round: params.round,
      month: params.month,
      team_id: params.team_id,
      limit: params.limit,
      offset: params.offset
    })
  );
}

export async function getMatch(matchId: number): Promise<MatchDetailResponse> {
  return fetchJson<MatchDetailResponse>(`/matches/${matchId}`);
}

export async function listStandings(): Promise<StandingsResponse> {
  return fetchJson<StandingsResponse>("/standings");
}

export async function topStats(category: StatsCategory, limit = 10): Promise<TopStatsResponse> {
  return fetchJson<TopStatsResponse>(withQuery("/stats/top", { category, limit }));
}

export async function listTeams(): Promise<TeamListResponse> {
  return fetchJson<TeamListResponse>("/teams");
}

export async function getTeam(teamId: number): Promise<TeamDetailResponse> {
  return fetchJson<TeamDetailResponse>(`/teams/${teamId}`);
}

export { ApiClientError };
