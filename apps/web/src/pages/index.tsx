import type { GetServerSideProps, InferGetServerSidePropsType } from "next";
import Link from "next/link";

import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateTime } from "@/lib/format";
import { cn } from "@/lib/utils";
import { listMatches, listStandings, listTeams, topStats } from "@/lib/api";
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
    <div className="space-y-6">
      <section className="rounded-2xl border border-border/70 bg-gradient-to-br from-[#e8f1ff] via-[#f4f8ff] to-white p-5 sm:p-7">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary/80">Premier League</p>
        <h1 className="mt-2 text-2xl font-black tracking-tight sm:text-3xl">프리미어리그 정보 허브</h1>
        <p className="mt-2 max-w-2xl text-sm text-muted-foreground sm:text-base">
          매치 결과, 순위, 주요 선수 기록을 한 화면에서 빠르게 확인하세요.
        </p>
      </section>

      {error ? (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
          홈 대시보드 부분 조회 실패: {error}
        </div>
      ) : null}

      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>진행 완료 하이라이트</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {finishedHighlights.length === 0 ? (
              <p className="rounded-lg border border-dashed border-border px-4 py-3 text-sm text-muted-foreground">
                최근 종료 경기 데이터가 없습니다.
              </p>
            ) : (
              finishedHighlights.map((match) => {
                const home = teamMap.get(match.home_team_id);
                const away = teamMap.get(match.away_team_id);

                return (
                  <div key={match.match_id} className="flex flex-col gap-3 rounded-lg border border-border/70 p-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm font-semibold">
                        <span>{home?.short_name ?? `#${match.home_team_id}`}</span> {match.home_score ?? "-"} : {" "}
                        {match.away_score ?? "-"} <span>{away?.short_name ?? `#${match.away_team_id}`}</span>
                      </p>
                      <p className="text-xs text-muted-foreground">{formatDateTime(match.match_date)}</p>
                    </div>
                    <Link
                      className={buttonVariants({ size: "sm" })}
                      href={`/matches/${match.match_id}`}
                    >
                      상세
                    </Link>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>예정 빅 매치</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {upcomingHighlights.length === 0 ? (
              <p className="rounded-lg border border-dashed border-border px-4 py-3 text-sm text-muted-foreground">
                예정된 경기 데이터가 없습니다.
              </p>
            ) : (
              upcomingHighlights.map((match) => {
                const home = teamMap.get(match.home_team_id);
                const away = teamMap.get(match.away_team_id);

                return (
                  <div key={match.match_id} className="space-y-2 rounded-lg border border-border/70 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <strong className="text-sm sm:text-base">
                        {home?.short_name ?? `#${match.home_team_id}`} vs {away?.short_name ?? `#${match.away_team_id}`}
                      </strong>
                      <Badge variant="secondary">Round {match.round}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">{formatDateTime(match.match_date)}</p>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>미니 순위표</CardTitle>
            <Link className={cn(buttonVariants({ variant: "secondary", size: "sm" }), "text-xs")} href="/standings">
              전체 순위 보기
            </Link>
          </CardHeader>
          <CardContent className="space-y-2">
            {miniStandings.length === 0 ? (
              <p className="rounded-lg border border-dashed border-border px-4 py-3 text-sm text-muted-foreground">
                순위 데이터가 없습니다.
              </p>
            ) : (
              miniStandings.map((item) => {
                const team = teamMap.get(item.team_id);
                return (
                  <div key={item.team_id} className="flex items-center justify-between rounded-lg border border-border/60 px-3 py-2 text-sm">
                    <span>
                      {item.rank}위 {team?.name ?? `Team #${item.team_id}`}
                    </span>
                    <strong>{item.points} pts</strong>
                  </div>
                );
              })
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center justify-between">
            <CardTitle>득점 Top 3</CardTitle>
            <Link className={cn(buttonVariants({ variant: "secondary", size: "sm" }), "text-xs")} href="/stats">
              통계 보기
            </Link>
          </CardHeader>
          <CardContent className="space-y-2">
            {safeState.topScorers.length === 0 ? (
              <p className="rounded-lg border border-dashed border-border px-4 py-3 text-sm text-muted-foreground">
                선수 통계 데이터가 없습니다.
              </p>
            ) : (
              safeState.topScorers.map((item, index) => (
                <div
                  key={item.player_id}
                  className="flex items-center justify-between rounded-lg border border-border/60 px-3 py-2 text-sm"
                >
                  <span>
                    {index + 1}. {item.player_name} ({item.team_short_name})
                  </span>
                  <strong>{item.value}골</strong>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
