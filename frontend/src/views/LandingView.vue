<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()

// 배경 '프롬프트 은하수' 카드 콘텐츠 (실제 서비스 톤의 스니펫)
const SNIPPETS = [
  { title: '코드 리뷰 요청', text: '다음 [언어] 코드를 [관점] 관점에서 리뷰해줘', source: 'ChatGPT' },
  { title: '이메일 다듬기', text: '아래 초안을 [톤] 톤으로 다듬어줘', source: 'Claude' },
  { title: '여행 일정', text: '[도시] 2박 3일, 예산 [예산]으로 일정 짜줘', source: 'Gemini' },
  { title: '면접 준비', text: '[직무] 면접 예상 질문 10개와 답변 포인트', source: 'ChatGPT' },
  { title: 'SQL 최적화', text: '이 쿼리를 실행 계획 관점에서 최적화해줘', source: 'Claude' },
  { title: '블로그 개요', text: '[주제] 글 개요를 SEO 키워드 포함해 잡아줘', source: 'Gemini' },
  { title: '영어 교정', text: '자연스럽게 교정하고 이유를 설명해줘', source: 'ChatGPT' },
  { title: '회의록 정리', text: '녹취록에서 안건별 action item을 뽑아줘', source: 'Claude' },
  { title: '마케팅 카피', text: '[제품] 인스타 광고 카피 5가지 톤으로', source: 'Gemini' },
  { title: '정규식 생성', text: '[요구사항]을 만족하는 정규식과 테스트 5개', source: 'ChatGPT' },
  { title: '발표 스크립트', text: '[주제]로 5분 발표 스크립트를 써줘', source: 'Claude' },
  { title: '운동 루틴', text: '주 [횟수]회 [목표] 루틴, 장비는 덤벨만', source: 'Gemini' },
]

// 피드 미리보기 섹션용 미니 카드
const FEED_PREVIEW = [
  { title: '코드 리뷰 요청 템플릿', tag: '개발', likes: 128, copies: 342 },
  { title: '이메일 정중하게 다듬기', tag: '업무', likes: 96, copies: 210 },
  { title: '논문 3문장 요약', tag: '연구', likes: 87, copies: 154 },
  { title: '면접 예상 질문 10선', tag: '커리어', likes: 143, copies: 388 },
  { title: '유튜브 훅 스크립트', tag: '콘텐츠', likes: 74, copies: 132 },
  { title: '하루 식단 설계', tag: '건강', likes: 61, copies: 98 },
]

const galaxyFar = ref(null)
const galaxyNear = ref(null)
const stage = ref(null)
const scrolled = ref(false)
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

// ── 타이핑 애니메이션 factory: 섹션 진입 시 start()로 시작 ──
function createTyping(segments, { loop = false, speed = 46 } = {}) {
  const chars = segments.flatMap((s) => [...s.t].map((ch) => ({ ch, v: !!s.v })))
  const count = ref(reduced ? chars.length : 0)
  const done = ref(reduced)
  let timer = null
  let started = false

  function tick() {
    if (count.value >= chars.length) {
      done.value = true
      if (loop) {
        // 완성 후 잠시 유지 → 지우고 다시 타이핑
        timer = setTimeout(() => {
          count.value = 0
          done.value = false
          timer = setTimeout(tick, 500)
        }, 2400)
      }
      return
    }
    count.value += 1
    timer = setTimeout(tick, speed)
  }

  function start(delay = 0) {
    if (started || reduced) return
    started = true
    timer = setTimeout(tick, delay)
  }

  function stop() {
    if (timer) clearTimeout(timer)
  }

  const rendered = computed(() => {
    const out = []
    for (const { ch, v } of chars.slice(0, count.value)) {
      const last = out[out.length - 1]
      if (last && last.v === v) last.text += ch
      else out.push({ text: ch, v })
    }
    return out
  })

  return { rendered, done, start, stop }
}

const tplTyping = createTyping(
  [
    { t: '다음 ' },
    { t: '[원문]', v: true },
    { t: '을 ' },
    { t: '[언어]', v: true },
    { t: '로, ' },
    { t: '[톤]', v: true },
    { t: ' 톤을 유지해 번역해줘.' },
  ],
  { loop: true }
)

