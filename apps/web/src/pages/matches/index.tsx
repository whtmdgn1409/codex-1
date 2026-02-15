import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { listMatches, listTeams } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/format";
import { MatchListItem, TeamItem } from "@/lib/types";

type MatchFilter = {
  round?: number;
  month?: number;
  team_id?: number;
};

const FILTER_DEBOUNCE_MS = 300;
const INITIAL_VISIBLE_MATCHES = 20;
const LOAD_MORE_STEP = 20;

export default function MatchesPage() {
  const [teams, setTeams] = useState<TeamItem[]>([]);
  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [visibleCount, setVisibleCount] = useState(INITIAL_VISIBLE_MATCHES);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [roundInput, setRoundInput] = useState("");
  const [monthInput, setMonthInput] = useState("");
  const [teamInput, setTeamInput] = useState("");
  const [debouncedFilter, setDebouncedFilter] = useState<MatchFilter>({});

  const parsedFilter = useMemo<MatchFilter>(
    () => ({
      round: roundInput ? Number(roundInput) : undefined,
      month: monthInput ? Number(monthInput) : undefined,
      team_id: teamInput ? Number(teamInput) : undefined
    }),
    [roundInput, monthInput, teamInput]
  );

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedFilter(parsedFilter);
    }, FILTER_DEBOUNCE_MS);
    return () => window.clearTimeout(timer);
  }, [parsedFilter]);

  useEffect(() => {
    let active = true;

    async function loadTeams(): Promise<void> {
      try {
        const teamsRes = await listTeams();
        if (active) {
          setTeams(teamsRes.items);
        }
      } catch {
        if (active) {
          setTeams([]);
        }
      }
    }

    void loadTeams();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    let active = true;

    async function loadMatches(): Promise<void> {
      setLoading(true);
      setError(null);
      try {
        const data = await listMatches({
          ...debouncedFilter,
          limit: 100,
          offset: 0
        });
        if (active) {
          setMatches(data.items);
          setVisibleCount(INITIAL_VISIBLE_MATCHES);
        }
      } catch (err) {
        if (active) {
          const message = err instanceof Error ? err.message : "경기 목록을 불러오지 못했습니다.";
          setError(message);
          setMatches([]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadMatches();

    return () => {
      active = false;
    };
  }, [debouncedFilter]);

  const teamMap = useMemo(() => new Map(teams.map((team) => [team.team_id, team])), [teams]);
  const visibleMatches = useMemo(() => matches.slice(0, visibleCount), [matches, visibleCount]);

  const groupedByDate = useMemo(() => {
    const groups: Record<string, MatchListItem[]> = {};

    visibleMatches.forEach((match) => {
      const key = formatDate(match.match_date);
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(match);
    });

    return Object.entries(groups);
  }, [visibleMatches]);

  return (
    <div className="stack">
      <h1 className="section-title">일정 / 결과</h1>

      <div className="card filters">
        <select className="select" value={roundInput} onChange={(e) => setRoundInput(e.target.value)}>
          <option value="">라운드 전체</option>
          {Array.from({ length: 38 }, (_, i) => i + 1).map((round) => (
            <option key={round} value={round}>
              {round}R
            </option>
          ))}
        </select>

        <select className="select" value={monthInput} onChange={(e) => setMonthInput(e.target.value)}>
          <option value="">월 전체</option>
          {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
            <option key={month} value={month}>
              {month}월
            </option>
          ))}
        </select>

        <select className="select" value={teamInput} onChange={(e) => setTeamInput(e.target.value)}>
          <option value="">팀 전체</option>
          {teams.map((team) => (
            <option key={team.team_id} value={team.team_id}>
              {team.name}
            </option>
          ))}
        </select>
      </div>

      {loading && <div className="loading">경기 일정 로딩 중...</div>}
      {error && <div className="error">경기 일정 조회 실패: {error}</div>}

      {!loading && !error && groupedByDate.length === 0 && (
        <div className="empty">조건에 맞는 경기가 없습니다.</div>
      )}

      {!loading &&
        !error &&
        groupedByDate.map(([date, items]) => (
          <section key={date} className="card stack">
            <h2 className="card-title">{date}</h2>
            {items.map((match) => {
              const homeTeam = teamMap.get(match.home_team_id);
              const awayTeam = teamMap.get(match.away_team_id);
              const isFinished = match.status === "FINISHED";

              return (
                <div key={match.match_id} className="row">
                  <div className="stack">
                    <div>
                      {formatDateTime(match.match_date)}
                      <span className={`pill ${isFinished ? "pill--ok" : "pill--warn"}`} style={{ marginLeft: 8 }}>
                        {match.status}
                      </span>
                    </div>
                    <strong>
                      {homeTeam?.short_name ?? `#${match.home_team_id}`} ({match.home_score ?? "-"}) vs ({match.away_score ?? "-"}) {" "}
                      {awayTeam?.short_name ?? `#${match.away_team_id}`}
                    </strong>
                  </div>
                  {isFinished ? (
                    <Link className="button-link" href={`/matches/${match.match_id}`}>
                      매치 리포트
                    </Link>
                  ) : (
                    <span className="muted">경기 전</span>
                  )}
                </div>
              );
            })}
          </section>
        ))}

      {!loading && !error && matches.length > visibleMatches.length && (
        <div className="row">
          <span className="muted">
            {visibleMatches.length} / {matches.length} 경기 표시
          </span>
          <button
            className="button-link"
            type="button"
            onClick={() => setVisibleCount((prev) => prev + LOAD_MORE_STEP)}
          >
            더 보기
          </button>
        </div>
      )}
    </div>
  );
}
