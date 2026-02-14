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
현재 API MVP, Web 1차 구현, Crawler/Batch 운영 스캐폴드가 구현되어 있습니다.

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
운영 설정/시크릿 가이드는 `docs/operations-config.md`를 참고하세요.

## NEXT_STEPS 운영 규칙
- 개발 시작 전: `NEXT_STEPS.md` 확인 (Primary Focus + P0/P1 우선순위)
- 개발 완료 후: `NEXT_STEPS.md` 업데이트 (Current Status, Next Priorities, Done Log)
- PR 작성 시: `NEXT_STEPS.md` 반영 여부를 명시

## Current Progress
- Infra/CI
  - `OPS-001`~`OPS-003` 완료
  - `CI / api` 필수 체크, `Batch Scheduler`(일/주 cron + 수동 실행) 적용 완료
- API
  - `API-001`~`API-005` 완료
  - OpenAPI 스냅샷 + API 통합 테스트(`API-002`~`API-005`) CI 필수화
- Web
  - `WEB-001`~`WEB-005` 완료 (핵심 라우트 + 모바일 390px 대응)
  - `make web-lint`, `make web-build` 통과
  - Playwright E2E 핵심 플로우 2건 추가 및 로컬 실행 검증 완료
- Crawler/Batch
  - `CRAWL-001` 완료 (샘플 소스 멱등 업서트)
  - `CRAWL-002` 진행중 (공식 사이트 `pl` 파서: table alias + JSON fallback + dataset 정책)
  - `BATCH-001`, `BATCH-002` 완료 (스케줄러 연동)
  - `BATCH-003` 완료 (재시도 + Slack 실패 알림)

## Next Development Plan (Concrete)
아래 순서대로 구현을 진행합니다.

1. `CRAWL-002` 마무리: 공식 사이트 실데이터 적재 안정화
- 작업:
  - 실제 페이지 샘플(팀/경기/스탯) fixture 추가
  - 파서 필드 매핑 정확도 보강(누락/형식 변환 케이스)
  - `teams/matches`는 실패 시 `abort`, `players/match_stats`는 `skip` 정책 검증
- DoD:
  - `make crawler-test` 통과
  - `CRAWLER_DATA_SOURCE=pl` 기준 ingest 결과 리포트 문서화

2. Web 품질 고도화 1단계: 핵심 사용자 플로우 E2E
- 작업:
  - 홈 -> 일정/결과 -> 매치상세
  - 구단목록 -> 구단상세
- DoD:
  - CI에서 E2E 통과(최소 핵심 2플로우)

3. Web 품질 고도화 2단계: 성능/접근성 기준 수립
- 작업:
  - Lighthouse 기준치 정의(모바일/데스크탑)
  - 저점 페이지 우선 개선 항목 backlog 등록
- DoD:
  - 목표치와 측정 방법 문서화

4. 운영 안정화
- 작업:
  - `main` PR-only 운영 강제 재점검
  - 배치/알림 시크릿 운영 체크리스트 점검
- DoD:
  - `docs/operations-config.md` 기준 설정 완료 확인

## Contribution Rules
- 브랜치: `feat/<scope>-<short-desc>`, `fix/<scope>-<short-desc>`
- 커밋: Conventional Commits (`feat:`, `fix:`, `chore:`)
- PR: 변경 요약, 테스트 결과, 스크린샷(프론트 변경 시) 필수
