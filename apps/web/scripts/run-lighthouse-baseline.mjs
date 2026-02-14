import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const WEB_DIR = path.resolve(__dirname, "..");
const REPO_ROOT = path.resolve(WEB_DIR, "..", "..");
const REPORT_DIR = path.join(REPO_ROOT, "docs", "reports", "lighthouse");
const WEB_BASE_URL = "http://127.0.0.1:3000";
const API_BASE_URL = "http://127.0.0.1:8000";
const ITERATIONS = 3;

const routes = [
  { slug: "home", path: "/" },
  { slug: "matches", path: "/matches" },
  { slug: "match-detail", path: "/matches/100" },
  { slug: "standings", path: "/standings" }
];

const presets = [
  { slug: "mobile", args: [] },
  { slug: "desktop", args: ["--preset=desktop"] }
];

function buildMockPayload(url) {
  const parsed = new URL(url, API_BASE_URL);
  const { pathname } = parsed;

  const teams = [
    { team_id: 1, name: "Arsenal FC", short_name: "ARS", logo_url: null, stadium: "Emirates Stadium", manager: "Mikel Arteta" },
    { team_id: 2, name: "Liverpool FC", short_name: "LIV", logo_url: null, stadium: "Anfield", manager: "Arne Slot" },
    { team_id: 3, name: "Chelsea FC", short_name: "CHE", logo_url: null, stadium: "Stamford Bridge", manager: "Enzo Maresca" }
  ];

  const matches = [
    { match_id: 100, round: 24, match_date: "2026-02-12T20:00:00Z", home_team_id: 1, away_team_id: 2, home_score: 2, away_score: 1, status: "FINISHED" },
    { match_id: 101, round: 25, match_date: "2026-02-20T20:00:00Z", home_team_id: 3, away_team_id: 1, home_score: null, away_score: null, status: "SCHEDULED" }
  ];

  const standings = [
    { team_id: 1, rank: 1, played: 24, won: 18, drawn: 4, lost: 2, goals_for: 55, goals_against: 20, goal_diff: 35, points: 58 },
    { team_id: 2, rank: 2, played: 24, won: 17, drawn: 5, lost: 2, goals_for: 52, goals_against: 23, goal_diff: 29, points: 56 },
    { team_id: 3, rank: 3, played: 24, won: 15, drawn: 4, lost: 5, goals_for: 48, goals_against: 27, goal_diff: 21, points: 49 }
  ];

  const topScorers = [
    {
      player_id: 10,
      player_name: "Bukayo Saka",
      team_id: 1,
      team_name: "Arsenal FC",
      team_short_name: "ARS",
      value: 15,
      goals: 15,
      assists: 9,
      attack_points: 24,
      clean_sheets: 0
    }
  ];

  if (pathname === "/matches") {
    return { status: 200, body: { total: matches.length, items: matches } };
  }

  if (pathname === "/matches/100") {
    return {
      status: 200,
      body: {
        match: matches[0],
        events: [
          { event_id: 1, minute: 24, event_type: "GOAL", team_id: 1, player_name: "Bukayo Saka", detail: null },
          { event_id: 2, minute: 89, event_type: "GOAL", team_id: 2, player_name: "Mohamed Salah", detail: null }
        ],
        stats: [
          { team_id: 1, possession: 55, shots: 12, shots_on_target: 6, fouls: 9, corners: 4 },
          { team_id: 2, possession: 45, shots: 8, shots_on_target: 3, fouls: 11, corners: 2 }
        ]
      }
    };
  }

  if (pathname === "/standings") {
    return { status: 200, body: { total: standings.length, items: standings } };
  }

  if (pathname === "/stats/top") {
    return { status: 200, body: { category: "goals", total: topScorers.length, items: topScorers } };
  }

  if (pathname === "/teams") {
    return { status: 200, body: { total: teams.length, items: teams } };
  }

  if (pathname === "/teams/1") {
    return {
      status: 200,
      body: {
        team: teams[0],
        recent_form: ["W", "D", "L", "W", "W"],
        squad: [
          { player_id: 10, name: "Bukayo Saka", position: "FW", jersey_num: 7, nationality: "England", photo_url: null }
        ]
      }
    };
  }

  return { status: 404, body: { detail: "not found" } };
}

function startMockApiServer() {
  const server = http.createServer((req, res) => {
    if (!req.url) {
      res.writeHead(400, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ detail: "bad request" }));
      return;
    }

    const payload = buildMockPayload(req.url);
    res.writeHead(payload.status, { "Content-Type": "application/json" });
    res.end(JSON.stringify(payload.body));
  });

  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(8000, "127.0.0.1", () => resolve(server));
  });
}

