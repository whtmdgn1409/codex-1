import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
    <div className="space-y-6">
      <section className="space-y-2">
        <h1 className="text-2xl font-black tracking-tight sm:text-3xl">구단</h1>
        <p className="text-sm text-muted-foreground">20개 구단 정보를 빠르게 탐색하고 상세 페이지로 이동하세요.</p>
      </section>

      {loading && <div className="rounded-xl border border-dashed border-border px-4 py-3 text-sm">구단 목록 로딩 중...</div>}
      {error && (
        <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-medium text-rose-700">
          구단 목록 조회 실패: {error}
        </div>
      )}

      {!loading && !error && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {teams.map((team) => (
            <Link key={team.team_id} href={`/teams/${team.team_id}`}>
              <Card className="h-full transition hover:-translate-y-0.5 hover:shadow-md">
                <CardHeader className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <CardTitle className="text-lg">{team.name}</CardTitle>
                    <Badge variant="secondary">{team.short_name}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2 text-sm text-muted-foreground">
                  <p>감독: {team.manager ?? "-"}</p>
                  <p>홈구장: {team.stadium ?? "-"}</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