const afterTyping = createTyping(
  [
    { t: '당신은 비즈니스 커뮤니케이션 전문가입니다. ' },
    { t: '[원본 이메일]', v: true },
    { t: '을 ' },
    { t: '[수신자]', v: true },
    { t: '와의 관계를 고려해 정중한 비즈니스 메일로 재작성하세요…' },
  ],
  { speed: 24 }
)

function buildCards(count, layerSeed) {
  const cards = []
  for (let i = 0; i < count; i += 1) {
    const s = SNIPPETS[(i * 7 + layerSeed) % SNIPPETS.length]
    cards.push({
      ...s,
      id: `${layerSeed}-${i}`,
      left: ((i + 0.5) / count) * 100 + (((i * 13 + layerSeed * 5) % 7) - 3),
      top: ((i * 37 + layerSeed * 53) % 120) - 10,
      dur: 60 + ((i * 11 + layerSeed * 3) % 45),
      rot: (((i * 17) % 9) - 4) * 0.8,
    })
  }
  return cards
}

const isMobile = window.innerWidth < 640
const farCards = buildCards(isMobile ? 5 : 11, 1)
const nearCards = buildCards(isMobile ? 5 : 9, 2)

let ctx = null
let rafId = null
let mouseHandler = null
let scrollHandler = null

onMounted(() => {
  scrollHandler = () => {
    scrolled.value = window.scrollY > 40
  }
  window.addEventListener('scroll', scrollHandler, { passive: true })

  if (reduced) return

  ctx = gsap.context(() => {
    // 은하수: 위→아래로 아주 천천히 흐름 (transform만)
    document.querySelectorAll('[data-drift]').forEach((el) => {
      const dur = Number(el.dataset.drift)
      const travel = window.innerHeight * 1.4
      gsap.fromTo(
        el,
        { y: 0 },
        {
          y: travel,
          duration: dur,
          ease: 'none',
          repeat: -1,
          modifiers: { y: (y) => `${(parseFloat(y) % travel) - travel * 0.15}px` },
        }
      )
    })

    // 대기 조명: 스크롤 진행에 따라 aurora blob이 이동·회전하며 환경이 변함
    const env = gsap.timeline({
      scrollTrigger: { trigger: stage.value, start: 'top top', end: 'bottom bottom', scrub: 0.8 },
    })
    env
      .to('.aurora-a', { xPercent: 38, yPercent: 46, scale: 1.35, rotate: 40, ease: 'none' }, 0)
      .to('.aurora-b', { xPercent: -42, yPercent: -30, scale: 1.5, rotate: -30, ease: 'none' }, 0)
      .to('.aurora-c', { xPercent: 20, yPercent: -55, scale: 1.25, ease: 'none' }, 0)
      .to('.aurora-a', { opacity: 0.5, ease: 'none' }, 0)
      .to('.aurora-b', { opacity: 0.85, ease: 'none' }, 0)

    // Apple 스타일 pinned 전환: 변수 템플릿 → AI 다듬기
    const pinTl = gsap.timeline({
      scrollTrigger: {
        trigger: '.pin-stage',
        start: 'top top',
        end: '+=160%',
        scrub: 0.6,
        pin: true,
      },
    })
    pinTl
      .to('.slide-1', { autoAlpha: 0, y: -70, ease: 'power1.in', duration: 1 }, 0.55)
      .fromTo(
        '.slide-2',
        { autoAlpha: 0, y: 90 },
        { autoAlpha: 1, y: 0, ease: 'power1.out', duration: 1 },
        1.25
      )
      .call(() => afterTyping.start(350), [], 1.7) // AFTER 카드가 보이면 타이핑 시작 (1회)
      .to({}, { duration: 0.45 }) // 전환 후 잠깐 머무름

    // 변수 템플릿 박스: 섹션이 화면에 들어올 때 비어 있다가 타이핑 시작
    ScrollTrigger.create({
      trigger: '.pin-stage',
      start: 'top 70%',
      once: true,
      onEnter: () => tplTyping.start(250),
    })

    // 섹션 콘텐츠 reveal
    gsap.utils.toArray('[data-reveal]').forEach((el) => {
      gsap.fromTo(
        el,
        { opacity: 0, y: 36 },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: 'power2.out',
          scrollTrigger: { trigger: el, start: 'top 82%', once: true },
        }
      )
    })

    // 피드 미리보기: 좋아요·복사 숫자가 차오르는 count-up
    gsap.utils.toArray('[data-count]').forEach((el) => {
      gsap.fromTo(
        el,
        { textContent: 0 },
        {
          textContent: Number(el.dataset.count),
          duration: 1.8,
          ease: 'power1.out',
          snap: { textContent: 1 },
          immediateRender: true,
          scrollTrigger: { trigger: el, start: 'top 88%', once: true },
        }
      )
    })

    // 피드 미리보기: 컬럼별 다른 속도의 패럴랙스 (심도)
    gsap.utils.toArray('[data-parallax]').forEach((el) => {
      gsap.fromTo(
        el,
        { yPercent: Number(el.dataset.parallax) },
        {
          yPercent: -Number(el.dataset.parallax),
          ease: 'none',
          scrollTrigger: { trigger: el, start: 'top bottom', end: 'bottom top', scrub: 1 },
        }
      )
    })
  }, stage.value)

  // 마우스 반대 방향 parallax (hero 은하수, rAF throttle)
  let queued = false
  mouseHandler = (e) => {
    const mx = e.clientX / window.innerWidth - 0.5
    const my = e.clientY / window.innerHeight - 0.5
    if (!queued) {
      queued = true
      rafId = requestAnimationFrame(() => {
        queued = false
        gsap.to(galaxyFar.value, { x: mx * -10, y: my * -8, duration: 0.8, overwrite: 'auto' })
        gsap.to(galaxyNear.value, { x: mx * -26, y: my * -18, duration: 0.6, overwrite: 'auto' })
      })
    }
  }
  window.addEventListener('mousemove', mouseHandler, { passive: true })
})

