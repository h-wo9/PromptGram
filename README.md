# PromptGram

AI 프롬프트를 카드로 아카이빙하고 태그로 모아보며 공유하는 소셜 피드 서비스.
시그니처 기능: **변수 템플릿** (`[변수명]` 재사용 프롬프트), AI 프롬프트 튜닝/태그 추천.

## Stack

- **FE**: Vue 3 (Composition API) + Vite + TailwindCSS v3 + Pinia + Vue Router + GSAP
- **BE**: FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 + Alembic
- **DB**: PostgreSQL (Docker)
- **Auth**: JWT — access(30분) = 프론트 메모리(Pinia) / refresh(14일) = localStorage + refresh rotation (`refresh_tokens` 테이블에 hash 저장, 재사용 시 401)
  > 트레이드오프: 무료 cross-domain 호스팅(FE/BE 서브도메인 분리)에서는 httpOnly third-party cookie가 차단되므로 localStorage + 짧은 access + refresh rotation 채택. 커스텀 도메인 시 httpOnly cookie로 전환 가능.

## 실행 방법

### 빠른 실행

```bash
docker compose up -d   # DB
./dev.sh               # backend + frontend 동시 실행 (Ctrl+C로 종료)
```


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
