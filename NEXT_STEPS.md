# NEXT STEPS

Last Updated: 2026-02-15
Primary Focus: Web 제품화(디자인/배포) + 운영 가드레일 고정 + 데이터 품질 고도화

## A) Current Status

### Backend/API
- 완료: `API-001`~`API-005`
- 완료: OpenAPI 스냅샷 테스트 + API 통합 테스트(`API-002`~`API-005`) CI 필수 단계 반영
- 완료: `GET /matches/{id}`, `GET /teams/{id}` 404 응답 스키마 명시

### Frontend
- 완료: Next.js + TypeScript 기반 라우트 MVP
  - `/`, `/matches`, `/matches/[id]`, `/standings`, `/stats`, `/teams`, `/teams/[id]`
- 완료: `WEB-DESIGN-001` shadcn 기반 리디자인 1차
  - 공통 토큰/유틸(`tailwind`, `cn`) 및 UI primitives(`button/card/badge`) 적용
  - 핵심 화면(`/`, `/matches`, `/teams`) 리프레시 및 반응형 정합성 확보
- 완료: 핵심 품질 작업
  - `WEB-Q-001`: match detail 탭 lazy render + dynamic import
  - `WEB-Q-002`: home SSR prefetch(`getServerSideProps`) 전환
  - `WEB-Q-003`: matches 필터 debounce + 단계적 렌더(더보기)
  - `WEB-Q-004`: standings 접근성/모바일 안정화(caption/scope/legend/skeleton)
- 완료: `make web-lint`, `make web-build` 통과
- 완료: Playwright E2E 핵심 플로우 2건 구축

### Crawler/Batch
- 완료: `CRAWL-001` 샘플 소스 멱등 업서트
- 완료: `CRAWL-002` 공식 소스 파서 고도화 + 운영 fallback 정책 확정
  - teams/matches seed fallback 기본 활성
  - players/match_stats fetch 실패 시 skip 정책 반영
- 완료: `CRAWL-002` CI live validate 성공 (`run 22008172330`)
- 완료: `docs/crawl-002-ingest-report.md` 상태 `COMPLETED`
- 완료: `BATCH-001`, `BATCH-002`, `BATCH-003` (일/주 스케줄 + 재시도 + Slack 알림)
- 진행중: `CRAWL-003` API-Football 적재 확장(MVP)
  - 완료 범위: `teams`, `players`, `matches`, `match_stats`, `standings` 수집/적재 구현 + 환경변수/문서/테스트 반영
  - 잔여 범위: 운영 시크릿(`API_FOOTBALL_KEY`) 연결 후 live ingest 리허설 최종 완료
  - 블로커: 로컬 환경 DNS 제약으로 API-Football 실호출 실패(Errno 8), CI runner에서 재검증 필요

### Infra/CI
- 완료: `CI / api`, `CI / web-e2e` 필수 단계화
- 완료: `Crawler Live Validate` 워크플로 추가
- 완료: `Lighthouse Baseline` 워크플로 추가 + 리포트 아카이브
- 완료: `DEPLOY-001` 배포 파이프라인 초안
  - `Vercel Deploy` 워크플로 추가(PR Preview + main Production)
- 진행중: `main` PR-only/관리자 우회 금지 정책 최종 고정 점검

### Known Issues / Risks
- `apps/web` 의존성 취약점 경고(`npm audit`) 잔여
- `CRAWL-002`는 안정화되었지만 teams/matches에서 seed fallback 의존 구간 존재
- Lighthouse 자동화는 동작하지만 기준치 대비 추세 리포트(회귀 경보)는 미구축

## B) Next Priorities

### P0
1. 배포 트랙(Vercel) 실배포 검증
- 범위: Preview/Production 파이프라인 구성
- DoD:
  - Vercel 프로젝트 연결 및 GitHub Secrets 적용 검증
  - 환경변수 템플릿/운영 문서 정리 및 실제 값 반영
  - PR Preview URL 확인 가능

2. 운영 가드레일 최종 고정
- DoD:
  - `main`에 PR-only + required checks 강제 상태 재확인
  - 관리자 우회 푸시 금지 상태 문서화

### P1
1. UI 리디자인 트랙(shadcn) 2차
- DoD:
  - `/standings`, `/stats`, `/matches/[id]`, `/teams/[id]` shadcn 스타일 정렬
  - legacy CSS 클래스 의존 제거 및 컴포넌트 단위 통일

2. Web 성능 회귀 관리
- DoD:
  - Lighthouse baseline 대비 개선/악화 비교표 자동 생성
  - 라우트별 fail threshold 정의(Performance/A11y)

3. Crawler 품질 고도화
- DoD:
  - teams/matches 공식 파서 커버리지 확장
  - seed fallback 사용률/원인 리포트 항목 추가

### P2
1. 웹 의존성 취약점 정리
- DoD:
  - 취약점 영향도 분류(즉시/계획/무시)
  - 업그레이드 계획 + 검증 체크리스트 수립

## C) In Progress
- `DEPLOY-001`: Vercel 실배포 검증(Secrets 연결 + Preview URL 확인)
- `CRAWL-003`: 운영 시크릿 연결 후 API-Football live ingest 리허설

## D) Done Log
- 2026-02-15
  - `CRAWL-003` 2차: API-Football `players`, `match_stats` 파서 구현 및 정책(`skip/abort`) 반영
  - crawler schema 보강: `player_season_stats`, `match_events` sqlite 테이블 추가(API 호환)
  - API-DB 연계 검증 스크립트 `scripts/verify_api_db_flow.py` 추가 (`make verify-api-flow` 통과)
  - API-Football live 리허설 시도 결과: 로컬 DNS 제약으로 실패, CI runner 재시도 필요
- 2026-02-15
  - `CRAWL-003` 1차: `ApiFootballDataSource` 추가, teams/matches/standings 적재 MVP 구현
  - `ingest-standings` CLI/배치 경로 추가, `PL_POLICY_STANDINGS`/`API_FOOTBALL_*` 환경변수 및 운영 문서 반영
  - crawler 테스트 30건 통과(`make crawler-test`)
- 2026-02-15
  - `DEPLOY-001` Vercel 전환: `.github/workflows/vercel-deploy.yml` 추가, Netlify 설정 제거, 운영 문서/우선순위 갱신
- 2026-02-15
  - `WEB-DESIGN-001` 1차 완료: Tailwind + shadcn primitives 도입, `/`, `/matches`, `/teams` 리디자인, `make web-lint/web-build` 통과
- 2026-02-15
  - 문서 정합화: `NEXT_STEPS.md`, `README.md` 현재 상태/다음 계획 동기화
- 2026-02-14
  - `WEB-Q-004` 적용: standings 접근성/모바일 안정화
  - `WEB-Q-003` 적용: matches 렌더 최적화
  - `CRAWL-002` CI live validate 성공 및 `COMPLETED` 전환
  - `CRAWL-002` teams/matches seed fallback 운영정책 반영
  - Lighthouse baseline/Live validate 워크플로 운영 반영
- 2026-02-13
  - API MVP + 테스트/CI 필수화
  - Web MVP 라우트 구축
  - Batch scheduler + retry/alert 구축

## E) Working Rules
1. 개발 시작 전
- `NEXT_STEPS.md`의 `Primary Focus`, `P0/P1` 확인
- 작업 시작 시 `C) In Progress` 반영

2. 개발 완료 후
- `A) Current Status`, `B) Next Priorities`, `D) Done Log` 업데이트

3. PR 규칙
- PR 본문에 `NEXT_STEPS.md 반영 여부` 명시
- 문서 반영이 필요한 변경에서 누락 시 머지 금지
