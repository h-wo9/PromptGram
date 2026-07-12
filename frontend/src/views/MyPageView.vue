<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  deletePrompt,
  fetchMyBookmarks,
  fetchMyPrompts,
  increaseCopyCount,
  toggleBookmark,
  toggleLike,
} from '../api/prompts'
import MasonryGrid from '../components/MasonryGrid.vue'
import PromptCard from '../components/PromptCard.vue'

const router = useRouter()
const auth = useAuthStore()

const tab = ref('mine')
const mine = ref([])
const saved = ref([])
const loading = ref(true)

const editingProfile = ref(false)
const nickname = ref('')
const bio = ref('')
const profileImageUrl = ref('')
const profileError = ref('')

async function load() {
  loading.value = true
  try {
    ;[mine.value, saved.value] = await Promise.all([
      fetchMyPrompts(),
      fetchMyBookmarks(),
    ])
  } finally {
    loading.value = false
  }
}

onMounted(load)

function startEditProfile() {
  nickname.value = auth.user?.nickname ?? ''
  bio.value = auth.user?.bio ?? ''
  profileImageUrl.value = auth.user?.profile_image_url ?? ''
  profileError.value = ''
  editingProfile.value = true
}

async function saveProfile() {
  try {
    await auth.updateProfile({
      nickname: nickname.value,
      bio: bio.value || null,
      profile_image_url: profileImageUrl.value || null,
    })
    editingProfile.value = false
  } catch (e) {
    const detail = e.response?.data?.detail
    profileError.value =
      typeof detail === 'string' ? detail : '입력값을 확인해주세요 (닉네임 2자 이상)'
  }
}

async function onLike(prompt) {
  Object.assign(prompt, await toggleLike(prompt.id))
}

async function onBookmark(prompt) {
  const data = await toggleBookmark(prompt.id)
  Object.assign(prompt, data)
  if (!data.is_bookmarked) saved.value = saved.value.filter((p) => p.id !== prompt.id)
}

async function onCopied(prompt) {
  try {
    Object.assign(prompt, await increaseCopyCount(prompt.id))
  } catch {
    /* 카운트 실패는 무시 */
  }
}

async function onRemove(prompt) {
  if (!confirm(`'${prompt.title}' 프롬프트를 삭제할까요?`)) return
  await deletePrompt(prompt.id)
  mine.value = mine.value.filter((p) => p.id !== prompt.id)
}

async function logout() {
  await auth.logout()
  router.push({ name: 'landing' })
}
</script>

