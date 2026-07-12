<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import gsap from 'gsap'

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
  { title: '커밋 메시지', text: 'conventional commit 메시지 만들어줘', source: 'ChatGPT' },
  { title: '자소서 초안', text: '[회사] [직무] 문항 답변 초안 작성해줘', source: 'Claude' },
  { title: '독서 토론', text: '[책제목] 토론 질문 8개 만들어줘', source: 'Gemini' },
]

const galaxyFar = ref(null)
const galaxyNear = ref(null)
const stage = ref(null)
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches

// 카드 배치: 레이어별 레인에 분산 (상한 ~30개)
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
const farCards = buildCards(isMobile ? 6 : 14, 1)
const nearCards = buildCards(isMobile ? 6 : 12, 2)

let ctx = null
let rafId = null
let mouseHandler = null

onMounted(() => {
  if (reduced) return

  ctx = gsap.context(() => {
    // 위→아래로 아주 천천히 흐르는 카드 (transform만 사용)
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
          modifiers: {
            y: (y) => `${(parseFloat(y) % travel) - travel * 0.15}px`,
          },
        }
      )
    })
  }, stage.value)

  // 마우스 반대 방향 parallax (rAF throttle)
  let mx = 0
  let my = 0
  let queued = false
  mouseHandler = (e) => {
    mx = e.clientX / window.innerWidth - 0.5
    my = e.clientY / window.innerHeight - 0.5
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
  if (rafId) cancelAnimationFrame(rafId)
})

// CTA: 카드 속으로 빨려드는 zoom-in 후 auth로
function start() {
  if (reduced) {
    router.push({ name: 'auth' })
    return
  }
  // scale 중 stage가 viewport를 넘쳐 scrollbar가 깜빡이는 것 방지 (route 전환의 after-enter에서 해제됨)
  document.documentElement.style.overflow = 'hidden'
  gsap.to(stage.value, {
    scale: 1.18,
    opacity: 0,
    duration: 0.5,
    ease: 'power2.in',
    onComplete: () => router.push({ name: 'auth' }),
  })
}
</script>

<template>
  <div ref="stage" class="landing relative min-h-screen overflow-hidden">
    <!-- 프롬프트 은하수 -->
    <div ref="galaxyFar" class="galaxy absolute inset-0" aria-hidden="true">
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
    <div ref="galaxyNear" class="galaxy absolute inset-0" aria-hidden="true">
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

    <!-- 가독성용 비네트 -->
    <div class="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,transparent_30%,#0A0A0A_92%)]"></div>

    <!-- 중앙 Hero -->
    <main class="relative z-10 min-h-screen flex flex-col items-center justify-center text-center px-6">
      <p class="text-sm font-semibold tracking-[0.2em] text-gray-500 uppercase">PromptGram</p>
      <h1 class="mt-5 text-4xl sm:text-5xl md:text-6xl font-extrabold leading-[1.15] tracking-tight max-w-3xl">
        당신의 <span class="var-chip">[완벽한 질문]</span>,<br />
        허공에 날리지 마세요.
      </h1>
      <p class="mt-6 text-base sm:text-lg text-gray-400 max-w-xl">
        전 세계의 검증된 프롬프트를 아카이빙하고,<br class="sm:hidden" />
        AI 100% 활용법을 발견하세요.
      </p>
      <button class="cta group mt-10" @click="start">
        <span class="relative z-10">PromptGram 시작하기</span>
      </button>
      <p class="mt-4 text-xs text-gray-600">
        이미 계정이 있다면
        <router-link to="/auth" class="inline-block px-1 py-1 text-gray-400 underline underline-offset-2 hover:text-white">로그인</router-link>
      </p>
    </main>
  </div>
</template>

<style scoped>
.landing {
  transform-origin: 50% 45%;
}

/* ── 배경 카드 ─────────────────────────── */
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
/* hover 시 대각선 glint */
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

/* ── Hero 변수 chip ─────────────────────── */
.var-chip {
  color: #0070f3;
  text-shadow: 0 0 32px rgba(0, 112, 243, 0.55);
}

/* ── CTA ────────────────────────────────── */
.cta {
  position: relative;
  overflow: hidden;
  padding: 1rem 2.75rem;
  border-radius: 9999px;
  font-size: 1.05rem;
  font-weight: 700;
  color: #fff;
  background: #0070f3;
  box-shadow: 0 0 24px rgba(0, 112, 243, 0.35);
  transition: box-shadow 0.4s ease, transform 0.2s ease;
}
.cta:hover {
  box-shadow:
    0 0 44px rgba(0, 112, 243, 0.6),
    0 0 90px rgba(0, 112, 243, 0.25);
  transform: translateY(-1px);
}
/* 좌→우 swipe light */
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

/* ── reduced motion: 흐름·parallax·glint 정지 ── */
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
}
</style>
