# Web Service

Next.js + TypeScript 기반 프론트엔드입니다.

## Run
```bash
make web-setup
make web-dev
```

## Build & Lint
```bash
make web-build
make web-lint
```

## Routes
- `/` 홈 대시보드
- `/matches` 일정/결과
- `/matches/[id]` 매치 상세
- `/standings` 순위표
- `/stats` 선수 통계
- `/teams` 구단 목록
- `/teams/[id]` 구단 상세

## Env
`apps/web/.env.example`을 참고해 아래 값을 설정하세요.

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
