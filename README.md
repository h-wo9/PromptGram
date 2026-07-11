# PromptGram

AI 프롬프트를 카드로 아카이빙하고 태그로 모아보며 공유하는 소셜 피드 서비스.
시그니처 기능: **변수 템플릿** (`[변수명]` 재사용 프롬프트), AI 프롬프트 튜닝/태그 추천.

## Stack

- **FE**: Vue 3 (Composition API) + Vite + TailwindCSS v3 + Pinia + Vue Router + GSAP
- **BE**: FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 + Alembic
- **DB**: PostgreSQL (Docker)
- **Auth**: JWT (access = memory, refresh = httpOnly cookie)

## 실행 방법

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
