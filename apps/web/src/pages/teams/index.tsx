import Link from "next/link";
import { useEffect, useState } from "react";

import { listTeams } from "@/lib/api";
import { TeamItem } from "@/lib/types";

export default function TeamsPage() {
  const [teams, setTeams] = useState<TeamItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load(): Promise<void> {
      setLoading(true);
      setError(null);

      try {
        const res = await listTeams();
        if (active) {
          setTeams(res.items);
        }
      } catch (err) {
        if (active) {
          const message = err instanceof Error ? err.message : "구단 데이터를 불러오지 못했습니다.";
          setError(message);
          setTeams([]);
        }
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

  return (
    <div className="stack">
      <h1 className="section-title">구단</h1>
      {loading && <div className="loading">구단 목록 로딩 중...</div>}
      {error && <div className="error">구단 목록 조회 실패: {error}</div>}

      {!loading && !error && (
        <div className="grid grid--3">
          {teams.map((team) => (
            <Link key={team.team_id} href={`/teams/${team.team_id}`} className="card stack">
              <h2 className="card-title">{team.name}</h2>
              <div className="muted">약어: {team.short_name}</div>
              <div className="muted">감독: {team.manager ?? "-"}</div>
              <div className="muted">홈구장: {team.stadium ?? "-"}</div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
