import { useEffect, useState } from "react";

import { topStats } from "@/lib/api";
import { StatsCategory, TopStatItem } from "@/lib/types";

const CATEGORY_META: Array<{ key: StatsCategory; label: string }> = [
  { key: "goals", label: "득점 순위" },
  { key: "assists", label: "도움 순위" },
  { key: "attack_points", label: "공격포인트" },
  { key: "clean_sheets", label: "클린시트" }
];

export default function StatsPage() {
  const [category, setCategory] = useState<StatsCategory>("goals");
  const [items, setItems] = useState<TopStatItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load(): Promise<void> {
      setLoading(true);
      setError(null);

      try {
        const res = await topStats(category, 20);
        if (active) {
          setItems(res.items);
        }
      } catch (err) {
        if (active) {
          const message = err instanceof Error ? err.message : "통계 데이터를 불러오지 못했습니다.";
          setError(message);
          setItems([]);
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
  }, [category]);

  return (
    <div className="stack">
      <h1 className="section-title">선수 통계</h1>

      <div className="card filters">
        {CATEGORY_META.map((entry) => (
          <button
            key={entry.key}
            type="button"
            className={`gnb__item ${category === entry.key ? "gnb__item--active" : ""}`}
            onClick={() => setCategory(entry.key)}
          >
            {entry.label}
          </button>
        ))}
      </div>

      {loading && <div className="loading">통계 로딩 중...</div>}
      {error && <div className="error">통계 조회 실패: {error}</div>}

      {!loading && !error && (
        <div className="card table-wrap">
          {items.length === 0 ? (
            <div className="empty">통계 데이터가 없습니다.</div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>순위</th>
                  <th>선수</th>
                  <th>팀</th>
                  <th>기록</th>
                  <th>득점</th>
                  <th>도움</th>
                  <th>공격P</th>
                  <th>클린시트</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, index) => (
                  <tr key={item.player_id}>
                    <td>{index + 1}</td>
                    <td>{item.player_name}</td>
                    <td>{item.team_short_name}</td>
                    <td>
                      <strong>{item.value}</strong>
                    </td>
                    <td>{item.goals}</td>
                    <td>{item.assists}</td>
                    <td>{item.attack_points}</td>
                    <td>{item.clean_sheets}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
