# Next Development Plan (After API-005)

기준일: 2026-02-13

## Goal
- API MVP를 실제 서비스 화면과 배치 파이프라인으로 연결
- Milestone 4~5의 핵심 리스크(데이터 품질, 운영 자동화, 프론트 UX)를 먼저 해소

## Phase 1: API 안정화 (2~3일)
1. OpenAPI/테스트 마무리
- OpenAPI 스냅샷 테스트를 CI에 포함
- API-002~005 통합 테스트를 CI 기본 파이프라인에 포함

2. 계약 정리
- 주요 404/422 응답 예시 문서화
- `docs/api-db-operations.md`에 API 에러 코드 매핑 추가

완료 기준
- PR에서 OpenAPI 스냅샷 diff로 계약 변경 확인 가능
- API 회귀 테스트가 CI에서 자동 수행

## Phase 2: Crawler MVP (1주)
1. `CRAWL-001` 구현
- FBref 소스 파서(팀/선수/경기/기초 스탯)
- 멱등 업서트(`matches`, `match_stats`, `player_season_stats`, `standings`)

2. 스케줄러 연결
- 일배치 09:00, 주간 동기화 목 12:00 실행 스크립트
- 실패 재시도(최소 3회), 실패 알림(웹훅)

완료 기준
- 샘플 시즌 데이터 1회 적재 + 재실행 시 중복 없음
- 배치 실패 시 알림 확인 가능

## Phase 3: Web MVP 착수 (1~2주)
1. `WEB-001`, `WEB-002`
- 홈 대시보드 + 일정/결과 리스트/필터

2. `WEB-003` 우선
- 매치 상세(스코어/타임라인/스탯)부터 구현

완료 기준
- 모바일(390px)에서 홈/일정/상세 탐색 가능
- API 응답 지연/에러에 대한 로딩/에러 UI 처리

## Immediate Backlog (우선순위)
1. CI에 `pytest apps/api/tests/test_openapi_snapshot.py` 추가 검증
2. Crawler 앱 초기 구조 + `ingest_matches.py` 스켈레톤 생성
3. Web 앱 초기화(Next.js + TypeScript) 및 `/matches` 페이지부터 연결
