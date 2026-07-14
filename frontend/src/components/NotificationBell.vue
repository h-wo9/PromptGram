<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchNotifications, readAllNotifications, readNotification } from '../api/notifications'
import { timeAgo } from '../utils/time'

const emit = defineEmits(['open-prompt'])

const router = useRouter()
const open = ref(false)
const items = ref([])
const loading = ref(true)
const rootEl = ref(null)

const hasUnread = computed(() => items.value.some((n) => !n.is_read))

const MESSAGES = {
  follow: (n) => `${n.actor.nickname}님이 회원님을 팔로우했어요`,
  new_prompt: (n) => `${n.actor.nickname}님이 새 프롬프트를 올렸어요`,
  comment: (n) => `${n.actor.nickname}님이 회원님의 글에 댓글을 남겼어요`,
}

async function load() {
  loading.value = true
  try {
    items.value = await fetchNotifications()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  load()
  window.addEventListener('click', onOutside)
})
onUnmounted(() => window.removeEventListener('click', onOutside))

function onOutside(e) {
  if (open.value && rootEl.value && !rootEl.value.contains(e.target)) open.value = false
}

async function onItemClick(n) {
  if (!n.is_read) {
    n.is_read = true
    readNotification(n.id).catch(() => {})
  }
  open.value = false
  if (n.type === 'follow') {
    router.push({ name: 'profile', params: { id: n.actor.id } })
  } else if (n.prompt_id) {
    emit('open-prompt', n.prompt_id)
  }
}

async function onReadAll() {
  items.value.forEach((n) => (n.is_read = true))
  readAllNotifications().catch(() => {})
}
</script>

<template>
  <div ref="rootEl" class="relative">
    <button
      class="relative w-8 h-8 rounded-full border border-white/15 text-gray-300 light:border-slate-300 light:text-slate-600 hover:border-accent hover:text-accent transition-colors flex items-center justify-center"
      :aria-label="hasUnread ? '알림 (읽지 않음 있음)' : '알림'"
      @click="open = !open"
    >
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
      </svg>
      <!-- 미읽음 표시: 종 옆 빨간 점 -->
      <span
        v-if="hasUnread"
        class="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full bg-red-500 border-2 border-night light:border-white"
        aria-hidden="true"
      ></span>
    </button>

    <Transition name="bell">
      <div
        v-if="open"
        class="absolute right-0 top-full mt-2 w-80 max-h-[26rem] overflow-y-auto rounded-2xl border p-2 shadow-2xl z-30
               border-white/15 bg-night/95 backdrop-blur-md light:border-slate-200 light:bg-white light:backdrop-blur-none"
      >
        <div class="flex items-center justify-between px-2.5 py-1.5">
          <h3 class="text-sm font-bold">알림</h3>
          <button
            v-if="hasUnread"
            class="text-xs text-accent hover:underline underline-offset-2"
            @click="onReadAll"
          >
            모두 읽음
          </button>
        </div>

        <p v-if="loading" class="px-2.5 py-4 text-sm text-gray-500">불러오는 중…</p>
        <ul v-else-if="items.length" class="space-y-0.5">
          <li v-for="n in items" :key="n.id">
            <button
              class="w-full flex items-start gap-2.5 rounded-xl px-2.5 py-2.5 text-left hover:bg-white/5 light:hover:bg-slate-100 transition-colors"
              @click="onItemClick(n)"
            >
              <span
                class="w-8 h-8 shrink-0 rounded-full bg-gradient-to-br from-accent to-purple-500 flex items-center justify-center text-xs font-bold text-white"
              >
                {{ n.actor.nickname[0] }}
              </span>
              <span class="min-w-0 flex-1">
                <span class="block text-[13px] leading-snug" :class="n.is_read ? 'text-gray-400 light:text-slate-500' : 'text-gray-100 light:text-slate-800 font-medium'">
                  {{ MESSAGES[n.type]?.(n) ?? '알림' }}
                </span>
                <span v-if="n.prompt_title" class="block text-xs text-gray-500 light:text-slate-400 truncate">
                  "{{ n.prompt_title }}"
                </span>
                <span class="block mt-0.5 text-[11px] text-gray-600 light:text-slate-400">{{ timeAgo(n.created_at) }}</span>
              </span>
              <!-- 미읽음: 항목 빨간 점 -->
              <span v-if="!n.is_read" class="mt-1.5 w-2 h-2 shrink-0 rounded-full bg-red-500" aria-hidden="true"></span>
            </button>
          </li>
        </ul>
        <p v-else class="px-2.5 py-6 text-center text-sm text-gray-500 light:text-slate-400">
          아직 알림이 없어요
        </p>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.bell-enter-active,
.bell-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.bell-enter-from,
.bell-leave-to {
  opacity: 0;
  transform: translateY(-6px) scale(0.98);
}
@media (prefers-reduced-motion: reduce) {
  .bell-enter-from,
  .bell-leave-to {
    transform: none;
  }
}
</style>