onUnmounted(() => {
  ctx?.revert()
  if (mouseHandler) window.removeEventListener('mousemove', mouseHandler)
  if (scrollHandler) window.removeEventListener('scroll', scrollHandler)
  if (rafId) cancelAnimationFrame(rafId)
  tplTyping.stop()
  afterTyping.stop()
})

// CTA: 카드 속으로 빨려드는 zoom-in 후 auth로
function start() {
  if (reduced) {
    router.push({ name: 'auth' })
    return
  }
  document.documentElement.style.overflow = 'hidden'
  const originY = window.scrollY + window.innerHeight / 2
  gsap.to(stage.value, {
    scale: 1.18,
    opacity: 0,
    duration: 0.5,
    ease: 'power2.in',
    transformOrigin: `50% ${originY}px`,
    onComplete: () => router.push({ name: 'auth' }),
  })
}
</script>

<template>
  <div ref="stage" class="landing relative overflow-hidden">
    <!-- ── 대기 조명 (viewport 고정 aurora) ── -->
    <div class="fixed inset-0 pointer-events-none" aria-hidden="true">
      <div class="aurora aurora-a"></div>
      <div class="aurora aurora-b"></div>
      <div class="aurora aurora-c"></div>
    </div>

    <!-- ── 상단 고정 nav (스크롤 시 glass bar) ── -->
    <header
      class="fixed top-0 inset-x-0 z-40 flex items-center justify-between px-6 sm:px-10 h-16 transition-all duration-300"
      :class="scrolled ? 'bg-night/70 backdrop-blur-md border-b border-white/10' : 'border-b border-transparent'"
    >
      <span class="text-base font-extrabold tracking-tight">Prompt<span class="text-accent">Gram</span></span>
      <router-link
        to="/auth"
        class="rounded-full border border-white/15 px-4 py-1.5 text-xs text-gray-300 hover:border-accent hover:text-white transition-colors"
      >
        로그인
      </router-link>
    </header>

    <!-- ════ S1. Hero — 프롬프트 은하수 ════ -->
    <section class="relative min-h-screen flex flex-col items-center justify-center text-center px-6 overflow-hidden">
      <div ref="galaxyFar" class="absolute inset-0" aria-hidden="true">
        <div
          v-for="c in farCards"
          :key="c.id"
          class="gcard gcard--far"
          :data-drift="c.dur"
          :style="{ left: c.left + '%', top: c.top + '%', '--rot': c.rot + 'deg' }"
        >
          <p class="gcard-title">{{ c.title }}</p>
          <p class="gcard-text">{{ c.text }}</p>
          <span class="gcard-badge">{{ c.source }}</span>
        </div>
      </div>
      <div ref="galaxyNear" class="absolute inset-0" aria-hidden="true">
        <div
          v-for="c in nearCards"
          :key="c.id"
          class="gcard gcard--near"
          :data-drift="c.dur * 0.7"
          :style="{ left: c.left + '%', top: c.top + '%', '--rot': c.rot + 'deg' }"
        >
          <p class="gcard-title">{{ c.title }}</p>
          <p class="gcard-text">{{ c.text }}</p>
          <span class="gcard-badge">{{ c.source }}</span>
        </div>
      </div>
      <div class="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,transparent_30%,#0A0A0A_92%)]"></div>

      <div class="relative z-10">
        <p class="text-sm font-semibold tracking-[0.2em] text-gray-500 uppercase">PromptGram</p>
        <h1 class="mt-5 text-4xl sm:text-5xl md:text-6xl font-extrabold leading-[1.15] tracking-tight max-w-3xl">
          당신의 <span class="var-chip">[완벽한 질문]</span>,<br />
          허공에 날리지 마세요.
        </h1>
        <p class="mt-6 text-base sm:text-lg text-gray-400 max-w-xl mx-auto">
          전 세계의 검증된 프롬프트를 아카이빙하고,<br class="sm:hidden" />
          AI 100% 활용법을 발견하세요.
        </p>
        <button class="cta group mt-10" @click="start">
          <span class="relative z-10">PromptGram 시작하기</span>
        </button>
      </div>

      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 text-gray-600 text-xs tracking-widest animate-bounce-slow">
        SCROLL ↓
      </div>
    </section>

    <!-- ════ S2+S3. Pinned 전환: 변수 템플릿 → AI 다듬기 ════ -->
    <section class="pin-stage">
      <div class="slide slide-1">
        <div class="section-inner">
          <div>
            <p class="eyebrow">변수 템플릿</p>
            <h2 class="headline">한 번의 발견을,<br /><span class="grad-text">평생의 도구로.</span></h2>
            <p class="body-copy">
              잘 만든 프롬프트를 매번 처음부터 다시 쓰고 있진 않나요?
              본문에 <span class="text-accent font-semibold">[변수]</span>만 넣어 저장하면,
              값을 갈아끼워 언제든 다시 꺼내 쓰는 나만의 템플릿이 됩니다.
            </p>
          </div>

          <div class="demo-wrap">
            <div class="demo-glow" aria-hidden="true"></div>
            <div class="demo-card">
              <div class="flex items-center justify-between">
                <span class="text-xs font-bold text-gray-300">번역 프롬프트</span>
                <span class="rounded-full bg-violet-500/20 text-violet-300 px-2.5 py-0.5 text-[11px] font-semibold">변수 3개 템플릿</span>
              </div>
              <p class="mt-4 text-[15px] leading-relaxed text-gray-200 min-h-[3.2em]">
                <template v-for="(seg, i) in tplTyping.rendered.value" :key="i">
                  <span v-if="seg.v" class="demo-var">{{ seg.text }}</span>
                  <template v-else>{{ seg.text }}</template>
                </template><span class="type-caret" aria-hidden="true"></span>
              </p>
              <div class="mt-5 rounded-lg bg-accent/90 text-center py-2.5 text-sm font-semibold shadow-[0_0_18px_rgba(0,112,243,0.4)]">
                변수 채워서 복사
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="slide slide-2">
        <div class="section-inner section-inner--reverse">
          <div>
            <p class="eyebrow eyebrow--violet">AI 다듬기 · 태그 추천</p>
            <h2 class="headline">쓰다 만 문장도,<br /><span class="grad-text">AI가 프로의 프롬프트로.</span></h2>
            <p class="body-copy">
              초안을 던지면 AI가 더 구체적이고 명확하게 다듬고,
              <strong class="text-gray-200">왜 그렇게 고쳤는지 이유까지</strong> 설명합니다.
              어울리는 태그도 골라주니, 정리는 덤이에요.
            </p>
            <ul class="mt-6 flex flex-wrap gap-2 text-xs">
              <li class="reason-chip">페르소나 부여</li>
              <li class="reason-chip">변수로 재사용성 확장</li>
              <li class="reason-chip">구체적 지침 추가</li>
            </ul>
          </div>

          <div class="demo-wrap">
            <div class="demo-glow demo-glow--violet" aria-hidden="true"></div>
            <div class="space-y-3">
              <div class="demo-card demo-card--dim">
                <p class="text-[11px] font-semibold text-gray-500 mb-1.5">BEFORE</p>
                <p class="text-sm text-gray-400">이메일 좀 정중하게 다듬어줘</p>
              </div>
              <div class="ai-beam" aria-hidden="true">✦</div>
              <div class="demo-card demo-card--ai">
                <p class="text-[11px] font-semibold text-violet-300 mb-1.5">AFTER — AI 개선 제안</p>
                <p class="text-sm leading-relaxed text-gray-200 min-h-[4.6em]">
                  <template v-for="(seg, i) in afterTyping.rendered.value" :key="i">
                    <span v-if="seg.v" class="demo-var">{{ seg.text }}</span>
                    <template v-else>{{ seg.text }}</template>
                  </template><span
                    v-if="!afterTyping.done.value"
                    class="type-caret type-caret--violet"
                    aria-hidden="true"
                  ></span>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ════ S4. 소셜 피드 ════ -->
    <section class="section">
      <div class="text-center max-w-2xl mx-auto px-6" data-reveal>
        <p class="eyebrow">소셜 피드 · 아카이브</p>
        <h2 class="headline">검증된 프롬프트가<br /><span class="grad-text">흐르는 곳.</span></h2>
        <p class="body-copy mx-auto">
          좋아요와 스크랩으로 커뮤니티가 골라낸 프롬프트를 무한 피드로 만나세요.
          마음에 들면 원클릭 복사, 자랑하고 싶으면 카드 이미지로 공유까지.
        </p>
      </div>

      <div class="mt-14 grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-4xl mx-auto px-6" data-reveal>
        <div
          v-for="(card, i) in FEED_PREVIEW"
          :key="card.title"
          class="mini-card"
          :data-parallax="[6, 14, 9][i % 3]"
        >
          <p class="text-[13px] font-bold leading-snug">{{ card.title }}</p>
          <span class="mt-2 inline-block rounded-full bg-accent/15 text-accent px-2 py-0.5 text-[10px]">#{{ card.tag }}</span>
          <div class="mt-3 flex gap-3 text-[11px] text-gray-500">
            <span class="text-red-400/80">♥ <span :data-count="card.likes">{{ card.likes }}</span></span>
            <span>⧉ <span :data-count="card.copies">{{ card.copies }}</span></span>
          </div>
        </div>
      </div>
    </section>

    <!-- ════ S5. 최종 CTA ════ -->
    <section class="relative min-h-[70vh] flex flex-col items-center justify-center text-center px-6">
      <div class="cta-orb" aria-hidden="true"></div>
      <div class="relative z-10" data-reveal>
        <h2 class="headline">지금, 첫 프롬프트를<br /><span class="grad-text">아카이브하세요.</span></h2>
        <p class="mt-4 text-gray-400">30초면 충분해요. 이메일 하나로 시작합니다.</p>
        <button class="cta group mt-9" @click="start">
          <span class="relative z-10">PromptGram 시작하기</span>
        </button>
      </div>
      <p class="absolute bottom-6 text-xs text-gray-700">© PromptGram — 당신의 완벽한 질문을 위해</p>
    </section>
  </div>
