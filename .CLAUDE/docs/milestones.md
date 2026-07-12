# milestones.md — PromptGram (자율 실행용)

Fable 5 토큰 절약을 위해 **왕복을 최소화**한다. 아래 batch를 하나씩 붙여넣으면,
Claude Code가 그 batch 안의 모든 milestone을 **끝까지 자율 실행**하고 batch 끝에서만 짧게 보고한다.
전체 프로젝트는 사용자 turn **2번(BATCH A → BATCH B)** 으로 완주하는 것이 목표다.

공통 전제(모든 batch에 적용):
- 시작 시 `CLAUDE.md`와 `docs/기능명세서.md`를 먼저 읽는다.
- CLAUDE.md의 "기술 결정(Pre-decided)"과 명세서를 근거로 스스로 결정. 사소한 선택으로 되묻지 않는다.
- 각 milestone은 스스로 smoke test 후 다음으로 진행. commit은 milestone 단위.
- 채팅 출력은 짧게. 코드 전문 재출력 금지.
- hard failure(스스로 못 고침)일 때만 멈추고 최소한으로 질문.

---

## BATCH A — Phase 0 + Phase 1 (MVP 전체를 한 번에)

```
CLAUDE.md와 docs/기능명세서.md를 먼저 읽어라. 그다음 아래 M0~M5를 순서대로 자율 실행하라.
각 단계는 스스로 smoke test하고 commit한 뒤 다음으로 넘어가라. 사소한 선택은 CLAUDE.md의
기술 결정을 따르고 되묻지 마라. 전부 끝나면 짧게 요약과 smoke test 결과만 보고하라.

M0. Scaffold: CLAUDE.md 디렉토리 구조대로 monorepo. backend(FastAPI + SQLAlchemy 2.0 async
    + Pydantic v2, /health, .env.example), frontend(Vue3+Vite+Tailwind v3+Pinia+Vue Router),
    docker-compose로 PostgreSQL, Alembic 초기화, README 실행법.
M1. DB: 명세서 3장 그대로 모델(users, prompts, tags, prompt_tags, likes, bookmarks) +
    Alembic migration. prompts에 ai_source/variables(JSON)/is_public/counter 3종/updated_at,
    likes·bookmarks 복합 unique, 3-3 인덱스 반영.
M2. Auth: signup/login/refresh. bcrypt hashing. refresh=httpOnly cookie, access=응답으로,
    get_current_user dependency. Pydantic 입력검증.
M3. 프롬프트 CRUD + 변수 템플릿(시그니처): CRUD(작성자만 수정·삭제), 작성 시 tags upsert+매핑,
    prompt_text의 [변수명]을 파싱해 variables에 저장. FE는 [변수명] 감지→변수 Input→치환 복사.
M4. 피드: GET /prompts?cursor=&sort=latest|popular&tag= (cursor pagination, offset 금지),
    태그·카운트 selectinload. FE는 재사용 PromptCard + Masonry + IntersectionObserver 무한스크롤
    + 정렬 토글. seed script로 20개 이상 생성.
M5. 상호작용: like/bookmark 토글(+counter 갱신, 중복 방지), copy count, 태그 검색,
    /users/me 프로필 수정, 마이페이지 2탭(내 글/스크랩). FE는 Clipboard API 복사 버튼 포함.
M5b. 랜딩 페이지(비로그인 대문): 명세서 2-5 그대로. dark(#0A0A0A)+#0070F3+Pretendard,
    Glassmorphism, 배경 '프롬프트 은하수'(카드 ~30개 흐름+parallax+hover glint),
    중앙 Hero 카피, 단일 CTA(글로우+swipe light, 클릭 시 zoom-in transition→피드).
    GSAP+CSS+Vue Router transition. prefers-reduced-motion 존중. CTA는 email/password auth로 연결
    (Google 버튼 만들지 말 것). 비로그인 진입 시 이 페이지를 보여주고, 로그인 상태면 피드로.

완료 기준(스스로 확인): 비로그인 시 랜딩 노출→CTA 클릭→auth→signup→login→프롬프트 작성
([변수] 포함)→피드 스크롤(중복·누락 없음)→좋아요/스크랩/복사→태그 검색→마이페이지 반영까지 동작.
```

---

## BATCH B — Phase 2 (AI 차별화)

```
CLAUDE.md와 docs/기능명세서.md를 먼저 읽어라. 아래 M6~M8을 순서대로 자율 실행하고,
끝나면 짧게 보고하라. LLM_PROVIDER 기본값은 ollama(로컬)로 두고, gemini(3 Flash)도 구현만 해둬라.

M6. LLM Provider 추상화 + 튜닝: services/에 LLMProvider 추상 base + GeminiProvider(3 Flash)
    + OllamaProvider. env LLM_PROVIDER로 선택. POST /ai/tune(async)는 개선안 + 개선 이유를
    구조화 반환. 응답 캐싱 + per-user rate limit + 429 exponential backoff. FE에 'AI 다듬기'
    버튼과 before/after+이유 표시. (Gemini 무료 티어 주의사항은 명세서 2-4 참고)
M7. 자동 태그 추천: POST /ai/suggest-tags(async), 태그 3~5개 반환. provider·캐싱·rate limit
    재사용. FE는 추천 태그 chip 선택 UI.
M8. 카드 이미지 다운로드: html2canvas로 PromptCard 캡처 PNG 저장. 공유용 카드 스타일 별도.

완료 기준(스스로 확인): LLM_PROVIDER=ollama로 튜닝·태그추천 동작, 캐시 hit 시 재호출 없음,
카드 PNG 다운로드 시 텍스트 잘림 없음.
```

---

## Phase 3 — 나중에 (선택)
full-text search(tsvector+GIN) / 소셜 로그인(Kakao·Google) / 팔로우·알림 / 신고
