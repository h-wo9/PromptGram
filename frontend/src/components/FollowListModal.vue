<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { fetchFollowers, fetchFollowing } from '../api/users'

const props = defineProps({
  userId: { type: Number, required: true },
  type: { type: String, required: true }, // 'followers' | 'following'
})
const emit = defineEmits(['close', 'navigate'])

const users = ref([])
const loading = ref(true)

onMounted(async () => {
  window.addEventListener('keydown', onKey)
  try {
    users.value =
      props.type === 'followers'
        ? await fetchFollowers(props.userId)
        : await fetchFollowing(props.userId)
  } finally {
    loading.value = false
  }
})
onUnmounted(() => window.removeEventListener('keydown', onKey))

function onKey(e) {
  if (e.key === 'Escape') emit('close')
}
</script>

<template>
  <div class="fixed inset-0 z-[75] flex items-center justify-center px-6 bg-black/60" @click.self="emit('close')">
    <div
      role="dialog"
      aria-modal="true"
      :aria-label="type === 'followers' ? '팔로워' : '팔로잉'"
      class="w-full max-w-xs max-h-[70vh] overflow-y-auto rounded-2xl border p-5 shadow-2xl
             border-white/15 bg-night/95 light:border-slate-200 light:bg-white"
    >
      <div class="flex items-center justify-between">
        <h2 class="font-bold text-sm">{{ type === 'followers' ? '팔로워' : '팔로잉' }}</h2>
        <button
          class="text-gray-500 hover:text-white light:hover:text-slate-900"
          aria-label="닫기"
          @click="emit('close')"
        >
          ✕
        </button>
      </div>

      <p v-if="loading" class="mt-4 text-sm text-gray-500">불러오는 중…</p>
      <ul v-else-if="users.length" class="mt-3 space-y-1">
        <li v-for="u in users" :key="u.id">
          <button
            class="w-full flex items-center gap-2.5 rounded-lg px-2 py-2 hover:bg-white/5 light:hover:bg-slate-100 transition-colors text-left"
            @click="emit('navigate', u.id)"
          >
            <img
              v-if="u.profile_image_url"
              :src="u.profile_image_url"
              alt=""
              class="w-8 h-8 rounded-full object-cover"
            />
            <div
              v-else
              class="w-8 h-8 rounded-full bg-gradient-to-br from-accent to-purple-500 flex items-center justify-center text-xs font-bold text-white"
            >
              {{ u.nickname[0] }}
            </div>
            <span class="text-sm font-medium truncate">{{ u.nickname }}</span>
          </button>
        </li>
      </ul>
      <p v-else class="mt-4 text-sm text-gray-500 light:text-slate-400">
        {{ type === 'followers' ? '아직 팔로워가 없어요' : '아직 팔로잉하는 사람이 없어요' }}
      </p>
    </div>
  </div>
</template>
