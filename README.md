# PromptGram

AI 프롬프트를 카드로 아카이빙하고 태그로 모아보며 공유·발전시키는 소셜 피드 서비스.
시그니처 기능: **변수 템플릿** (`[변수명]` 재사용 프롬프트), **AI 프롬프트 튜닝/태그 추천**.

## 주요 기능

### 프롬프트 아카이브 (핵심)
- **프롬프트 CRUD** — 제목·본문·AI 응답·대상 모델(ChatGPT/Claude/Gemini)·해시태그·공개/비공개. 수정·삭제는 작성자만
- **변수 템플릿 (시그니처)** — 본문에 `[변수명]`을 쓰면 자동 감지·저장. 사용할 땐 변수별 입력창에 값을 채워 치환된 완성 프롬프트를 복사
- **원클릭 복사** — Clipboard API 복사 + 복사 횟수 집계(계정당 1회만 카운트, 복사는 무제한)
- **카드 이미지 다운로드** — 프롬프트를 브랜드 카드 PNG로 캡처(html2canvas)해 SNS 공유

### 피드 & 탐색
- **Masonry 피드 + 무한 스크롤** — cursor 기반 페이지네이션(offset 미사용)으로 중복/누락 없음
- **정렬** — 최신순 ↔ 인기순(좋아요) 토글
- **검색** — `#태그` 필터 + 키워드 검색(제목·본문, PostgreSQL `pg_trgm` 트라이그램 GIN 인덱스 — 한국어 친화)
- **상세 카드** — 카드를 누르면 원래 위치에서 확대(FLIP)되는 상세 모달: 전체 본문, 업로드 날짜, AI 응답, 댓글. 긴 프롬프트는 피드에서 6줄 clamp + '자세히 보기'

### 소셜
- **좋아요 / 스크랩** — 낙관적 업데이트(즉시 반영, 실패 시 롤백), 중복 방지
- **댓글** — 작성·인라인 수정("(수정됨)" 표시)·삭제, 상대 시간 표기
- **공개 프로필** (`/users/:id`) — 프로필 사진·닉네임·한 줄 소개 + 그 유저의 공개 프롬프트. 상세 카드의 게시자/댓글 작성자 클릭으로 진입
- **팔로우** — 팔로우/언팔로우 토글, 팔로워·팔로잉 수와 목록(모달)
- **알림** — ① 누가 나를 팔로우 ② 팔로잉의 새 공개 프롬프트 ③ 내 글에 댓글. 마이페이지 종 아이콘 + 안 읽음 빨간 점, 클릭 시 해당 프로필/프롬프트로 이동

### AI (Gemini 3 Flash)
- **프롬프트 튜닝** — 초안을 넣으면 더 구체적인 개선안 + **개선 이유**를 함께 반환 (결과는 '제안'으로 표기)
- **자동 태그 추천** — 본문 분석 후 태그 3~5개 추천, chip으로 선택
- `LLMProvider` 추상화 뒤 단일 GeminiProvider — 응답 캐싱, per-user rate limit, 429 exponential backoff

### 계정 & 개인화
- 이메일/비밀번호 회원가입·로그인 (bcrypt), JWT access+refresh rotation
- **마이페이지 3탭** — 내 프롬프트(공개) / 스크랩 / **나만 보기**(비공개 전용) + 프로필 수정, 팔로워·팔로잉
- **라이트/다크 테마** — feed·마이페이지에서 토글(랜딩·로그인은 다크 고정), localStorage 유지

### 랜딩 & UX
- **인터랙티브 랜딩** — 프롬프트 은하수, 스크롤 여정(GSAP ScrollTrigger): 변수 템플릿→AI 다듬기 pinned 전환, 타이핑 데모, 검색 필터 데모, **팔로우 모션그래픽**(프로필 줌인→팔로워 카운트업→알림 도착), ghost 타이포그래피. `prefers-reduced-motion` 존중
- 전역 toast·confirm 모달, skeleton 로딩, 피드 스크롤 위치 복원, 작성 중 이탈 경고, Cmd+Enter 제출, 글자 수 카운터

## Stack

