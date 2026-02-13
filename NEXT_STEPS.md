# NEXT STEPS

Last Updated: 2026-02-13
Primary Focus: Crawler MVP + Web 품질 고도화 + 운영 안정화

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

### Crawler/Batch
- 미완료: `CRAWL-001`, `BATCH-001`~`BATCH-003`

### Known Issues / Risks
- `apps/web` 의존성에서 보안 취약점 경고 존재 (`npm audit` 기준 4건)
- 현재 `main` 브랜치에 관리자 우회 푸시가 가능했던 이력 존재 (PR-only 운영 고정 필요)

## B) Next Priorities

### P0
1. `CRAWL-001` 초기 수집 파이프라인 구현
- 목적: 실제 데이터 적재 루프 확보
- DoD:
  - 팀/선수/경기/기초 스탯 1회 적재 성공
  - 재실행 시 중복 없는 업서트 보장

2. 배치 실행 스켈레톤 (`BATCH-001`, `BATCH-002`)
- 목적: 수동 실행이 아닌 스케줄 기반 운영 준비
- DoD:
  - 일배치/주배치 진입 스크립트 분리
  - 실패 시 비정상 종료 코드 및 로그 표준화

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
- 없음

## D) Done Log
- 2026-02-13
  - API MVP(`API-001`~`API-005`) 완료
  - OpenAPI 스냅샷/통합 테스트 CI 필수화
  - 브랜치 보호 적용 및 CI 통과 확인
  - Web 초기 라우트 및 UI/연동 구현
  - `web-lint`, `web-build`, `web-dev` 실행 검증 완료

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