</template>

<style scoped>
.landing {
  transform-origin: 50% 45%;
  background: #0a0a0a;
}

/* ── 대기 조명: pre-blurred radial gradient (filter 없이 저비용) ── */
.aurora {
  position: absolute;
  width: 90vmax;
  height: 90vmax;
  border-radius: 9999px;
  will-change: transform, opacity;
}
.aurora-a {
  top: -30vmax;
  left: -25vmax;
  background: radial-gradient(closest-side, rgba(0, 112, 243, 0.34), rgba(0, 112, 243, 0.1) 45%, transparent 70%);
  opacity: 0.9;
}
.aurora-b {
  bottom: -40vmax;
  right: -30vmax;
  background: radial-gradient(closest-side, rgba(124, 58, 237, 0.32), rgba(124, 58, 237, 0.1) 45%, transparent 70%);
  opacity: 0.55;
}
.aurora-c {
  top: 30%;
  left: 30%;
  width: 60vmax;
  height: 60vmax;
  background: radial-gradient(closest-side, rgba(59, 130, 246, 0.16), transparent 65%);
  opacity: 0.7;
}

/* ── 공통 섹션 레이아웃 ── */
.section {
  position: relative;
  padding: 8.5rem 0;
}

/* ── Pinned 전환 스테이지 (모션 허용 시 슬라이드를 겹쳐두고 GSAP이 crossfade) ── */
@media (prefers-reduced-motion: no-preference) {
  .pin-stage {
    position: relative;
    height: 100vh;
    overflow: hidden;
  }
  .slide {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .slide-2 {
    opacity: 0;
    visibility: hidden;
  }
}
@media (prefers-reduced-motion: reduce) {
  .slide {
    padding: 6rem 0;
  }
}

/* 타이핑 caret */
.type-caret {
  display: inline-block;
  width: 2px;
  height: 1.05em;
  margin-left: 2px;
  vertical-align: -0.15em;
  background: #3b96ff;
  animation: caret-blink 1s steps(2) infinite;
}
.type-caret--violet {
  background: #a78bfa;
}
@keyframes caret-blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
.section-inner {
  display: grid;
  gap: 3.5rem;
  align-items: center;
  max-width: 64rem;
  margin: 0 auto;
  padding: 0 1.5rem;
}
@media (min-width: 768px) {
  .section-inner {
    grid-template-columns: 1fr 1fr;
  }
  .section-inner--reverse > :first-child {
    order: 2;
  }
}
.eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  color: #3b96ff;
  text-transform: uppercase;
}
.eyebrow--violet {
  color: #a78bfa;
}
.headline {
  margin-top: 1rem;
  font-size: clamp(1.9rem, 4vw, 2.75rem);
  font-weight: 800;
  line-height: 1.22;
  letter-spacing: -0.02em;
}
.grad-text {
  background: linear-gradient(100deg, #3b96ff, #a78bfa);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.body-copy {
  margin-top: 1.25rem;
  font-size: 0.975rem;
  line-height: 1.8;
  color: #9ca3af;
  max-width: 26rem;
}

/* ── 데모 카드 (DOF: 뒤에 흐린 glow, 앞은 선명한 glass) ── */
.demo-wrap {
  position: relative;
}
.demo-glow {
  position: absolute;
  inset: -18%;
  background: radial-gradient(closest-side, rgba(0, 112, 243, 0.22), transparent 70%);
  pointer-events: none;
}
.demo-glow--violet {
  background: radial-gradient(closest-side, rgba(124, 58, 237, 0.24), transparent 70%);
}
.demo-card {
  position: relative;
  border-radius: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  padding: 1.5rem;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45);
}
.demo-card--dim {
  opacity: 0.75;
  padding: 1.1rem 1.5rem;
}
.demo-card--ai {
  border-color: rgba(167, 139, 250, 0.4);
  box-shadow: 0 0 34px rgba(124, 58, 237, 0.18), 0 20px 60px rgba(0, 0, 0, 0.45);
}
.demo-var {
  color: #3b96ff;
  font-weight: 700;
  animation: var-pulse 3.6s ease-in-out infinite;
}
@keyframes var-pulse {
  0%, 100% { text-shadow: 0 0 0 rgba(59, 150, 255, 0); }
  50% { text-shadow: 0 0 16px rgba(59, 150, 255, 0.75); }
}
.ai-beam {
  text-align: center;
  color: #a78bfa;
  font-size: 0.9rem;
  text-shadow: 0 0 12px rgba(167, 139, 250, 0.8);
}
.reason-chip {
  border: 1px solid rgba(167, 139, 250, 0.35);
  color: #c4b5fd;
  border-radius: 9999px;
  padding: 0.3rem 0.8rem;
}