function waitForServer(url, timeoutMs = 60_000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const attempt = () => {
      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode < 500) {
          resolve();
          return;
        }
        if (Date.now() - start >= timeoutMs) {
          reject(new Error(`Timed out waiting for ${url}`));
          return;
        }
        setTimeout(attempt, 1000);
      });

      req.on("error", () => {
        if (Date.now() - start >= timeoutMs) {
          reject(new Error(`Timed out waiting for ${url}`));
          return;
        }
        setTimeout(attempt, 1000);
      });
    };

    attempt();
  });
}

function runCommand(cmd, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, { stdio: "inherit", ...options });
    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`${cmd} ${args.join(" ")} failed with exit code ${code ?? "unknown"}`));
      }
    });
  });
}

function median(values) {
  if (values.length === 0) {
    return null;
  }
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 1) {
    return sorted[mid];
  }
  return Number(((sorted[mid - 1] + sorted[mid]) / 2).toFixed(2));
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf-8"));
}

function toFixedNumber(value, digits = 2) {
  return Number(value.toFixed(digits));
}

function extractMetrics(report) {
  return {
    performance: toFixedNumber((report.categories.performance?.score ?? 0) * 100),
    accessibility: toFixedNumber((report.categories.accessibility?.score ?? 0) * 100),
    bestPractices: toFixedNumber((report.categories["best-practices"]?.score ?? 0) * 100),
    seo: toFixedNumber((report.categories.seo?.score ?? 0) * 100),
    lcpMs: toFixedNumber((report.audits["largest-contentful-paint"]?.numericValue ?? 0), 0),
    inpMs: toFixedNumber((report.audits["interaction-to-next-paint"]?.numericValue ?? 0), 0),
    cls: toFixedNumber((report.audits["cumulative-layout-shift"]?.numericValue ?? 0), 3),
    tbtMs: toFixedNumber((report.audits["total-blocking-time"]?.numericValue ?? 0), 0)
  };
}

function writeSummary(summary) {
  const summaryJsonPath = path.join(REPORT_DIR, "baseline-summary.json");
  const summaryMdPath = path.join(REPORT_DIR, "baseline-summary.md");

  fs.writeFileSync(summaryJsonPath, JSON.stringify(summary, null, 2), "utf-8");

  const lines = [
    "# Lighthouse Baseline",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    "| Route | Preset | Perf | A11y | BP | SEO | LCP(ms) | INP(ms) | CLS | TBT(ms) |",
    "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
  ];

  for (const row of summary.rows) {
    lines.push(
      `| ${row.route} | ${row.preset} | ${row.performance} | ${row.accessibility} | ${row.bestPractices} | ${row.seo} | ${row.lcpMs} | ${row.inpMs} | ${row.cls} | ${row.tbtMs} |`
    );
  }

  fs.writeFileSync(summaryMdPath, `${lines.join("\n")}\n`, "utf-8");
}

async function run() {
  fs.mkdirSync(REPORT_DIR, { recursive: true });

  const apiServer = await startMockApiServer();
  const nextProcess = spawn("npm", ["run", "start"], {
    cwd: WEB_DIR,
    env: {
      ...process.env,
      NEXT_PUBLIC_API_BASE_URL: API_BASE_URL
    },
    stdio: "inherit"
  });

  try {
    await waitForServer(`${WEB_BASE_URL}/`);

    const rowAccumulator = [];

    for (const route of routes) {
      for (const preset of presets) {
        const reports = [];

        for (let runIndex = 1; runIndex <= ITERATIONS; runIndex += 1) {
          const outputPath = path.join(REPORT_DIR, `${route.slug}-${preset.slug}-run${runIndex}.json`);
          const targetUrl = `${WEB_BASE_URL}${route.path}`;
          const args = [
            "--yes",
            "lighthouse",
            targetUrl,
            "--output=json",
            `--output-path=${outputPath}`,
            "--quiet",
            "--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage",
            ...preset.args
          ];

          await runCommand("npx", args, { cwd: WEB_DIR });
          reports.push(extractMetrics(readJson(outputPath)));
        }

        rowAccumulator.push({
          route: route.path,
          preset: preset.slug,
          performance: median(reports.map((item) => item.performance)),
          accessibility: median(reports.map((item) => item.accessibility)),
          bestPractices: median(reports.map((item) => item.bestPractices)),
          seo: median(reports.map((item) => item.seo)),
          lcpMs: median(reports.map((item) => item.lcpMs)),
          inpMs: median(reports.map((item) => item.inpMs)),
          cls: median(reports.map((item) => item.cls)),
          tbtMs: median(reports.map((item) => item.tbtMs))
        });
      }
    }

    writeSummary({ rows: rowAccumulator });
  } finally {
    apiServer.close();
    nextProcess.kill("SIGTERM");
  }
}

run().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
