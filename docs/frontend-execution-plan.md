# Frontend Execution Plan (Subagent-driven)

기준일: 2026-02-13

## 목표
- `apps/web`에 Next.js + TypeScript 기반 프론트엔드 MVP를 구축한다.
- 기존 API (`/matches`, `/matches/{id}`, `/standings`, `/stats/top`, `/teams`, `/teams/{id}`)와 연결한다.
- AGENTS.md의 IA/GNB/핵심 UX를 우선 구현한다.

## 개발 순서
1. 스캐폴드/공통 레이어
- Next.js(페이지 라우터) 기본 구조 생성
- 공통 레이아웃(GNB), API 클라이언트, 타입 정의, 공통 스타일 토큰 구성

2. MVP 화면
- `/` 홈: 하이라이트 카드 + 미니 순위표 + Top 득점
- `/matches`: 라운드/월/팀 필터 + 경기 카드 리스트
- `/matches/[id]`: 스코어보드 + 이벤트 타임라인 + 팀별 스탯

3. 확장 화면
- `/standings`: 리그 순위표 (권역 색상)
- `/stats`: 카테고리 탭(득점/도움/공격포인트/클린시트)
- `/teams`, `/teams/[id]`: 팀 목록 및 상세(최근 폼/스쿼드)

## API 매핑
- 홈: `GET /matches`, `GET /standings`, `GET /stats/top?category=goals`
- 일정/결과: `GET /matches`
- 매치 상세: `GET /matches/{match_id}`
- 순위표: `GET /standings`
- 선수 통계: `GET /stats/top`
- 구단: `GET /teams`, `GET /teams/{team_id}`

## Subagent 전략
- Explorer subagent: 코드베이스/요구사항 분석, 데이터 계약 검토
- Worker subagent (구현):
  - 소유 범위: `apps/web/**`, 관련 문서(`docs/*frontend*`, `README.md` 일부)
  - 원칙: 다른 변경과 충돌 시 해당 변경은 건드리지 않고 자신의 파일 범위만 수정

## 완료 기준 (MVP)
- 모바일(390px) 포함 반응형 동작
- API 에러/로딩 상태 표시
- GNB 기준 페이지 라우팅 완성
- CI 대상 변경 시 웹 빌드/린트 명령 추가 준비