/* ── 피드 미리보기 미니 카드 ── */
.mini-card {
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  padding: 1rem;
  will-change: transform;
}

/* ── 최종 CTA orb ── */
.cta-orb {
  position: absolute;
  width: 34rem;
  height: 34rem;
  border-radius: 9999px;
  background: radial-gradient(closest-side, rgba(0, 112, 243, 0.22), rgba(124, 58, 237, 0.14) 55%, transparent 72%);
  animation: orb-breathe 7s ease-in-out infinite;
}
@keyframes orb-breathe {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.08); opacity: 1; }
}

/* ── 은하수 카드 (기존 유지) ── */
.gcard {
  position: absolute;
  width: 13.5rem;
  padding: 0.9rem 1rem;
  border-radius: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.04);
  transform: rotate(var(--rot));
  will-change: transform;
  transition: opacity 0.35s ease, filter 0.35s ease, border-color 0.35s ease;
  overflow: hidden;
}
.gcard--far {
  opacity: 0.18;
  filter: blur(2.5px);
  scale: 0.82;
}
.gcard--near {
  opacity: 0.3;
  filter: blur(1.2px);
}
.gcard:hover {
  opacity: 0.92;
  filter: blur(0);
  border-color: rgba(0, 112, 243, 0.5);
}
.gcard::after {
  content: '';
  position: absolute;
  inset: -150% auto auto -60%;
  width: 45%;
  height: 400%;
  transform: rotate(25deg) translateX(-140%);
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.22), transparent);
}
.gcard:hover::after {
  transition: transform 0.7s ease;
  transform: rotate(25deg) translateX(520%);
}
.gcard:hover .gcard-badge {
  color: #fff;
  background: rgba(0, 112, 243, 0.85);
  box-shadow: 0 0 14px rgba(0, 112, 243, 0.6);
}
.gcard-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: #e5e7eb;
}
.gcard-text {
  margin-top: 0.3rem;
  font-size: 0.66rem;
  line-height: 1.45;
  color: #9ca3af;
}
.gcard-badge {
  display: inline-block;
  margin-top: 0.55rem;
  padding: 0.1rem 0.55rem;
  border-radius: 9999px;
  font-size: 0.58rem;
  font-weight: 600;
  color: #d1d5db;
  background: rgba(255, 255, 255, 0.08);
  transition: all 0.35s ease;
}

