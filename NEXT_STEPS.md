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

### Infra/CI
- 완료: `CI / api`, `CI / web-e2e` 필수 단계화
- 완료: `Crawler Live Validate` 워크플로 추가
- 완료: `Lighthouse Baseline` 워크플로 추가 + 리포트 아카이브
- 진행중: `main` PR-only/관리자 우회 금지 정책 최종 고정 점검

### Known Issues / Risks
- `apps/web` 의존성 취약점 경고(`npm audit`) 잔여
- `CRAWL-002`는 안정화되었지만 teams/matches에서 seed fallback 의존 구간 존재
- Lighthouse 자동화는 동작하지만 기준치 대비 추세 리포트(회귀 경보)는 미구축

## B) Next Priorities

### P0
1. UI 리디자인 트랙(shadcn)
- 범위: 홈/매치/구단 핵심 화면을 shadcn 기반으로 재구성
- DoD:
  - 공통 UI 토큰/컴포넌트 정리(button/card/table/tabs)
  - 모바일/데스크탑에서 레이아웃 일관성 확보
  - 기존 기능/라우팅 회귀 없음

2. 배포 트랙(Netlify)
- 범위: Preview/Production 파이프라인 구성
- DoD:
  - Netlify 사이트 연결 및 빌드 설정 확정
  - 환경변수 템플릿/운영 문서 정리
  - PR Preview URL 확인 가능

3. 운영 가드레일 최종 고정
- DoD:
  - `main`에 PR-only + required checks 강제 상태 재확인
  - 관리자 우회 푸시 금지 상태 문서화

### P1
1. Web 성능 회귀 관리
- DoD:
  - Lighthouse baseline 대비 개선/악화 비교표 자동 생성
  - 라우트별 fail threshold 정의(Performance/A11y)

2. Crawler 품질 고도화
- DoD:
  - teams/matches 공식 파서 커버리지 확장
  - seed fallback 사용률/원인 리포트 항목 추가

### P2
1. 웹 의존성 취약점 정리
- DoD:
  - 취약점 영향도 분류(즉시/계획/무시)
  - 업그레이드 계획 + 검증 체크리스트 수립

## C) In Progress
- `WEB-DESIGN-001`: shadcn 전환 설계(컴포넌트 맵/우선 화면 정의)
- `DEPLOY-001`: Netlify 배포 설정 초안(환경변수/빌드 명령/Preview 전략)

## D) Done Log
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
