# CLAUDE.md — PromptGram

이 파일은 Claude Code가 이 프로젝트에서 작업할 때 반드시 따라야 하는 규칙이다.

---

## 답변 규칙 (Response Rules) — 최우선

이 프로젝트는 Claude Code Fable 5로 진행하며, **토큰 절약을 위해 자율 실행 모드**로 운영한다.

1. **작업 시작 전 `docs/기능명세서.md`와 이 `CLAUDE.md`를 먼저 읽는다.** 추측하지 말고 명세서를 기준으로 한다.
2. **설명 문장만 한국어. 기술 용어·파일명·경로·코드·명령어·라이브러리명은 영문 원문 그대로. 음차 금지.**
3. **자율 실행.** 승인을 매번 기다리지 말고, 아래 "기술 결정(Pre-decided)"과 명세서를 근거로 스스로 판단해 **해당 batch/phase 전체를 끝까지 진행**한다.
4. **되묻지 않는다.** 사용자 질문은 CLAUDE.md·명세서로 해결 불가능한 진짜 blocker(외부 계정/API key 필요, 상충하는 요구 등)일 때만. 사소한 선택은 표준적·보수적으로 알아서 정하고 진행한다.
5. **출력은 짧게 (토큰 절약).** 코드 전문을 채팅에 다시 붙여넣지 말 것 — 파일로만 작성. 요약은 몇 줄로. 장황한 설명·반복 금지. 관련 tool 호출은 묶어서 실행.
6. 각 milestone은 스스로 smoke test까지 하고 다음으로 넘어간다. **batch가 끝났을 때만** 한 것 요약(짧게) + smoke test 결과를 보고한다. 중간에 멈추는 건 스스로 못 고치는 hard failure일 때만.

---

## 프로젝트 개요

AI 프롬프트를 카드 형태로 아카이빙하고 태그로 모아보며 공유·발전시키는 소셜 피드 서비스.
시그니처 기능은 **변수 템플릿**(재사용 가능한 프롬프트)과 **AI 프롬프트 튜닝/태그 추천**.
상세 스펙은 `docs/기능명세서.md` 참조.

## 기술 결정 (Pre-decided Defaults) — 되묻지 말 것

아래는 확정 사항이다. 이 값으로 진행하고 사용자에게 확인하지 않는다.

- Python 3.12 / Node 20 LTS
- BE 패키지: **pip + venv + requirements.txt** (poetry·uv 쓰지 말 것)
- FE 패키지: npm
- **TailwindCSS는 v3로 고정** (v4 금지 — config 호환 이슈로 시간 낭비)
- FE 상태관리 Pinia, 라우팅 Vue Router
- ID: int autoincrement PK
- 비밀번호 hashing: passlib + bcrypt
- **JWT 저장 방식: refresh token = httpOnly + Secure + SameSite cookie / access token = 프론트 메모리(Pinia)**. CORS는 credentials 허용, 개발 origin은 env로 관리, refresh 엔드포인트는 cookie에서 읽음
- 프로필 이미지: MVP는 URL 문자열만 저장(파일 업로드 없음). 미설정 시 기본 avatar
- BE 테스트: pytest — 핵심 경로만 가볍게 (과설계 금지)
- seed script로 프롬프트 20개 이상 생성(피드·무한 스크롤 테스트용)
- 스키마 변경은 항상 Alembic migration
- milestone 단위로 의미 있는 commit message로 commit
- **랜딩 페이지 디자인 토큰**: 기본 배경 dark #0A0A0A, 포인트 #0070F3, 폰트 Pretendard(웹폰트 CDN)
- **랜딩 애니메이션 스택**: GSAP(카드 흐름·parallax·swipe light·zoom-in) + CSS(glassmorphism·glow) + Vue Router transition(페이지 전환). 무거운 3D/WebGL 쓰지 말 것
- **랜딩 성능**: 배경 카드 ~30개 상한, transform/opacity만 애니메이트, mousemove는 rAF throttle, `prefers-reduced-motion` 존중
- **CTA는 email/password auth로 연결** (MVP). Google 로그인 버튼은 Phase 3 전까지 만들지 말 것(죽은 버튼 금지)
- Frontend UI를 설계할때는 UI UX 관련 스킬을 사용한다.


## 기술 스택

| 영역 | 스택 |
| --- | --- |
| FE | Vue 3 (Composition API, `<script setup>`) + Vite + TailwindCSS |
| BE | FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 |
| DB | PostgreSQL |
| Auth | JWT (access + refresh 분리), 비밀번호 bcrypt/argon2 hashing |
| AI | LLM Provider 추상화 — local=Ollama, demo=Gemini 3 Flash |

## 디렉토리 구조 (monorepo)

```
promptgram/
├── CLAUDE.md
├── docs/
│   ├── 기능명세서.md
│   └── milestones.md
├── frontend/          # Vue 3 + Vite
└── backend/           # FastAPI
    ├── app/
    │   ├── main.py
    │   ├── core/      # config, security, db session
    │   ├── models/    # SQLAlchemy models
    │   ├── schemas/   # Pydantic schemas
    │   ├── api/       # routers
    │   ├── services/  # 비즈니스 로직 (AI provider 추상화 포함)
    │   └── crud/
    ├── alembic/
    └── tests/
```

## 코딩 컨벤션

- **BE**: async 우선. DB 세션은 async session. Router는 얇게, 로직은 `services/`·`crud/`로 분리.
- **Pydantic**: 입력 검증은 schema에서 엄격하게 (비밀번호 길이, prompt_text 글자 수 제한 등).
- **N+1 방지**: 관계 로딩은 `selectinload` 등 eager loading 명시.
- **Pagination**: 피드는 **cursor-based** (`(created_at, id)`). Offset 금지.
- **FE**: `PromptCard`는 feed/mypage/search에서 공통으로 쓰는 재사용 컴포넌트로 분리.
- **Secret**: 모든 key·비밀번호는 `.env` (env var)로만. 절대 커밋 금지. `.env.example` 유지.
- **Migration**: 스키마 변경은 반드시 Alembic migration으로.

## AI Provider 규칙

- `services/`에 `LLMProvider` 인터페이스(추상 base)를 두고 `GeminiProvider`, `OllamaProvider` 구현.
- 실제 provider는 env var(`LLM_PROVIDER=gemini|ollama`)로 선택.
- 모든 AI 호출: async / 응답 캐싱 / per-user rate limit / 429 exponential backoff.
- **Gemini 무료 티어 주의**: 무료 입력·출력은 학습에 쓰일 수 있으니 민감정보 금지. billing을 켜면 해당 GCP 프로젝트 무료 티어가 사라지므로 무료/유료 프로젝트 분리.

## 결과물 프레이밍

- AI 튜닝 결과는 "개선 **제안**"으로 표기 (정답 아님).
- 프롬프트는 사용자 생성 콘텐츠 — 부적절 콘텐츠/신고는 후순위(Phase 3) 고려.

---

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
