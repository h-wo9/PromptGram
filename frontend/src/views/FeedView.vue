<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  fetchFeed,
  increaseCopyCount,
  toggleBookmark,
  toggleLike,
} from '../api/prompts'
import MasonryGrid from '../components/MasonryGrid.vue'
import PromptCard from '../components/PromptCard.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const searchInput = ref('')
const items = ref([])
const nextCursor = ref(null)
const sort = ref('latest')
const tag = ref(route.query.tag ?? null)
const loading = ref(false)
const done = ref(false)
const sentinel = ref(null)
let observer = null

async function loadMore(reset = false) {
  if (loading.value || (done.value && !reset)) return
  loading.value = true
  try {
    if (reset) {
      items.value = []
      nextCursor.value = null
      done.value = false
    }
    const data = await fetchFeed({
      cursor: nextCursor.value ?? undefined,
      sort: sort.value,
      tag: tag.value ?? undefined,
    })
    items.value.push(...data.items)
    nextCursor.value = data.next_cursor
    if (!data.next_cursor) done.value = true
  } finally {
    loading.value = false
  }
}

watch([sort, tag], () => {
  router.replace({ query: tag.value ? { tag: tag.value } : {} })
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

function requireAuth() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'auth' })
    return false
  }
  return true
}

async function onLike(prompt) {
  if (!requireAuth()) return
  const data = await toggleLike(prompt.id)
  Object.assign(prompt, data)
}

async function onBookmark(prompt) {
  if (!requireAuth()) return
  const data = await toggleBookmark(prompt.id)
  Object.assign(prompt, data)
}

async function onCopied(prompt) {
  try {
    const data = await increaseCopyCount(prompt.id)
    Object.assign(prompt, data)
  } catch {
    /* 카운트 실패는 무시 */
  }
}

function searchTag() {
  const t = searchInput.value.replace(/^#/, '').trim()
  if (t) tag.value = t
  searchInput.value = ''
}

async function logout() {
  await auth.logout()
  router.push({ name: 'landing' })
}
</script>

<template>
  <div class="min-h-screen">
    <header
      class="sticky top-0 z-20 border-b border-white/10 bg-base/80 backdrop-blur-xl"
    >
      <div class="max-w-6xl mx-auto px-4 h-14 flex items-center gap-4">
        <router-link to="/feed" class="text-lg font-extrabold tracking-tight">
          Prompt<span class="text-accent">Gram</span>
        </router-link>

        <div class="flex rounded-lg bg-white/5 p-0.5 text-xs font-medium">
          <button
            :class="sort === 'latest' ? 'bg-accent rounded-md px-3 py-1' : 'px-3 py-1 text-gray-400'"
            @click="sort = 'latest'"
          >
            최신
          </button>
          <button
            :class="sort === 'popular' ? 'bg-accent rounded-md px-3 py-1' : 'px-3 py-1 text-gray-400'"
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

        <form class="hidden sm:block" @submit.prevent="searchTag">
          <input
            v-model="searchInput"
            placeholder="#태그 검색"
            class="w-36 rounded-lg bg-white/5 border border-white/10 px-3 py-1.5 text-xs focus:border-accent focus:outline-none focus:w-48 transition-all"
          />
        </form>

        <span class="flex-1"></span>

        <template v-if="auth.isLoggedIn">
          <router-link
            to="/write"
            class="rounded-lg bg-accent hover:bg-blue-500 transition-colors px-3.5 py-1.5 text-sm font-semibold"
          >
            + 글쓰기
          </router-link>
          <router-link to="/me" class="text-sm text-gray-300 hover:text-white">
            마이페이지
          </router-link>
          <button class="text-sm text-gray-500 hover:text-white" @click="logout">
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
    </header>

    <main class="max-w-6xl mx-auto px-4 py-6">
      <MasonryGrid :items="items" v-slot="{ item }">
        <PromptCard
          :prompt="item"
          @like="onLike"
          @bookmark="onBookmark"
          @copied="onCopied"
          @tag="(t) => (tag = t)"
        />
      </MasonryGrid>

      <div ref="sentinel" class="h-8"></div>
      <p v-if="loading" class="text-center text-sm text-gray-500 py-4">불러오는 중…</p>
      <p v-else-if="done && items.length" class="text-center text-sm text-gray-600 py-4">
        마지막 프롬프트까지 다 봤어요
      </p>
      <p v-else-if="done && !items.length" class="text-center text-sm text-gray-500 py-16">
        아직 프롬프트가 없어요
      </p>
    </main>
  </div>
</template>
