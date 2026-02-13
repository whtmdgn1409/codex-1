import { useRouter } from "next/router";
import { useEffect, useMemo, useState } from "react";

import { getTeam } from "@/lib/api";
import { SquadPlayerItem, TeamDetailResponse } from "@/lib/types";

function formSymbol(result: "W" | "D" | "L"): string {
  if (result === "W") {
    return "🟢 승";
  }
  if (result === "L") {
    return "🔴 패";
  }
  return "⚪ 무";
}

export default function TeamDetailPage() {
  const router = useRouter();
  const [data, setData] = useState<TeamDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const teamId = useMemo(() => {
    const raw = router.query.id;
    if (!raw) {
      return null;
    }

    const parsed = Number(Array.isArray(raw) ? raw[0] : raw);
    return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
  }, [router.query.id]);

  useEffect(() => {
    if (!router.isReady) {
      return;
    }

    if (teamId === null) {
      setError("잘못된 team id 입니다.");
      setLoading(false);
      return;
    }
    const safeTeamId = teamId;

    let active = true;

    async function load(): Promise<void> {
      setLoading(true);
      setError(null);

      try {
        const res = await getTeam(safeTeamId);
        if (active) {
          setData(res);
        }
      } catch (err) {
        if (active) {
          const message = err instanceof Error ? err.message : "구단 상세를 불러오지 못했습니다.";
          setError(message);
          setData(null);
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
  }, [router.isReady, teamId]);

  const groupedSquad = useMemo(() => {
    const groups: Record<string, SquadPlayerItem[]> = {};

    (data?.squad ?? []).forEach((player) => {
      if (!groups[player.position]) {
        groups[player.position] = [];
      }
      groups[player.position].push(player);
    });

    return Object.entries(groups);
  }, [data?.squad]);

  if (loading) {
    return <div className="loading">구단 상세 로딩 중...</div>;
  }

  if (error) {
    return <div className="error">구단 상세 조회 실패: {error}</div>;
  }

  if (!data) {
    return <div className="empty">구단 데이터가 없습니다.</div>;
  }

  return (
    <div className="stack">
      <h1 className="section-title">{data.team.name}</h1>

      <section className="card stack">
        <div className="row">
          <span className="badge">{data.team.short_name}</span>
          <span className="muted">감독: {data.team.manager ?? "-"}</span>
        </div>
        <div className="muted">홈 구장: {data.team.stadium ?? "-"}</div>
      </section>

      <section className="card stack">
        <h2 className="card-title">최근 5경기 폼</h2>
        {data.recent_form.length === 0 ? (
          <div className="empty">최근 경기 기록이 없습니다.</div>
        ) : (
          <div className="row">
            {data.recent_form.map((result, index) => (
              <span key={`${result}-${index}`}>{formSymbol(result)}</span>
            ))}
          </div>
        )}
      </section>

      <section className="card stack">
        <h2 className="card-title">시즌 스쿼드</h2>
        {groupedSquad.length === 0 ? (
          <div className="empty">스쿼드 데이터가 없습니다.</div>
        ) : (
          groupedSquad.map(([position, players]) => (
            <div key={position} className="stack">
              <strong>{position}</strong>
              {players.map((player) => (
                <div key={player.player_id} className="row">
                  <span>
                    {player.name} {player.jersey_num ? `#${player.jersey_num}` : ""}
                  </span>
                  <span className="muted">{player.nationality ?? "-"}</span>
                </div>
              ))}
            </div>
          ))
        )}
      </section>
    </div>
  );
}