/* ── Hero ── */
.var-chip {
  color: #0070f3;
  text-shadow: 0 0 32px rgba(0, 112, 243, 0.55);
}
.cta {
  position: relative;
  overflow: hidden;
  padding: 1rem 2.75rem;
  border-radius: 9999px;
  font-size: 1.05rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(115deg, #0070f3, #7c3aed 120%);
  box-shadow: 0 0 24px rgba(60, 95, 245, 0.4);
  transition: box-shadow 0.4s ease, transform 0.2s ease;
}
.cta:hover {
  box-shadow: 0 0 44px rgba(85, 90, 248, 0.65), 0 0 90px rgba(110, 75, 245, 0.28);
  transform: translateY(-1px);
}
.cta::before {
  content: '';
  position: absolute;
  inset: 0 auto 0 -40%;
  width: 35%;
  transform: skewX(-20deg) translateX(-120%);
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
}
.cta:hover::before {
  transition: transform 0.65s ease;
  transform: skewX(-20deg) translateX(480%);
}

.animate-bounce-slow {
  animation: bounce-slow 2.4s ease-in-out infinite;
}
@keyframes bounce-slow {
  0%, 100% { transform: translate(-50%, 0); }
  50% { transform: translate(-50%, 8px); }
}

/* ── reduced motion: 모든 장식 애니메이션 정지, 콘텐츠는 정적으로 노출 ── */
@media (prefers-reduced-motion: reduce) {
  .gcard,
  .gcard::after,
  .cta::before {
    transition: none;
  }
  .cta:hover::before,
  .gcard:hover::after {
    transform: none;
  }
  .demo-var,
  .cta-orb,
  .animate-bounce-slow,
  .type-caret {
    animation: none;
  }
}
</style>
