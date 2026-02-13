# ⚽ EPL Information Hub (프리미어리그 비공식 데이터 웹사이트)

프리미어리그 공식 사이트 및 오픈 통계 사이트(FBref 등)의 데이터를 일 단위(Daily)로 수집하여, 축구 팬들에게 직관적인 경기 결과, 순위표, 선수 통계를 제공하는 웹 서비스입니다. 

---

## 📑 Table of Contents
1. [Database Schema (MySQL)](#1-database-schema-mysql)
2. [Wireframe & Page Flow](#2-wireframe--page-flow)
3. [Data Update Policy](#3-data-update-policy)

---

## 1. Database Schema (MySQL)

축구 데이터의 특성상 명확한 관계성(구단-선수-경기)을 가지므로 관계형 데이터베이스(RDBMS)로 설계되었습니다.

### 📌 ERD 요약 구조
* **`teams`** (구단 정보) 1 : N **`players`** (선수 정보)
* **`teams`** 1 : N **`matches`** (홈팀/원정팀 경기 일정)
* **`matches`** 1 : N **`match_events`** (득점, 카드 등 경기 이벤트)
* **`matches`** 1 : 1 **`match_stats`** (점유율, 슈팅 등 경기 통계)

### 📊 상세 테이블 명세서

#### 1) `teams` (구단 테이블)
| Column Name | Data Type | PK/FK | Description |
| :--- | :--- | :---: | :--- |
| `team_id` | INT | PK | 구단 고유 ID (Auto Increment) |
| `name` | VARCHAR(50) | | 구단 풀네임 (예: Arsenal FC) |
| `short_name` | VARCHAR(10) | | 구단 약어 (예: ARS) |
| `logo_url` | VARCHAR(255)| | 구단 로고 이미지 URL |
| `stadium` | VARCHAR(100)| | 홈 구장 이름 |
| `manager` | VARCHAR(50) | | 현 감독 이름 |

#### 2) `players` (선수 테이블)
| Column Name | Data Type | PK/FK | Description |
| :--- | :--- | :---: | :--- |
| `player_id` | INT | PK | 선수 고유 ID |
| `team_id` | INT | FK | 소속 구단 ID (`teams.team_id`) |
| `name` | VARCHAR(50) | | 선수 이름 |
| `position` | VARCHAR(10) | | 포지션 (FW, MF, DF, GK) |
| `jersey_num`| INT | | 등번호 |
| `nationality`| VARCHAR(50) | | 국적 |
| `photo_url` | VARCHAR(255)| | 선수 프로필 이미지 URL |

#### 3) `matches` (경기 일정 및 결과 테이블)
| Column Name | Data Type | PK/FK | Description |
| :--- | :--- | :---: | :--- |
| `match_id` | INT | PK | 경기 고유 ID |
| `round` | INT | | 라운드 (1 ~ 38) |
| `match_date`| DATETIME | | 경기 날짜 및 시간 |
| `home_team_id`| INT | FK | 홈팀 ID (`teams.team_id`) |
| `away_team_id`| INT | FK | 원정팀 ID (`teams.team_id`) |
| `home_score`| INT | | 홈팀 득점 (경기 전엔 NULL) |
| `away_score`| INT | | 원정팀 득점 (경기 전엔 NULL) |
| `status` | VARCHAR(20) | | 상태 (SCHEDULED, FINISHED) |

#### 4) `match_stats` (경기별 상세 스탯)
*크롤러가 경기 종료 후 1회만 수집하여 저장*

| Column Name | Data Type | PK/FK | Description |
| :--- | :--- | :---: | :--- |
| `stat_id` | INT | PK | 스탯 고유 ID |
| `match_id` | INT | FK | 경기 ID (`matches.match_id`) |
| `team_id` | INT | FK | 구단 ID (`teams.team_id`) |
| `possession`| DECIMAL(5,2)| | 점유율 (%) |
| `shots` | INT | | 총 슈팅 수 |
| `shots_on_target`| INT | | 유효 슈팅 수 |
| `fouls` | INT | | 파울 횟수 |
| `corners` | INT | | 코너킥 횟수 |

#### 5) `standings` (리그 순위표 캐싱 테이블)
*매 경기 종료 후 업데이트 배치 스크립트 실행으로 갱신*

| Column Name | Data Type | PK/FK | Description |
| :--- | :--- | :---: | :--- |
| `team_id` | INT | PK/FK | 구단 ID (`teams.team_id`) |
| `rank` | INT | | 현재 순위 |
| `played` | INT | | 경기 수 |
| `won` | INT | | 승리 |
| `drawn` | INT | | 무승부 |
| `lost` | INT | | 패배 |
| `goals_for` | INT | | 득점 (GF) |
| `goals_against`| INT | | 실점 (GA) |
| `goal_diff` | INT | | 골득실 (GD) |
| `points` | INT | | 승점 |

---

## 2. Wireframe & Page Flow

전체 웹사이트는 크게 5개의 메인 탭(GNB)으로 구성됩니다. 사용자 경험(UX)을 고려하여 복잡한 조작 없이 직관적으로 데이터를 볼 수 있도록 설계했습니다.

### 🗺️ GNB (Global Navigation Bar)
`[로고] | 🏠 홈 | 📅 일정/결과 | 🏆 순위표 | 📊 통계 | 🛡️ 구단 | 🔍 검색`

### 📱 페이지별 화면 레이아웃 (Layout)

#### 1. Home (메인 대시보드)
* **Hero Section (상단 메인):**
  * `진행 완료` 지난 라운드 주요 경기 스코어 하이라이트 (좌우 슬라이드)
  * `예정` 다가오는 빅 매치 카운트다운 및 중계 채널 정보
* **Main Content (좌측):** 최신 프리미어리그 관련 뉴스 헤드라인 리스트
* **Sidebar (우측):** * 미니 리그 순위표 (1위~5위, 18위~20위 강등권 노출)
  * 득점/도움 순위 Top 3 프로필

#### 2. Matches (일정 및 결과 페이지)
* **Filter Bar:** 라운드별(1R~38R) / 월별(8월~5월) / 팀별 필터 드롭다운
* **Match List:** * 날짜별 그룹핑 박스
  * `[시간] 홈팀 로고 (스코어) vs (스코어) 원정팀 로고` 형태의 카드 리스트
  * 종료된 경기는 클릭 시 **[Match Detail]** 페이지로 이동

#### 3. Match Detail (매치 리포트 페이지) - *경기 클릭 시 진입*
* **Header:** 대형 전광판 형태의 최종 스코어 및 득점자 목록 (예: ⚽ 24' Saka, ⚽ 89' Son)
* **Content Tabs:**
  * **Tab 1 [라인업]:** 축구장 그래픽 위 11명 선발 명단 및 포메이션 배치도, 벤치 멤버 목록.
  * **Tab 2 [매치 스탯]:** 점유율, 슈팅, 패스 성공률 등을 홈/원정 비교 막대 그래프(Bar Chart)로 시각화.
  * **Tab 3 [타임라인]:** 시간순으로 골, 교체, 옐로/레드카드 이벤트를 수직선 위에 아이콘으로 표시.

#### 4. Standings (리그 전체 순위표)
* **Table View:** 1위부터 20위까지 전체 순위 표출.
* **UX 포인트:**
  * 1~4위 (챔피언스리그 진출권): 행 배경색 옅은 파란색 강조
  * 5위 (유로파리그 진출권): 행 배경색 옅은 주황색 강조
  * 18~20위 (강등권): 행 배경색 옅은 빨간색 강조
  * 모바일 환경에서는 화면을 좁게 쓰고, 좌우 스와이프(Scroll)로 상세 스탯(GF, GA, GD)을 확인하도록 구성.

#### 5. Stats (선수 통계 페이지)
* **Category Tabs:** [득점 순위] | [도움 순위] | [공격포인트] | [클린시트(골키퍼)]
* **List:** 순위, 선수 사진, 이름, 소속팀 로고, 기록 수치. 1~3위는 프로필 사진을 크게 노출하여 시각적 만족도 제공.

#### 6. Teams (구단 프로필 페이지)
* **Grid View:** 20개 구단의 엠블럼을 바둑판식으로 배열 (클릭 시 상세 페이지 이동)
* **Team Detail (상세):**
  * 구단 헤더 (엠블럼, 창단 연도, 홈 구장 이미지, 감독)
  * 최근 5경기 폼 (예: 🟢 승 - 🔴 패 - ⚪ 무 - 🟢 승 - 🟢 승)
  * 시즌 스쿼드 리스트 (포지션별 그룹화)

---

## 3. Data Update Policy (크롤링 및 배치 작업 기준)
본 프로젝트는 실시간 API를 사용하지 않고 배치(Batch) 스크립트를 통한 정기 업데이트를 원칙으로 합니다.

* **매일 09:00 AM (경기 다음 날 아침):** * 전날 밤~새벽 진행된 경기의 **최종 스코어, 득점자, 매치 스탯** 크롤링 및 DB 저장 (`matches`, `match_stats` 업데이트)
  * **순위표 (`standings`)** 및 **선수 개인 스탯 (`players`)** 재계산 및 업데이트
* **매주 목요일 12:00 PM:**
  * 다가오는 주말 라운드의 **경기 일정 및 변경 사항** 확인 및 업데이트
* **크롤링 타겟:** FBref.com 데이터 테이블 (Pandas `read_html` 활용 권장) 및 공식 홈페이지 스쿼드 리스트.