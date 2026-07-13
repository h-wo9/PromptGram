<script setup>
import { nextTick, onActivated, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  fetchFeed,
  increaseCopyCount,
  toggleBookmark,
  toggleLike,
} from '../api/prompts'
import { feedStale } from '../composables/feedSignal'
import { showToast } from '../composables/toast'
import AuroraBackground from '../components/AuroraBackground.vue'
import MasonryGrid from '../components/MasonryGrid.vue'
import PromptCard from '../components/PromptCard.vue'
import PromptDetailModal from '../components/PromptDetailModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import ThemeToggle from '../components/ThemeToggle.vue'

// KeepAlive 대상 이름 (뒤로가기 시 목록·스크롤 유지)
defineOptions({ name: 'FeedView' })

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const searchInput = ref('')
const mobileSearch = ref(false)
const detail = ref(null) // { prompt, el } — 카드 확대 상세
const items = ref([])
const nextCursor = ref(null)
const sort = ref('latest')
const tag = ref(route.query.tag ?? null)
const q = ref(route.query.q ?? null) // 키워드 검색 (제목+본문, pg_trgm)
const loading = ref(false)
const done = ref(false)
const sentinel = ref(null)
const feedVersion = ref(0) // reset 데이터가 도착할 때만 증가 → grid crossfade 트리거
let observer = null
let requestSeq = 0

async function loadMore(reset = false) {
  // reset(정렬·태그 전환)은 진행 중 로드를 무시하고 항상 최신 요청을 우선한다
  if (!reset && (loading.value || done.value)) return
  const seq = ++requestSeq
  loading.value = true
  try {
    const data = await fetchFeed({
      cursor: reset ? undefined : nextCursor.value ?? undefined,
      sort: sort.value,
      tag: tag.value ?? undefined,
      q: q.value ?? undefined,
    })
    if (seq !== requestSeq) return // 더 최신 요청이 나감 — 결과 폐기
    if (reset) {
      // 기존 카드를 유지하다가 새 데이터 도착 시점에 교체 (빈 화면 플래시 방지)
      items.value = data.items
      feedVersion.value += 1
    } else {
      items.value.push(...data.items)
    }
    nextCursor.value = data.next_cursor
    done.value = !data.next_cursor
  } finally {
    if (seq === requestSeq) {
      loading.value = false
      // sentinel이 여전히 화면 안이면 re-observe로 초기 콜백을 다시 받아 이어서 로드
      await nextTick()
      if (!done.value && observer && sentinel.value) {
        observer.unobserve(sentinel.value)
        observer.observe(sentinel.value)
      }
    }
  }
}

watch([sort, tag, q], () => {
  const query = {}
  if (tag.value) query.tag = tag.value
  if (q.value) query.q = q.value
  router.replace({ query })
  loadMore(true)
})

onMounted(() => {
  loadMore(true)
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting) loadMore()
    },
    { rootMargin: '400px' }
  )
  if (sentinel.value) observer.observe(sentinel.value)
})
onUnmounted(() => observer?.disconnect())

// keep-alive 복귀: 게시/수정/삭제가 있었을 때만 새로고침 (뒤로가기는 캐시+스크롤 유지)
onActivated(() => {
  if (feedStale.value) {
    feedStale.value = false
    loadMore(true)
  }
})

function requireAuth() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'auth' })
    return false
  }
  return true
}

// 낙관적 업데이트: 즉시 반영 → 성공 시 서버값 동기화, 실패 시 롤백
async function onLike(prompt) {
  if (!requireAuth()) return
  const rollback = { is_liked: prompt.is_liked, like_count: prompt.like_count }
  prompt.is_liked = !prompt.is_liked
  prompt.like_count += prompt.is_liked ? 1 : -1
  try {
    Object.assign(prompt, await toggleLike(prompt.id))
  } catch {
    Object.assign(prompt, rollback)
    showToast('좋아요 처리에 실패했어요', 'error')
  }
}

async function onBookmark(prompt) {
  if (!requireAuth()) return
  const rollback = { is_bookmarked: prompt.is_bookmarked, bookmark_count: prompt.bookmark_count }
  prompt.is_bookmarked = !prompt.is_bookmarked
  prompt.bookmark_count += prompt.is_bookmarked ? 1 : -1
  try {
    Object.assign(prompt, await toggleBookmark(prompt.id))
  } catch {
    Object.assign(prompt, rollback)
    showToast('스크랩 처리에 실패했어요', 'error')
  }
}

async function onCopied(prompt) {
  try {
    const data = await increaseCopyCount(prompt.id)
    Object.assign(prompt, data)
  } catch {
    /* 카운트 실패는 무시 */
  }
}

