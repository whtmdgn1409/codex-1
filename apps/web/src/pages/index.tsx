import Link from "next/link";
import type { GetServerSideProps, InferGetServerSidePropsType } from "next";

import { listMatches, listStandings, listTeams, topStats } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { MatchListItem, StandingItem, TeamItem, TopStatItem } from "@/lib/types";

type HomeState = {
  matches: MatchListItem[];
  standings: StandingItem[];
  topScorers: TopStatItem[];
  teams: TeamItem[];
};

type HomeProps = {
  state: HomeState;
  error: string | null;
};

const EMPTY_STATE: HomeState = {
  matches: [],
  standings: [],
  topScorers: [],
  teams: []
};

function buildHomeState(state: HomeState): HomeState {
  return {
    matches: state.matches,
    standings: state.standings,
    topScorers: state.topScorers,
    teams: state.teams
  };
}

export const getServerSideProps: GetServerSideProps<HomeProps> = async () => {
  const [matchesRes, standingsRes, scorersRes, teamsRes] = await Promise.allSettled([
    listMatches({ limit: 10, offset: 0 }),
    listStandings(),
    topStats("goals", 3),
    listTeams()
  ]);

  const hasFailure = [matchesRes, standingsRes, scorersRes, teamsRes].some((result) => result.status === "rejected");

  const state = buildHomeState({
    matches: matchesRes.status === "fulfilled" ? matchesRes.value.items : [],
    standings: standingsRes.status === "fulfilled" ? standingsRes.value.items : [],
    topScorers: scorersRes.status === "fulfilled" ? scorersRes.value.items : [],
    teams: teamsRes.status === "fulfilled" ? teamsRes.value.items : []
  });

  return {
    props: {
      state,
      error: hasFailure ? "일부 데이터를 불러오지 못했습니다." : null
    }
  };
};

export default function HomePage({ state, error }: InferGetServerSidePropsType<typeof getServerSideProps>) {
  const safeState = state ?? EMPTY_STATE;
  const teamMap = new Map(safeState.teams.map((team) => [team.team_id, team]));

  const finishedHighlights = safeState.matches.filter((match) => match.status === "FINISHED").slice(0, 4);
  const upcomingHighlights = safeState.matches.filter((match) => match.status !== "FINISHED").slice(0, 3);

  const miniStandings = safeState.standings.filter(
    (item) => item.rank <= 5 || item.rank >= Math.max(18, safeState.standings.length - 2)
  );

  return (
    <div className="stack">
      <h1 className="section-title">프리미어리그 정보 허브</h1>
      {error ? <div className="error">홈 대시보드 부분 조회 실패: {error}</div> : null}

      <section className="grid grid--2">
        <article className="card stack">
          <h2 className="card-title">진행 완료 하이라이트</h2>
          {finishedHighlights.length === 0 ? (
            <div className="empty">최근 종료 경기 데이터가 없습니다.</div>
          ) : (
            finishedHighlights.map((match) => {
              const home = teamMap.get(match.home_team_id);
              const away = teamMap.get(match.away_team_id);

              return (
                <div key={match.match_id} className="row">
                  <div>
                    <div>
                      <strong>{home?.short_name ?? `#${match.home_team_id}`}</strong> {match.home_score ?? "-"} : {" "}
                      {match.away_score ?? "-"} <strong>{away?.short_name ?? `#${match.away_team_id}`}</strong>
                    </div>
                    <div className="muted">{formatDateTime(match.match_date)}</div>
                  </div>
                  <Link className="button-link" href={`/matches/${match.match_id}`}>
                    상세
                  </Link>
                </div>
              );
            })
          )}
        </article>

        <article className="card stack">
          <h2 className="card-title">예정 빅 매치</h2>
          {upcomingHighlights.length === 0 ? (
            <div className="empty">예정된 경기 데이터가 없습니다.</div>
          ) : (
            upcomingHighlights.map((match) => {
              const home = teamMap.get(match.home_team_id);
              const away = teamMap.get(match.away_team_id);

              return (
                <div key={match.match_id} className="stack">
                  <div className="row">
                    <strong>
                      {home?.short_name ?? `#${match.home_team_id}`} vs {away?.short_name ?? `#${match.away_team_id}`}
                    </strong>
                    <span className="badge">Round {match.round}</span>
                  </div>
                  <span className="muted">{formatDateTime(match.match_date)}</span>
                </div>
              );
            })
          )}
        </article>
      </section>

      <section className="grid grid--2">
        <article className="card stack">
          <h2 className="card-title">미니 순위표</h2>
          {miniStandings.length === 0 ? (
            <div className="empty">순위 데이터가 없습니다.</div>
          ) : (
            miniStandings.map((item) => {
              const team = teamMap.get(item.team_id);
              return (
                <div key={item.team_id} className="row">
                  <span>
                    {item.rank}위 {team?.name ?? `Team #${item.team_id}`}
                  </span>
                  <strong>{item.points} pts</strong>
                </div>
              );
            })
          )}
          <Link className="button-link" href="/standings">
            전체 순위 보기
          </Link>
        </article>

        <article className="card stack">
          <h2 className="card-title">득점 Top 3</h2>
          {safeState.topScorers.length === 0 ? (
            <div className="empty">선수 통계 데이터가 없습니다.</div>
          ) : (
            safeState.topScorers.map((item, index) => (
              <div key={item.player_id} className="row">
                <span>
                  {index + 1}. {item.player_name} ({item.team_short_name})
                </span>
                <strong>{item.value}골</strong>
              </div>
            ))
          )}
          <Link className="button-link" href="/stats">
            통계 보기
          </Link>
        </article>
      </section>
    </div>
  );
}
