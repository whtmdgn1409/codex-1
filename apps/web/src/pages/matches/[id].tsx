import { useRouter } from "next/router";
import { useEffect, useMemo, useState } from "react";

import { getMatch, listTeams } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { MatchDetailResponse, TeamItem } from "@/lib/types";

export default function MatchDetailPage() {
  const router = useRouter();
  const [data, setData] = useState<MatchDetailResponse | null>(null);
  const [teams, setTeams] = useState<TeamItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const matchId = useMemo(() => {
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

    if (matchId === null) {
      setError("잘못된 match id 입니다.");
      setLoading(false);
      return;
    }
    const safeMatchId = matchId;

    let active = true;

    async function load(): Promise<void> {
      setLoading(true);
      setError(null);

      try {
        const [matchRes, teamsRes] = await Promise.all([getMatch(safeMatchId), listTeams()]);
        if (!active) {
          return;
        }

        setData(matchRes);
        setTeams(teamsRes.items);
      } catch (err) {
        if (!active) {
          return;
        }

        const message = err instanceof Error ? err.message : "매치 상세를 불러오지 못했습니다.";
        setError(message);
        setData(null);
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
  }, [router.isReady, matchId]);

  const teamMap = useMemo(() => new Map(teams.map((team) => [team.team_id, team])), [teams]);

  if (loading) {
    return <div className="loading">매치 리포트 로딩 중...</div>;
  }

  if (error) {
    return <div className="error">매치 리포트 조회 실패: {error}</div>;
  }

  if (!data) {
    return <div className="empty">매치 데이터가 없습니다.</div>;
  }

  const home = teamMap.get(data.match.home_team_id);
  const away = teamMap.get(data.match.away_team_id);

  return (
    <div className="stack">
      <h1 className="section-title">Match Detail</h1>

      <section className="card stack">
        <div className="row">
          <span className="badge">Round {data.match.round}</span>
          <span className="muted">{formatDateTime(data.match.match_date)}</span>
        </div>
        <h2 className="card-title">
          {home?.name ?? `Team #${data.match.home_team_id}`} {data.match.home_score ?? "-"} : {data.match.away_score ?? "-"} {" "}
          {away?.name ?? `Team #${data.match.away_team_id}`}
        </h2>
      </section>

      <section className="card stack">
        <h2 className="card-title">타임라인</h2>
        {data.events.length === 0 ? (
          <div className="empty">기록된 이벤트가 없습니다.</div>
        ) : (
          data.events.map((event) => (
            <div key={event.event_id} className="row">
              <strong>{event.minute}&apos;</strong>
              <span>
                {event.event_type}
                {event.player_name ? ` - ${event.player_name}` : ""}
                {event.detail ? ` (${event.detail})` : ""}
              </span>
              <span className="muted">
                {event.team_id ? teamMap.get(event.team_id)?.short_name ?? `#${event.team_id}` : "-"}
              </span>
            </div>
          ))
        )}
      </section>

      <section className="card stack">
        <h2 className="card-title">매치 스탯</h2>
        {data.stats.length === 0 ? (
          <div className="empty">기록된 스탯이 없습니다.</div>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>팀</th>
                  <th>점유율</th>
                  <th>슈팅</th>
                  <th>유효슈팅</th>
                  <th>파울</th>
                  <th>코너킥</th>
                </tr>
              </thead>
              <tbody>
                {data.stats.map((stat) => (
                  <tr key={stat.team_id}>
                    <td>{teamMap.get(stat.team_id)?.name ?? `Team #${stat.team_id}`}</td>
                    <td>{stat.possession ?? "-"}</td>
                    <td>{stat.shots ?? "-"}</td>
                    <td>{stat.shots_on_target ?? "-"}</td>
                    <td>{stat.fouls ?? "-"}</td>
                    <td>{stat.corners ?? "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
