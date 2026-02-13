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

  if (loading) {
    return <div className="loading">순위표 로딩 중...</div>;
  }

  if (error) {
    return <div className="error">순위표 조회 실패: {error}</div>;
  }

  return (
    <div className="stack">
      <h1 className="section-title">리그 순위표</h1>
      <div className="card table-wrap">
        {items.length === 0 ? (
          <div className="empty">순위 데이터가 없습니다.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>순위</th>
                <th>팀</th>
                <th>경기</th>
                <th>승</th>
                <th>무</th>
                <th>패</th>
                <th>GF</th>
                <th>GA</th>
                <th>GD</th>
                <th>승점</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const zoneClass =
                  item.rank <= 4 ? "zone-ucl" : item.rank === 5 ? "zone-uel" : item.rank >= 18 ? "zone-relegation" : "";

                return (
                  <tr key={item.team_id} className={zoneClass}>
                    <td>{item.rank}</td>
                    <td>{teamMap.get(item.team_id)?.name ?? `Team #${item.team_id}`}</td>
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