// 통합 검색: '#태그'는 태그 필터, 그 외는 제목+본문 키워드 검색
function searchTag() {
  const raw = searchInput.value.trim()
  if (!raw) return
  if (raw.startsWith('#')) {
    const t = raw.replace(/^#+/, '').trim()
    if (t) {
      tag.value = t
      q.value = null
    }
  } else {
    q.value = raw
    tag.value = null
  }
  searchInput.value = ''
}

async function logout() {
  await auth.logout()
  router.push({ name: 'landing' })
}
</script>

<template>
  <div class="min-h-screen">
    <AuroraBackground />
    <header
      class="sticky top-0 z-20 border-b border-white/10 bg-night/80 backdrop-blur-xl light:border-slate-200 light:bg-white light:backdrop-blur-none"
    >
      <div class="max-w-6xl mx-auto px-4 h-14 flex items-center gap-4">
        <router-link to="/feed" class="text-lg font-extrabold tracking-tight">
          Prompt<span class="text-accent">Gram</span>
        </router-link>

        <div class="relative grid grid-cols-2 rounded-lg bg-white/5 light:bg-slate-900/[0.06] p-0.5 text-xs font-medium">
          <div
            class="absolute inset-y-0.5 left-0.5 w-[calc(50%-0.125rem)] rounded-md bg-gradient-to-r from-accent to-violet-600 transition-transform duration-300 ease-out"
            :class="sort === 'popular' ? 'translate-x-full' : ''"
            aria-hidden="true"
          ></div>
          <button
            class="relative z-10 px-3 py-1 transition-colors duration-300"
            :class="sort === 'latest' ? 'text-white' : 'text-gray-400 light:text-slate-500'"
            @click="sort = 'latest'"
          >
            최신
          </button>
          <button
            class="relative z-10 px-3 py-1 transition-colors duration-300"
            :class="sort === 'popular' ? 'text-white' : 'text-gray-400 light:text-slate-500'"
            @click="sort = 'popular'"
          >
            인기
          </button>
        </div>

        <button
          v-if="tag"
          class="rounded-full bg-accent/20 text-accent px-3 py-1 text-xs"
          @click="tag = null"
        >
          #{{ tag }} ✕
        </button>
        <button
          v-if="q"
          class="rounded-full bg-violet-500/20 text-violet-300 light:text-violet-600 px-3 py-1 text-xs"
          @click="q = null"
        >
          "{{ q }}" ✕
        </button>

        <form class="hidden sm:block" @submit.prevent="searchTag">
          <input
            v-model="searchInput"
            placeholder="검색 · #태그"
            class="w-36 rounded-lg bg-white/5 border border-white/10 light:bg-white light:border-slate-200 px-3 py-1.5 text-xs focus:border-accent focus:outline-none focus:w-48 transition-all"
          />
        </form>

        <span class="flex-1"></span>

        <!-- 모바일: 검색 토글 버튼 -->
        <button
          class="sm:hidden w-8 h-8 rounded-full border border-white/15 text-gray-300 light:border-slate-300 light:text-slate-600 hover:border-accent hover:text-accent transition-colors flex items-center justify-center"
          aria-label="태그 검색 열기"
          @click="mobileSearch = !mobileSearch"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
        </button>

        <ThemeToggle />
        <template v-if="auth.isLoggedIn">
          <router-link
            to="/write"
            class="btn-grad rounded-lg px-3.5 py-1.5 text-sm font-semibold text-white"
          >
            + 글쓰기
          </router-link>
          <router-link
            to="/me"
            class="text-sm text-gray-300 hover:text-white light:text-slate-600 light:hover:text-slate-900"
          >
            마이페이지
          </router-link>
          <button
            class="text-sm text-gray-500 hover:text-white light:hover:text-slate-900"
            @click="logout"
          >
            로그아웃
          </button>
        </template>
        <router-link
          v-else
          to="/auth"
          class="rounded-lg bg-accent hover:bg-blue-500 transition-colors px-3.5 py-1.5 text-sm font-semibold"
        >
          시작하기
        </router-link>
      </div>

      <!-- 모바일 검색 row -->
      <div v-if="mobileSearch" class="sm:hidden px-4 pb-3">
        <form @submit.prevent="searchTag(); mobileSearch = false">
          <input
            v-model="searchInput"
            placeholder="검색 · #태그"
            class="w-full rounded-lg bg-white/5 border border-white/10 light:bg-white light:border-slate-200 px-3 py-2 text-sm focus:border-accent focus:outline-none"
          />
        </form>
      </div>
    </header>

    <main class="relative z-10 max-w-6xl mx-auto px-4 py-6">
      <!-- 초기 로딩: shimmer skeleton -->
      <MasonryGrid v-if="loading && !items.length" :items="[1, 2, 3, 4, 5, 6].map((id) => ({ id }))" v-slot="{ item }">
        <SkeletonCard :lines="(item.id % 3) + 2" />
      </MasonryGrid>

      <transition v-else name="feed-swap" mode="out-in">
        <MasonryGrid :key="feedVersion" :items="items" v-slot="{ item }">
          <PromptCard
            :prompt="item"
            @like="onLike"
            @bookmark="onBookmark"
            @copied="onCopied"
            @tag="(t) => (tag = t)"
            @open="detail = $event"
          />
        </MasonryGrid>
      </transition>

      <div ref="sentinel" class="h-8"></div>
      <p v-if="loading && items.length" class="text-center text-sm text-gray-500 py-4">불러오는 중…</p>
      <p v-else-if="done && items.length" class="text-center text-sm text-gray-600 light:text-slate-400 py-4">
        마지막 프롬프트까지 다 봤어요
      </p>
      <p v-else-if="done && !items.length" class="text-center text-sm text-gray-500 py-16">
        아직 프롬프트가 없어요
      </p>
    </main>

    <PromptDetailModal
      v-if="detail"
      :prompt="detail.prompt"
      :source-el="detail.el"
      @close="detail = null"
      @like="onLike"
      @bookmark="onBookmark"
      @copied="onCopied"
    />
  </div>
</template>

<style scoped>
/* 정렬·태그 전환: 이전 grid가 살짝 내려가며 사라지고 새 grid가 fade-in (카드 stagger는 MasonryGrid) */
.feed-swap-enter-active {
  transition: opacity 0.2s ease;
}
.feed-swap-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.feed-swap-enter-from {
  opacity: 0;
}
.feed-swap-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
@media (prefers-reduced-motion: reduce) {
  .feed-swap-leave-to {
    transform: none;
  }
}
</style>
