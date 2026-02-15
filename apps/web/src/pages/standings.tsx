import { useEffect, useMemo, useState } from "react";

import { listStandings, listTeams } from "@/lib/api";
import { StandingItem, TeamItem } from "@/lib/types";

export default function StandingsPage() {
  const [items, setItems] = useState<StandingItem[]>([]);
  const [teams, setTeams] = useState<TeamItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load(): Promise<void> {
      setLoading(true);
      setError(null);

      try {
        const [standingsRes, teamsRes] = await Promise.all([listStandings(), listTeams()]);
        if (!active) {
          return;
        }

        setItems(standingsRes.items);
        setTeams(teamsRes.items);
      } catch (err) {
        if (!active) {
          return;
        }
        const message = err instanceof Error ? err.message : "순위표를 불러오지 못했습니다.";
        setError(message);
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      active = false;
    };
  }, []);

  const teamMap = useMemo(() => new Map(teams.map((team) => [team.team_id, team])), [teams]);

  return (
    <div className="stack">
      <h1 className="section-title">리그 순위표</h1>
      <p id="standings-note" className="muted">
        모바일에서는 표를 좌우로 스와이프해 GF, GA, GD를 확인하세요.
      </p>
      <div className="row standings-legend" aria-label="순위 구간 안내">
        <span className="legend-item legend-item--ucl">1-4위 UCL</span>
        <span className="legend-item legend-item--uel">5위 UEL</span>
        <span className="legend-item legend-item--relegation">18-20위 강등권</span>
      </div>
      <div className="card table-wrap standings-table-wrap">
        {loading ? (
          <div className="standings-skeleton" aria-live="polite" aria-label="순위표 로딩 중">
            <div className="standings-skeleton__line" />
            <div className="standings-skeleton__line" />
            <div className="standings-skeleton__line" />
            <div className="standings-skeleton__line" />
            <div className="standings-skeleton__line" />
            <div className="standings-skeleton__line" />
          </div>
        ) : error ? (
          <div className="error">순위표 조회 실패: {error}</div>
        ) : items.length === 0 ? (
          <div className="empty">순위 데이터가 없습니다.</div>
        ) : (
          <table className="standings-table" aria-describedby="standings-note">
            <caption className="sr-only">프리미어리그 순위표</caption>
            <thead>
              <tr>
                <th scope="col">순위</th>
                <th scope="col">팀</th>
                <th scope="col">경기</th>
                <th scope="col">승</th>
                <th scope="col">무</th>
                <th scope="col">패</th>
                <th scope="col">GF</th>
                <th scope="col">GA</th>
                <th scope="col">GD</th>
                <th scope="col">승점</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const zoneClass =
                  item.rank <= 4 ? "zone-ucl" : item.rank === 5 ? "zone-uel" : item.rank >= 18 ? "zone-relegation" : "";

                return (
                  <tr key={item.team_id} className={zoneClass}>
                    <td>{item.rank}</td>
                    <th scope="row">{teamMap.get(item.team_id)?.name ?? `Team #${item.team_id}`}</th>
                    <td>{item.played}</td>
                    <td>{item.won}</td>
                    <td>{item.drawn}</td>
                    <td>{item.lost}</td>
                    <td>{item.goals_for}</td>
                    <td>{item.goals_against}</td>
                    <td>{item.goal_diff}</td>
                    <td>
                      <strong>{item.points}</strong>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
