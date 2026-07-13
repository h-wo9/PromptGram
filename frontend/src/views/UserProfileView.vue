<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { increaseCopyCount, toggleBookmark, toggleLike } from '../api/prompts'
import { fetchUserProfile, fetchUserPrompts, toggleFollow } from '../api/users'
import { showToast } from '../composables/toast'
import AuroraBackground from '../components/AuroraBackground.vue'
import FollowListModal from '../components/FollowListModal.vue'
import MasonryGrid from '../components/MasonryGrid.vue'
import PromptCard from '../components/PromptCard.vue'
import PromptDetailModal from '../components/PromptDetailModal.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import ThemeToggle from '../components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const profile = ref(null)
const prompts = ref([])
const loading = ref(true)
const notFound = ref(false)
const detail = ref(null)
const followList = ref(null) // 'followers' | 'following'
const followBusy = ref(false)

const isMe = computed(() => auth.user && profile.value && auth.user.id === profile.value.id)

async function load(id) {
  loading.value = true
  notFound.value = false
  followList.value = null
  detail.value = null
  try {
    ;[profile.value, prompts.value] = await Promise.all([
      fetchUserProfile(id),
      fetchUserPrompts(id),
    ])
  } catch (e) {
    if (e.response?.status === 404) notFound.value = true
  } finally {
    loading.value = false
  }
}

onMounted(() => load(Number(route.params.id)))
// 팔로워 목록에서 다른 프로필로 이동하는 경우 등 같은 컴포넌트 재사용 대응
watch(
  () => route.params.id,
  (id) => {
    if (route.name === 'profile' && id) load(Number(id))
  }
)

function requireAuth() {
  if (!auth.isLoggedIn) {
    router.push({ name: 'auth' })
    return false
  }
  return true
}

async function onFollow() {
  if (!requireAuth() || followBusy.value) return
  followBusy.value = true
  try {
    const data = await toggleFollow(profile.value.id)
    profile.value.is_following = data.is_following
    profile.value.follower_count = data.follower_count
  } catch {
    showToast('팔로우 처리에 실패했어요', 'error')
  } finally {
    followBusy.value = false
  }
}

function goProfile(id) {
  followList.value = null
  if (Number(route.params.id) !== id) router.push({ name: 'profile', params: { id } })
}

// 카드 상호작용 (낙관적 업데이트 — 피드와 동일 패턴)
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
    Object.assign(prompt, await increaseCopyCount(prompt.id))
  } catch {
    /* 카운트 실패는 무시 */
  }
}

async function logout() {
  await auth.logout()
  router.push({ name: 'landing' })
}
</script>

<template>
  <div class="min-h-screen">
    <AuroraBackground />
    <header class="sticky top-0 z-20 border-b border-white/10 bg-night/80 backdrop-blur-xl light:border-slate-200 light:bg-white light:backdrop-blur-none">
      <div class="max-w-6xl mx-auto px-4 h-14 flex items-center gap-4">
        <router-link to="/feed" class="text-lg font-extrabold tracking-tight">
          Prompt<span class="text-accent">Gram</span>
        </router-link>
        <span class="flex-1"></span>
        <ThemeToggle />
        <template v-if="auth.isLoggedIn">
          <router-link to="/write" class="btn-grad rounded-lg px-3.5 py-1.5 text-sm font-semibold text-white">
            + 글쓰기
          </router-link>
          <router-link
            to="/me"
            class="text-sm text-gray-300 hover:text-white light:text-slate-600 light:hover:text-slate-900"
          >
            마이페이지
          </router-link>
          <button class="text-sm text-gray-500 hover:text-white light:hover:text-slate-900" @click="logout">
            로그아웃
          </button>
        </template>
        <router-link
          v-else
          to="/auth"
          class="rounded-lg bg-accent hover:bg-blue-500 transition-colors px-3.5 py-1.5 text-sm font-semibold text-white"
        >
          시작하기
        </router-link>
      </div>
    </header>

    <main class="relative z-10 max-w-6xl mx-auto px-4 py-8">
      <p v-if="notFound" class="text-center text-sm text-gray-500 py-24">존재하지 않는 사용자예요</p>

      <template v-else-if="profile">
        <!-- 프로필 카드 -->
        <section class="rounded-2xl border border-white/10 bg-white/[0.04] light:border-slate-200 light:bg-white backdrop-blur-sm light:backdrop-blur-none p-6 shadow-[0_12px_50px_rgba(40,60,180,0.1)]">
          <div class="flex items-center gap-4">
            <img
              v-if="profile.profile_image_url"
              :src="profile.profile_image_url"
              alt=""
              class="w-16 h-16 rounded-full object-cover"
            />
            <div
              v-else
              class="w-16 h-16 rounded-full bg-gradient-to-br from-accent to-purple-500 flex items-center justify-center text-xl font-bold text-white shadow-[0_0_22px_rgba(80,90,245,0.4)]"
            >
              {{ profile.nickname[0] }}
            </div>
            <div class="min-w-0 flex-1">
              <h1 class="text-lg font-bold">{{ profile.nickname }}</h1>
              <p class="text-sm text-gray-400 light:text-slate-500 truncate">
                {{ profile.bio || '한 줄 소개가 아직 없어요' }}
              </p>
              <div class="mt-1.5 flex gap-4 text-sm">
                <button class="hover:text-accent transition-colors" @click="followList = 'followers'">
                  팔로워 <strong>{{ profile.follower_count }}</strong>
                </button>
                <button class="hover:text-accent transition-colors" @click="followList = 'following'">
                  팔로잉 <strong>{{ profile.following_count }}</strong>
                </button>
              </div>
            </div>
            <router-link
              v-if="isMe"
              to="/me"
              class="rounded-lg border border-white/20 light:border-slate-300 hover:border-accent hover:text-accent transition-colors px-3.5 py-1.5 text-sm"
            >
              마이페이지
            </router-link>
            <button
              v-else
              :disabled="followBusy"
              class="rounded-lg px-4 py-1.5 text-sm font-semibold transition-colors"
              :class="profile.is_following
                ? 'border border-white/20 light:border-slate-300 text-gray-300 light:text-slate-600 hover:border-red-400 hover:text-red-400'
                : 'btn-grad text-white'"
              @click="onFollow"
            >
              {{ profile.is_following ? '팔로잉' : '팔로우' }}
            </button>
          </div>
        </section>

        <!-- 공개 프롬프트 -->
        <h2 class="mt-8 text-sm font-bold text-gray-300 light:text-slate-600">
          공개 프롬프트 <span class="text-gray-500 light:text-slate-400">{{ prompts.length }}</span>
        </h2>
        <div class="mt-4">
          <MasonryGrid v-if="loading" :items="[1, 2, 3].map((id) => ({ id }))" v-slot="{ item }">
            <SkeletonCard :lines="(item.id % 3) + 2" />
          </MasonryGrid>
          <MasonryGrid v-else-if="prompts.length" :items="prompts" v-slot="{ item }">
            <PromptCard
              :prompt="item"
              @like="onLike"
              @bookmark="onBookmark"
              @copied="onCopied"
              @tag="(t) => router.push({ name: 'feed', query: { tag: t } })"
              @open="detail = $event"
            />
          </MasonryGrid>
          <p v-else class="text-center text-sm text-gray-500 light:text-slate-400 py-12">
            아직 공개한 프롬프트가 없어요
          </p>
        </div>
      </template>
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
    <FollowListModal
      v-if="followList"
      :user-id="profile.id"
      :type="followList"
      @close="followList = null"
      @navigate="goProfile"
    />
  </div>
</template>
