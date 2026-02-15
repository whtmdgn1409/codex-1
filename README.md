# EPL Information Hub

프리미어리그 경기/순위/선수 통계를 일배치로 수집해 제공하는 웹서비스입니다.

## Live Service
- Current Vercel URL: `https://codex-1-liard.vercel.app/`
- Custom Domain: 미연결 (도메인 확보 후 Vercel에 추가 예정)

## Repository Layout
```text
apps/
  web/       # Next.js 프론트엔드
  api/       # FastAPI 백엔드
  crawler/   # 배치 크롤러/검증 스크립트
packages/
  shared/    # 공통 타입/유틸(확장 예정)
infra/       # 배포/인프라 설정(확장 예정)
docs/        # 운영/로드맵/리포트 문서
AGENTS.md    # 서비스 요구사항 소스 문서
NEXT_STEPS.md # 실행 우선순위/진행현황 기준 문서
```

## Quick Start
```bash
make setup        # API 의존성 설치
make lint         # API lint
make test         # API 테스트
make dev          # API 서버 실행 (:8000)

make web-setup    # Web 의존성 설치
make web-dev      # Web 개발 서버 실행 (:3000)
make web-lint     # Web lint
make web-build    # Web production build
make web-e2e      # Playwright E2E

make crawler-setup    # Crawler 의존성 설치
make crawler-ingest   # Crawler 적재 실행
make crawler-summary  # 적재 결과 요약
make crawler-test     # Crawler 테스트
make crawler-daily    # 일배치 수동 실행
make crawler-weekly   # 주배치 수동 실행
```

## Current Progress
- API: `API-001`~`API-005` 완료, OpenAPI 스냅샷/통합 테스트 CI 필수화
- Web: MVP 라우트 + `WEB-Q-001`~`WEB-Q-004` 성능/접근성 개선 반영
- Crawler: `CRAWL-001` 완료, `CRAWL-002` 완료(CI live validate 성공)
- Batch: 일/주 스케줄 + 재시도 + Slack 알림 구축 완료
- CI: `CI / api`, `CI / web-e2e`, `Crawler Live Validate`, `Lighthouse Baseline` 운영

## Next Priorities
1. Vercel Git Integration 실배포 검증(Preview/Production)
2. 브랜치 보호/PR-only 정책 최종 고정 점검
3. shadcn UI 리디자인 2차(standings/stats/detail)
4. Lighthouse 회귀 관리 자동화(기준치/경보)
5. `npm audit` 취약점 정리 계획 수립

## Core Docs
- 실행 기준: `NEXT_STEPS.md`
- 크롤링 POC/정책: `docs/premierleague-crawling-poc.md`
- CRAWL-002 리포트: `docs/crawl-002-ingest-report.md`
- CI 필수 체크 가이드: `docs/ci-required-checks.md`
- 운영 설정/시크릿: `docs/operations-config.md`
- 배포 설정: Vercel Dashboard Git Integration (`apps/web`)

## Contribution Rules
- 브랜치: `feat/<scope>-<desc>`, `fix/<scope>-<desc>`
- 커밋: Conventional Commits (`feat:`, `fix:`, `chore:`)
- PR 필수: 변경 요약, 테스트 결과, 프론트 변경 시 스크린샷
- 문서 규칙: 기능/운영 변경 시 `NEXT_STEPS.md` 동기화 필수
