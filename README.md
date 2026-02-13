# EPL Information Hub

프리미어리그 경기/순위/선수 통계를 일배치로 수집해 제공하는 웹서비스입니다.

## Repository Layout
```text
apps/
  web/       # Next.js 프론트엔드
  api/       # FastAPI(NestJS 대체 가능) 백엔드
  crawler/   # 배치 크롤러/정합성 검증
packages/
  shared/    # 공통 타입/유틸
infra/       # Docker, 배포/인프라 설정
docs/        # 로드맵, 태스크 보드, 운영 문서
AGENTS.md    # 서비스/DB/화면/배치 요구사항
```

## Quick Start
현재 API MVP와 Web 초기 화면이 구현되어 있습니다.

```bash
make setup   # API 의존성 설치
make lint    # API lint (ruff)
make test    # API 테스트 (pytest)
make dev     # API 서버 실행 (uvicorn, :8000)
make web-setup  # Web 의존성 설치 (npm)
make web-dev    # Web 개발 서버 실행 (Next.js, :3000)
make crawler-ingest  # Crawler 샘플 수집/적재 실행
make crawler-summary # Crawler 적재 결과 카운트 확인
make crawler-daily   # BATCH-001 일배치 runner(수동)
make crawler-weekly  # BATCH-002 주배치 runner(수동)
```

## Batch Scheduler
- GitHub Actions `Batch Scheduler` 워크플로가 배치 자동 실행을 담당합니다.
- 스케줄:
  - 일배치: 매일 09:00 KST (`cron: 0 0 * * *`, UTC 기준)
  - 주배치: 매주 목요일 12:00 KST (`cron: 0 3 * * 4`, UTC 기준)
- 수동 실행:
  - Actions > `Batch Scheduler` > `Run workflow`에서 `all | daily | weekly` 선택

## MVP Scope
- 홈 대시보드
- 일정/결과 + 매치 상세(라인업/스탯/타임라인)
- 순위표
- 선수 통계
- 구단 목록/상세
- 크롤러 배치(매일 09:00, 매주 목 12:00)

## Delivery Plan
상세 일정과 이슈 단위 작업은 `docs/task-board.md`를 따릅니다.
API 이후 실행 계획은 `docs/next-development-plan.md`를 따릅니다.
실행 기준 문서는 `NEXT_STEPS.md`를 따릅니다.
CI 필수 체크 설정 가이드는 `docs/ci-required-checks.md`를 참고하세요.
공식 사이트 크롤링 POC 스펙은 `docs/premierleague-crawling-poc.md`를 참고하세요.

## NEXT_STEPS 운영 규칙
- 개발 시작 전: `NEXT_STEPS.md` 확인 (Primary Focus + P0/P1 우선순위)
- 개발 완료 후: `NEXT_STEPS.md` 업데이트 (Current Status, Next Priorities, Done Log)
- PR 작성 시: `NEXT_STEPS.md` 반영 여부를 명시

## Current Progress
- `OPS-001`, `OPS-002`, `OPS-003` 완료
- `DB-001`, `DB-002` 완료 (`apps/api/migrations/001_init_schema.sql`)
- `API-001` 완료 (`GET /matches`: 라운드/월/팀 필터 지원)
- `API-002` 완료 (`GET /matches/{id}`: 스코어/이벤트/스탯 조회)
- `API-003` 완료 (`GET /standings`)
- `API-004` 완료 (`GET /stats/top`)
- `API-005` 완료 (`GET /teams`, `GET /teams/{id}`)
- `WEB-001`~`WEB-004` 1차 화면/연동 구현 (`apps/web`)
- `WEB-005` 모바일 390px 대응 CSS 반영
- `CRAWL-001` 초기 수집 파이프라인(샘플 소스+업서트) 구현
- `CRAWL-002` 공식 사이트(`premierleague.com`) 기반 `pl` 데이터소스 POC 진행중
- `BATCH-001`, `BATCH-002` 스케줄러 연동 완료 (`Batch Scheduler`)

## Contribution Rules
- 브랜치: `feat/<scope>-<short-desc>`, `fix/<scope>-<short-desc>`
- 커밋: Conventional Commits (`feat:`, `fix:`, `chore:`)
- PR: 변경 요약, 테스트 결과, 스크린샷(프론트 변경 시) 필수
