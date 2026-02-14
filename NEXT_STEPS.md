# NEXT STEPS

Last Updated: 2026-02-14
Primary Focus: CRAWL-002 완료 전환 + 운영 가드레일 고정 + Web 성능 실측/개선

## A) Current Status

### Backend/API
- 완료: `API-001`~`API-005`
- 완료: OpenAPI 스냅샷 테스트 + API 통합 테스트(`API-002`~`API-005`) CI 필수 단계 반영
- 완료: `GET /matches/{id}`, `GET /teams/{id}`에 404 응답 스키마 명시

### Frontend
- 완료: Next.js + TypeScript 초기 구축 (`apps/web`)
- 완료: 라우트 1차 구현
  - `/`, `/matches`, `/matches/[id]`, `/standings`, `/stats`, `/teams`, `/teams/[id]`
- 완료: `make web-lint`, `make web-build` 통과
- 완료: `make web-dev` 기동 확인 (`http://localhost:3000`)
- 완료: Playwright E2E 핵심 플로우 2건 추가 및 로컬 실행 검증 (`apps/web/tests/e2e/core-flows.spec.ts`)

### Infra/CI
- 완료: `CI / api` 워크플로 구성
- 완료: 브랜치 보호 규칙에 `CI / api` 필수 체크 적용
- 완료: `Batch Scheduler` 워크플로 추가 (일/주 배치 cron + 수동 실행)
- 완료: `CI`에 Web E2E job 추가 및 필수 단계로 전환
- 완료: `Crawler Live Validate` 워크플로 추가 (실사이트 validate + JSON artifact)
- 완료: `Lighthouse Baseline` 워크플로 추가 (핵심 라우트 모바일/데스크탑 3회 측정 + 리포트 artifact)

### Crawler/Batch
- 완료: `CRAWL-001` 초기 수집 파이프라인(샘플 소스 + 멱등 업서트)
- 완료: `BATCH-001` 일배치 스케줄러 연동 (`make crawler-daily`, 매일 09:00 KST)
- 완료: `BATCH-002` 주배치 스케줄러 연동 (`make crawler-weekly`, 매주 목 12:00 KST)
- 완료: `BATCH-003` 실패 재시도/Slack 알림 연동 (`BATCH_RETRY_*`, `BATCH_ALERT_SLACK_WEBHOOK`)
- 진행중: `CRAWL-002` 공식 사이트 파서 고도화 (table alias + JSON fallback + JS assignment/PULSE fallback + dataset 정책)
- 완료: `CRAWL-002` fixture 기반 파서 회귀테스트 추가 (`apps/crawler/tests/fixtures/premier_league/*`)
- 완료: `CRAWL-002` ingest 리포트 템플릿 추가 (`docs/crawl-002-ingest-report.md`)
- 진행중: `CRAWL-002` `pl` 실측 ingest 결과(요약 카운트/검증 JSON) 수집 및 리포트 확정

### Known Issues / Risks
- `apps/web` 의존성에서 보안 취약점 경고 존재 (`npm audit` 기준 4건)
- 현재 `main` 브랜치에 관리자 우회 푸시가 가능했던 이력 존재 (PR-only 운영 고정 필요)
- `CRAWL-002` 실사이트 validate 시 DNS 해석 오류 발생 (`gaierror: nodename nor servname provided`)
- `CRAWL-002` CI runner live validate에서도 `teams` dataset 파싱 0건으로 실패 (`no_records_after_all_strategies`)
- Lighthouse CLI 설치/실행이 현재 네트워크 제약으로 타임아웃(실측 자동화 지연)

## B) Next Priorities

### P0
1. Crawler 소스 확장 (Premier League 공식 사이트 파서 도입)
- 목적: 샘플 데이터가 아닌 실제 시즌 데이터 적재
- DoD:
  - `docs/crawl-002-ingest-report.md`에 `pl` 실측 실행 근거(명령/로그/검증 JSON) 기록
  - `summary` 실제 카운트 및 검증 결과(`teams>0`, `matches>0`) 확정

2. Premier League 공식 사이트 파서 안정화
- 목적: 실제 운영 데이터 품질 확보
- DoD:
  - 공식 사이트 DOM 변화 대응 파서 보강
  - 파싱 실패 시 fallback/skip 정책 구체화 및 리포트 이슈 섹션 반영

### P1
1. Web E2E/핵심 사용자 플로우 테스트 추가
- DoD:
  - 홈 → 일정/결과 → 매치상세 이동 검증
  - 구단목록 → 구단상세 이동 검증

2. Web 성능/접근성 점검 (`Lighthouse` 기준 합의)
- DoD:
  - 목표 수치 정의
  - 개선 항목 backlog 반영

### P2
1. 웹 의존성 취약점 정리 계획
- DoD:
  - 취약점 영향 분석
  - 업그레이드/대체 패키지 계획 수립