<template>
  <div class="min-h-screen">
    <header class="sticky top-0 z-20 border-b border-white/10 bg-night/80 backdrop-blur-xl">
      <div class="max-w-6xl mx-auto px-4 h-14 flex items-center gap-4">
        <router-link to="/feed" class="text-lg font-extrabold tracking-tight">
          Prompt<span class="text-accent">Gram</span>
        </router-link>
        <span class="flex-1"></span>
        <router-link
          to="/write"
          class="rounded-lg bg-accent hover:bg-blue-500 transition-colors px-3.5 py-1.5 text-sm font-semibold"
        >
          + 글쓰기
        </router-link>
        <button class="text-sm text-gray-500 hover:text-white" @click="logout">로그아웃</button>
      </div>
    </header>

    <main class="max-w-6xl mx-auto px-4 py-8">
      <!-- 프로필 -->
      <section class="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div v-if="!editingProfile" class="flex items-center gap-4">
          <img
            v-if="auth.user?.profile_image_url"
            :src="auth.user.profile_image_url"
            alt=""
            class="w-16 h-16 rounded-full object-cover"
          />
          <div
            v-else
            class="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-purple-500 flex items-center justify-center text-xl font-bold"
          >
            {{ auth.user?.nickname?.[0] ?? '?' }}
          </div>
          <div class="min-w-0 flex-1">
            <h1 class="text-lg font-bold">{{ auth.user?.nickname }}</h1>
            <p class="text-sm text-gray-400 truncate">
              {{ auth.user?.bio || '한 줄 소개가 아직 없어요' }}
            </p>
          </div>
          <button
            class="rounded-lg border border-white/20 hover:border-accent hover:text-accent transition-colors px-3.5 py-1.5 text-sm"
            @click="startEditProfile"
          >
            프로필 수정
          </button>
        </div>

        <form v-else class="space-y-3" @submit.prevent="saveProfile">
          <div class="grid sm:grid-cols-2 gap-3">
            <input
              v-model="nickname"
              required
              minlength="2"
              maxlength="50"
              placeholder="닉네임"
              class="rounded-lg bg-white/5 border border-white/10 px-4 py-2.5 text-sm focus:border-accent focus:outline-none"
            />
            <input
              v-model="profileImageUrl"
              type="url"
              maxlength="500"
              placeholder="프로필 이미지 URL (선택)"
              class="rounded-lg bg-white/5 border border-white/10 px-4 py-2.5 text-sm focus:border-accent focus:outline-none"
            />
          </div>
          <input
            v-model="bio"
            maxlength="200"
            placeholder="한 줄 소개 (선택)"
            class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-2.5 text-sm focus:border-accent focus:outline-none"
          />
          <p v-if="profileError" class="text-sm text-red-400">{{ profileError }}</p>
          <div class="flex gap-2 justify-end">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-sm text-gray-400 hover:text-white"
              @click="editingProfile = false"
            >
              취소
            </button>
            <button
              type="submit"
              class="rounded-lg bg-accent hover:bg-blue-500 transition-colors px-4 py-2 text-sm font-semibold"
            >
              저장
            </button>
          </div>
        </form>
      </section>

      <!-- 탭 -->
      <div class="mt-8 flex gap-1 border-b border-white/10 text-sm font-medium">
        <button
          class="px-4 py-2.5 -mb-px border-b-2 transition-colors"
          :class="tab === 'mine' ? 'border-accent text-white' : 'border-transparent text-gray-500 hover:text-gray-300'"
          @click="tab = 'mine'"
        >
          내 프롬프트 ({{ mine.length }})
        </button>
        <button
          class="px-4 py-2.5 -mb-px border-b-2 transition-colors"
          :class="tab === 'saved' ? 'border-accent text-white' : 'border-transparent text-gray-500 hover:text-gray-300'"
          @click="tab = 'saved'"
        >
          스크랩 ({{ saved.length }})
        </button>
      </div>

      <div class="mt-6">
        <p v-if="loading" class="text-center text-sm text-gray-500 py-12">불러오는 중…</p>
        <template v-else>
          <MasonryGrid v-if="tab === 'mine'" :items="mine" v-slot="{ item }">
            <PromptCard
              :prompt="item"
              show-visibility
              editable
              @like="onLike"
              @bookmark="onBookmark"
              @copied="onCopied"
              @tag="(t) => router.push({ name: 'feed', query: { tag: t } })"
              @edit="(p) => router.push({ name: 'edit', params: { id: p.id } })"
              @remove="onRemove"
            />
          </MasonryGrid>
          <p v-if="tab === 'mine' && !mine.length" class="text-center text-sm text-gray-500 py-12">
            아직 쓴 프롬프트가 없어요 —
            <router-link to="/write" class="text-accent">첫 프롬프트를 남겨보세요</router-link>
          </p>

          <MasonryGrid v-if="tab === 'saved'" :items="saved" v-slot="{ item }">
            <PromptCard
              :prompt="item"
              @like="onLike"
              @bookmark="onBookmark"
              @copied="onCopied"
              @tag="(t) => router.push({ name: 'feed', query: { tag: t } })"
            />
          </MasonryGrid>
          <p v-if="tab === 'saved' && !saved.length" class="text-center text-sm text-gray-500 py-12">
            스크랩한 프롬프트가 없어요
          </p>
        </template>
      </div>
    </main>
  </div>
</template>
