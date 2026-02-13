# NEXT STEPS

Last Updated: 2026-02-13
Primary Focus: Crawler 실데이터 확장 + Web 품질 고도화 + 운영 안정화

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

### Infra/CI
- 완료: `CI / api` 워크플로 구성
- 완료: 브랜치 보호 규칙에 `CI / api` 필수 체크 적용
- 완료: `Batch Scheduler` 워크플로 추가 (일/주 배치 cron + 수동 실행)

### Crawler/Batch
- 완료: `CRAWL-001` 초기 수집 파이프라인(샘플 소스 + 멱등 업서트)
- 완료: `BATCH-001` 일배치 스케줄러 연동 (`make crawler-daily`, 매일 09:00 KST)
- 완료: `BATCH-002` 주배치 스케줄러 연동 (`make crawler-weekly`, 매주 목 12:00 KST)
- 완료: `BATCH-003` 실패 재시도/Slack 알림 연동 (`BATCH_RETRY_*`, `BATCH_ALERT_SLACK_WEBHOOK`)

### Known Issues / Risks
- `apps/web` 의존성에서 보안 취약점 경고 존재 (`npm audit` 기준 4건)
- 현재 `main` 브랜치에 관리자 우회 푸시가 가능했던 이력 존재 (PR-only 운영 고정 필요)

## B) Next Priorities

### P0
1. Crawler 소스 확장 (Premier League 공식 사이트 파서 도입)
- 목적: 샘플 데이터가 아닌 실제 시즌 데이터 적재
- DoD:
  - 공식 사이트 데이터 파싱(팀/경기/핵심 스탯) 구현
  - 파싱 실패 케이스 로깅 및 재시도 전략 정의

2. Premier League 공식 사이트 파서 안정화
- 목적: 실제 운영 데이터 품질 확보
- DoD:
  - 공식 사이트 DOM 변화 대응 파서 보강
  - 파싱 실패 시 fallback/skip 정책 구체화

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

## C) In Progress
- `P0-1`: Premier League 공식 사이트 기반 데이터소스(`pl`) 안정화 작업 진행중

## D) Done Log
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