- **FE**: Vue 3 (Composition API) + Vite + TailwindCSS v3 + Pinia + Vue Router + GSAP
- **BE**: FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 + Alembic
- **DB**: PostgreSQL (Docker)
- **AI**: Gemini 3 Flash (`LLMProvider` 인터페이스 뒤 단일 provider — 향후 OpenAI 등 교체 가능)
- **Auth**: JWT — access(30분) = 프론트 메모리(Pinia) / refresh(14일) = localStorage + refresh rotation (`refresh_tokens` 테이블에 hash 저장, 재사용 시 401)
  > 트레이드오프: 무료 cross-domain 호스팅(FE/BE 서브도메인 분리)에서는 httpOnly third-party cookie가 차단되므로 localStorage + 짧은 access + refresh rotation 채택. 커스텀 도메인 시 httpOnly cookie로 전환 가능.

## 기술 하이라이트

- **Cursor 기반 무한 스크롤** — `(created_at, id)` / `(like_count, id)` 복합 커서로 새 글 유입 시에도 중복·누락 없음
- **N+1 방지** — 태그·작성자·댓글 작성자 `selectinload` eager loading, 상호작용 여부는 페이지 단위 일괄 조회
- **비정규화 & 인덱스** — `like_count`/`bookmark_count`/`copy_count` 카운터 컬럼 + 목적별 인덱스(cursor·인기순·태그·트라이그램)
- **한국어 검색** — tsvector는 조사 등 형태소 문제로 부적합 → `pg_trgm` GIN 인덱스로 ILIKE 부분 검색 가속
- **낙관적 UI** — 좋아요/스크랩 즉시 반영 후 서버 동기화, 실패 시 롤백
- **AI 비용 관리** — 동일 입력 응답 캐싱, 사용자별 rate limit(60초 5회), 429 backoff, 60s timeout
- **모든 스키마 변경은 Alembic migration**, 핵심 경로 pytest + Playwright E2E로 검증

## 실행 방법

### 빠른 실행

```bash
docker compose up -d   # DB
./dev.sh               # backend + frontend 동시 실행 (Ctrl+C로 종료)
```

데모 계정: `demo@promptgram.dev` / `demo1234` (seed 실행 시)

### 1. Database (PostgreSQL)

```bash
docker compose up -d
```

호스트 포트는 `55432`를 사용한다 (로컬 native PostgreSQL 5432와 충돌 회피).

### 2. Backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 필요 시 값 수정
alembic upgrade head        # migration 적용
python -m app.seed          # (선택) 데모 데이터 시딩
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000 (docs: `/docs`)
- AI 기능(`/ai/*`)은 `.env`의 `GEMINI_API_KEY` 필요

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173

### 테스트

```bash
cd backend && .venv/bin/pytest
```

## 배포 (Vercel + Render + Supabase)

### DB — Supabase
- 프로젝트 생성 후 **Session pooler** 연결 문자열 사용 (포트 5432 — Transaction pooler 6543보다 호환성 좋음)
- URL 끝에 `?sslmode=require` 유지. `postgres://`·`postgresql://` 스킴은 서버가 자동으로 asyncpg 스킴으로 변환함
- 초기 스키마: 로컬에서 `DATABASE_URL=<supabase-url> .venv/bin/alembic upgrade head`
- (선택) 데모 데이터: `DATABASE_URL=<supabase-url> .venv/bin/python -m app.seed`

### Backend — Render (Web Service)
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`
- 환경변수:
  - `DATABASE_URL` — Supabase Session pooler URL (`?sslmode=require`)
  - `JWT_SECRET_KEY` — `openssl rand -hex 32` 등으로 생성한 랜덤 값
  - `CORS_ORIGINS` — Vercel 프론트 URL (예: `https://promptgram.vercel.app`)
  - `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3-flash-preview`
- Python 버전은 `backend/.python-version`(3.12)을 자동 인식

### Frontend — Vercel
- Root Directory: `frontend` (Vite 프리셋 자동 인식)
- 환경변수: `VITE_API_BASE_URL` — Render backend URL (예: `https://promptgram-api.onrender.com`)
- SPA 라우팅 rewrite는 `frontend/vercel.json`에 포함되어 있음
- 배포 후 Render의 `CORS_ORIGINS`를 실제 Vercel 도메인으로 맞출 것

> 참고: Render 무료 플랜은 유휴 시 슬립 → 첫 요청이 수십 초 걸릴 수 있음. Gemini 무료 티어는 입력·출력이 학습에 사용될 수 있으니 데모 안내 권장.