## B-1) Execution Queue (Concrete)
1. `CRAWL-002` 완료 전환
- 실사이트 DNS/네트워크 접근 가능한 환경에서 `validate_pl_ingest.py` 재실행
- `docs/crawl-002-ingest-report.md` 상태를 `COMPLETED`로 전환
2. 브랜치 보호 최종 고정
- required checks에 `CI / web-e2e` 반영 확인
- `set_branch_protection.sh`로 `enforce_admins=true` 적용 확인
3. Lighthouse 실측 baseline 확보
- `/`, `/matches`, `/matches/[id]`, `/standings` 모바일/데스크탑 3회 측정
- 결과 JSON 아카이빙 + 기준치 충족/미충족 표시
4. Web 성능 개선 스프린트 실행
- `WEB-Q-001`, `WEB-Q-002` 우선 적용 후 재측정
- 이후 `WEB-Q-003`, `WEB-Q-004` 진행
5. 보안 취약점 정리 계획 수립
- `npm audit` 결과 영향도 분석
- 업그레이드/대체 패키지 계획 및 일정 확정
6. UI 리디자인 트랙 추가 (shadcn)
- `apps/web` UI 컴포넌트/스타일을 shadcn 기반으로 전환
- 홈/매치/구단 핵심 화면을 트렌디한 디자인으로 개편
7. 배포 트랙 추가 (Netlify)
- Netlify 배포 파이프라인 구성(Preview/Production)
- 환경변수/빌드 설정 및 도메인 연결 절차 문서화

## C) In Progress
- `P0-1`: Premier League 공식 사이트 기반 데이터소스(`pl`) 안정화 작업 진행중
  - table/header alias + JSON fallback + JS assignment/PULSE fallback 구현
  - dataset별 skip/abort 정책 운영값 정리
- `P0-1a`: 실사이트 DNS 접근 오류 해결 및 live validate 재실행 진행중
- `P0-1b`: CI runner live validate 실패 원인(teams 0건) 대응 파서/소스 전략 고도화 진행중
- `P1-2`: Web 성능 개선 `WEB-Q-001` 적용 진행중 (매치 상세 탭 lazy render + dynamic import)

## D) Done Log
- 2026-02-14
  - `CRAWL-002` CI live validate 실행: run `22007750599`, `22007850722`, `22007891760` 실패 원인 확인(`teams` 0건)
  - `CRAWL-002` teams fallback 보강: required 완화 + links 기반 fallback + 회귀 테스트 추가
  - `WEB-Q-002` 적용 완료: 홈(`/`) 데이터를 SSR prefetch(`getServerSideProps`)로 전환해 초기 로딩 상태 제거
  - `Lighthouse Baseline` CI 자동화 실행 확인: run `22007750602`, `22007793692` 성공
  - `Lighthouse Baseline` 자동화 추가: `apps/web/scripts/run-lighthouse-baseline.mjs`, `make web-lighthouse`
  - CI 워크플로 추가: `Crawler Live Validate`, `Lighthouse Baseline`
  - `CRAWL-002` 파서 보강: 스크립트 assignment/PULSE 계열 JSON fallback 추가
  - `CRAWL-002` 회귀 테스트 추가: `teams_pulse_assignment.html` 파싱 케이스
  - 브랜치 보호 스크립트 보정: required checks `CI / api`, `CI / web-e2e` 동시 반영
  - 원격 브랜치 보호 재적용 확인(`enforce_admins=true`, `strict=true`)
  - Web 성능개선 `WEB-Q-001` 1차 적용: `/matches/[id]` 탭 lazy render + dynamic import
- 2026-02-13
  - API MVP(`API-001`~`API-005`) 완료
  - OpenAPI 스냅샷/통합 테스트 CI 필수화
  - 브랜치 보호 적용 및 CI 통과 확인
  - Web 초기 라우트 및 UI/연동 구현
  - `web-lint`, `web-build`, `web-dev` 실행 검증 완료
  - `CRAWL-001` 초기 수집 파이프라인 구현 및 멱등 실행 확인
  - `BATCH-001`, `BATCH-002` 수동 runner 스켈레톤 상태 문서 반영
  - `BATCH-001`, `BATCH-002` GitHub Actions 스케줄러 연동 완료 (`Batch Scheduler`)
  - `BATCH-003` 재시도 정책 + Slack Webhook 실패 알림 연동 완료
  - `CRAWL-002` 1차 안정화: 다중 파싱 전략(table -> JSON fallback) 및 dataset fallback 정책 도입
  - `CRAWL-002` fixture(official-like html/json) 기반 테스트 확대
  - 운영 보강: PR-only/enforce_admins 및 시크릿 체크리스트 문서 반영

## E) Working Rules
1. 개발 시작 전
- 반드시 `NEXT_STEPS.md`를 읽고 `Primary Focus` 및 `P0/P1` 우선순위를 확인한다.
- 새 작업을 시작하면 필요 시 `In Progress`를 업데이트한다.

2. 개발 완료 후
- 반드시 `NEXT_STEPS.md`의 다음 항목을 갱신한다.
  - `A) Current Status`
  - `B) Next Priorities` (우선순위 재정렬)
  - `C) In Progress` (완료 처리)
  - `D) Done Log` (날짜/핵심 결과)

3. PR 체크
- PR 설명에 `NEXT_STEPS.md 반영 여부`를 명시한다.
- 문서 갱신이 필요한 변경인데 누락된 경우 머지하지 않는다.
