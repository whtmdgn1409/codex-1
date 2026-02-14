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

## Lighthouse 실행 계획 (Web Quality)
### 측정 범위/방법
- 측정 대상 라우트
  - `/` (Home)
  - `/matches`
  - `/matches/[id]` (대표 경기 1건)
  - `/standings`
- 측정 조건
  - 모바일: Lighthouse mobile preset
  - 데스크톱: Lighthouse desktop preset
  - 각 라우트별 3회 측정 후 중앙값 기준으로 판정
- 실행 커맨드(로컬 기준)
  - `npx lighthouse http://localhost:3000 --preset=desktop --output=json --output-path=.lighthouse/home-desktop.json`
  - `npx lighthouse http://localhost:3000 --output=json --output-path=.lighthouse/home-mobile.json`
  - 나머지 라우트도 동일 패턴으로 반복 측정

### 목표 점수 (합격 기준)
| 구분 | Mobile | Desktop |
| :--- | :---: | :---: |
| Performance | >= 70 | >= 90 |
| Accessibility | >= 95 | >= 95 |
| Best Practices | >= 95 | >= 95 |
| SEO | >= 95 | >= 95 |

### Core Web Vitals/성능 세부 목표
- Mobile (핵심 라우트 중앙값)
  - LCP <= 3.2s
  - INP <= 250ms
  - CLS <= 0.10
  - TBT <= 300ms
- Desktop (핵심 라우트 중앙값)
  - LCP <= 2.0s
  - INP <= 200ms
  - CLS <= 0.10
  - TBT <= 150ms

### 우선순위 백로그 (저성능 가능성 기반)
1. `WEB-Q-001` Match Detail(`/matches/[id]`) 초기 렌더 경량화 (P0)
- 리스크 가설: 타임라인/스탯/라인업 탭 데이터와 차트 코드가 초기 번들에 과다 포함될 가능성
- 실행 항목: 탭별 코드 스플리팅(dynamic import), 비가시 탭 lazy render, 차트 라이브러리 지연 로드
- 완료 기준: 해당 라우트 Mobile Performance +12p 이상 또는 TBT 120ms 이상 절감

2. `WEB-Q-002` Home(`/`) Hero/뉴스 섹션 이미지 최적화 (P0)
- 리스크 가설: 하이라이트 카드 이미지 및 상단 섹션이 LCP 후보를 악화
- 실행 항목: above-the-fold 이미지 우선순위 로딩, 크기 고정(width/height), WebP/AVIF 적용, 오프스크린 lazy
- 완료 기준: Home Mobile LCP <= 3.0s, Desktop LCP <= 1.8s

3. `WEB-Q-003` Matches(`/matches`) 리스트 렌더 비용 절감 (P1)
- 리스크 가설: 다수 경기 카드 동시 렌더로 스크립트 평가/레이아웃 비용 증가
- 실행 항목: 카드 리스트 단계적 렌더(초기 N개), 필터 변경 debounce, 불필요 re-render 제거
- 완료 기준: Mobile TBT <= 250ms, INP <= 250ms

4. `WEB-Q-004` Standings(`/standings`) 테이블 접근성/모바일 성능 보정 (P1)
- 리스크 가설: 가로 스크롤 테이블의 semantics 부족 및 style/layout shift 가능성
- 실행 항목: 테이블 헤더/caption/scope 정비, 고정 너비 규칙 명시, 스켈레톤 높이 고정
- 완료 기준: Accessibility >= 98, CLS <= 0.08

### 작업 순서 (2주)
- Week 1: `WEB-Q-001`, `WEB-Q-002` 완료 + 재측정
- Week 2: `WEB-Q-003`, `WEB-Q-004` 완료 + 회귀 측정/문서 업데이트
