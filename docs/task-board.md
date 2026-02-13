# Task Board (Issue-based)

기준 문서: `AGENTS.md`

## Milestone 1: Foundation (Week 1)
- [x] `OPS-001` 모노레포 기본 설정 (`apps/`, `packages/`, `infra/`)
- [x] `OPS-002` 공통 환경변수 템플릿 작성 (`.env.example`)
- [x] `OPS-003` CI 파이프라인 초안 (lint/test 실행)
- [x] `DOC-001` API/DB 운영 원칙 문서화

DoD
- [ ] `make setup/lint/test/dev`가 실패 없이 동작
- [ ] 신규 기여자가 README만 보고 로컬 실행 가능

## Milestone 2: Data Layer (Week 2)
- [x] `DB-001` MySQL 스키마 마이그레이션 작성 (`teams`, `players`, `matches`, `match_stats`, `standings`)
- [x] `DB-002` 인덱스/제약조건/업서트 전략 확정
- [ ] `CRAWL-001` 팀/선수/일정 초기 수집 파이프라인

DoD
- [ ] 20개 팀/선수/일정 데이터 1회 적재 완료
- [ ] 중복 실행 시 데이터 중복 없음(idempotent)

## Milestone 3: API MVP (Week 3)
- [x] `API-001` `GET /matches` (라운드/월/팀 필터)
- [x] `API-002` `GET /matches/{id}` (스코어/이벤트/스탯)
- [x] `API-003` `GET /standings`
- [x] `API-004` `GET /stats/top`
- [x] `API-005` `GET /teams`, `GET /teams/{id}`

DoD
- [ ] OpenAPI 문서 생성
- [ ] 핵심 API 계약 테스트 통과

## Milestone 4: Web MVP (Week 4-5)
- [x] `WEB-001` GNB + 홈 대시보드
- [x] `WEB-002` 일정/결과 리스트 + 필터
- [x] `WEB-003` 매치 상세(라인업/스탯/타임라인 탭)
- [x] `WEB-004` 순위표/선수통계/구단 화면
- [x] `WEB-005` 모바일 반응형(우선 390px)

DoD
- [ ] 주요 플로우 E2E 통과
- [ ] Lighthouse 성능/접근성 기준 합의치 달성

## Milestone 5: Batch & Ops (Week 6-8)
- [ ] `BATCH-001` 일배치(매일 09:00) 스케줄러
- [ ] `BATCH-002` 주간 일정 동기화(목 12:00)
- [ ] `BATCH-003` 실패 재시도/알림(Slack 또는 이메일)
- [ ] `OPS-004` 모니터링/로그 대시보드
- [ ] `REL-001` 스테이징/운영 배포

DoD
- [ ] 배치 성공률 99%+
- [ ] API p95 300ms 이하
- [ ] 장애 대응 런북 문서화

## Working Agreement
- 이슈 라벨: `backend`, `frontend`, `crawler`, `infra`, `docs`, `priority:*`
- 우선순위: `P0 > P1 > P2`
- 브랜치 규칙: `feat/<issue-id>-<slug>`, `fix/<issue-id>-<slug>`
- 상태 기준 문서: `NEXT_STEPS.md` (작업 시작 전 확인, 완료 후 갱신)
