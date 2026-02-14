import { expect, Page, test } from "@playwright/test";

const API_BASES = ["http://api.epl.test", "http://localhost:8000"];

async function routeApi(page: Page, path: string, handler: (route: any) => Promise<void>): Promise<void> {
  await Promise.all(
    API_BASES.map((base) => page.route(`${base}${path}`, handler))
  );
}

async function mockCoreApi(page: Page): Promise<void> {
  await routeApi(page, "/matches**", async (route) => {
    const url = new URL(route.request().url());
    const pathname = url.pathname;
    if (pathname === "/matches") {
      const items = [
        {
          match_id: 100,
          round: 24,
          match_date: "2026-02-12T20:00:00Z",
          home_team_id: 1,
          away_team_id: 2,
          home_score: 2,
          away_score: 1,
          status: "FINISHED"
        },
        {
          match_id: 101,
          round: 25,
          match_date: "2026-02-20T20:00:00Z",
          home_team_id: 3,
          away_team_id: 1,
          home_score: null,
          away_score: null,
          status: "SCHEDULED"
        }
      ];

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ total: items.length, items })
      });
      return;
    }

    if (pathname === "/matches/100") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          match: {
            match_id: 100,
            round: 24,
            match_date: "2026-02-12T20:00:00Z",
            home_team_id: 1,
            away_team_id: 2,
            home_score: 2,
            away_score: 1,
            status: "FINISHED"
          },
          events: [
            { event_id: 1, minute: 24, event_type: "GOAL", team_id: 1, player_name: "Bukayo Saka", detail: null },
            { event_id: 2, minute: 89, event_type: "GOAL", team_id: 2, player_name: "Mohamed Salah", detail: null }
          ],
          stats: [
            { team_id: 1, possession: 55, shots: 12, shots_on_target: 6, fouls: 9, corners: 4 },
            { team_id: 2, possession: 45, shots: 8, shots_on_target: 3, fouls: 11, corners: 2 }
          ]
        })
      });
      return;
    }

    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: "not found" })
    });
  });

  await routeApi(page, "/teams", async (route) => {
    const url = new URL(route.request().url());
    const pathname = url.pathname;

    if (pathname === "/teams") {
      const items = [
        {
          team_id: 1,
          name: "Arsenal FC",
          short_name: "ARS",
          logo_url: null,
          stadium: "Emirates Stadium",
          manager: "Mikel Arteta"
        },
        {
          team_id: 2,
          name: "Liverpool FC",
          short_name: "LIV",
          logo_url: null,
          stadium: "Anfield",
          manager: "Arne Slot"
        },
        {
          team_id: 3,
          name: "Chelsea FC",
          short_name: "CHE",
          logo_url: null,
          stadium: "Stamford Bridge",
          manager: "Enzo Maresca"
        }
      ];

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ total: items.length, items })
      });
      return;
    }
    await route.fallback();
  });

  await routeApi(page, "/teams/**", async (route) => {
    const url = new URL(route.request().url());
    const pathname = url.pathname;

    if (pathname === "/teams/1") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          team: {
            team_id: 1,
            name: "Arsenal FC",
            short_name: "ARS",
            logo_url: null,
            stadium: "Emirates Stadium",
            manager: "Mikel Arteta"
          },
          recent_form: ["W", "D", "L", "W", "W"],
          squad: [
            {
              player_id: 10,
              name: "Bukayo Saka",
              position: "FW",
              jersey_num: 7,
              nationality: "England",
              photo_url: null
            }
          ]
        })
      });
      return;
    }

    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({ detail: "not found" })
    });
  });

  await routeApi(page, "/standings", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            team_id: 1,
            rank: 1,
            played: 24,
            won: 18,
            drawn: 4,
            lost: 2,
            goals_for: 55,
            goals_against: 20,
            goal_diff: 35,
            points: 58
          }
        ]
      })
    });
  });

  await routeApi(page, "/stats/top", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            player_id: 10,
            player_name: "Bukayo Saka",
            team_id: 1,
            team_short_name: "ARS",
            value: 15
          }
        ]
      })
    });
  });

  await routeApi(page, "/stats/top**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        items: [
          {
            player_id: 10,
            player_name: "Bukayo Saka",
            team_id: 1,
            team_short_name: "ARS",
            value: 15
          }
        ]
      })
    });
  });
}

test.beforeEach(async ({ page }) => {
  await mockCoreApi(page);
});

test("home -> matches -> match detail flow", async ({ page }) => {
  await page.goto("/");

  await expect(page.locator("h1.section-title")).toContainText("프리미어리그 정보 허브");
  await page.getByRole("link", { name: "일정/결과" }).click();

  await expect(page).toHaveURL(/\/matches$/);
  await expect(page.locator("h1.section-title")).toContainText("일정 / 결과");

  await page.getByRole("link", { name: "매치 리포트" }).first().click();

  await expect(page).toHaveURL(/\/matches\/100$/);
  const detailTitle = page.locator("h1.section-title");
  const detailError = page.locator(".error");
  await Promise.race([
    detailTitle.waitFor({ state: "visible", timeout: 7000 }),
    detailError.waitFor({ state: "visible", timeout: 7000 })
  ]);
});

test("teams list -> team detail flow", async ({ page }) => {
  await page.goto("/teams");

  await expect(page.locator("h1.section-title")).toContainText("구단");
  await page.getByRole("link", { name: /Arsenal FC/ }).first().click();

  await expect(page).toHaveURL(/\/teams\/1$/);
  await expect(page.locator("h1.section-title")).toContainText("Arsenal FC");
  await expect(page.locator("h2.card-title", { hasText: "최근 5경기 폼" })).toBeVisible();
  await expect(page.locator("h2.card-title", { hasText: "시즌 스쿼드" })).toBeVisible();
});
