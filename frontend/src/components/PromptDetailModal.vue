<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import gsap from 'gsap'
import { createComment, deleteComment, fetchComments, updateComment } from '../api/comments'
import { confirmDialog } from '../composables/confirm'
import { lockScroll, unlockScroll } from '../composables/scrollLock'
import { showToast } from '../composables/toast'
import { useAuthStore } from '../stores/auth'
import { splitVariableSegments } from '../utils/variables'
import { timeAgo } from '../utils/time'
import VariableFillPanel from './VariableFillPanel.vue'

const props = defineProps({
  prompt: { type: Object, required: true },
  // 클릭된 카드 element — 여기서부터 확대되는 FLIP 애니메이션의 출발점
  sourceEl: { type: Object, default: null },
})
const emit = defineEmits(['close', 'like', 'bookmark', 'copied'])

const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
const cardEl = ref(null)
const backdropEl = ref(null)
let closing = false

const segments = computed(() => splitVariableSegments(props.prompt.prompt_text))
const dateText = computed(() =>
  new Date(props.prompt.created_at).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
)

// ── 댓글 ──
const auth = useAuthStore()
const comments = ref([])
const commentsLoading = ref(true)
const newComment = ref('')
const posting = ref(false)
const editingId = ref(null)
const editText = ref('')

async function loadComments() {
  commentsLoading.value = true
  try {
    comments.value = await fetchComments(props.prompt.id)
  } finally {
    commentsLoading.value = false
  }
}

async function postComment() {
  const content = newComment.value.trim()
  if (!content || posting.value) return
  posting.value = true
  try {
    const created = await createComment(props.prompt.id, content)
    comments.value.unshift(created)
    newComment.value = ''
  } catch {
    showToast('댓글 등록에 실패했어요', 'error')
  } finally {
    posting.value = false
  }
}

function startEdit(comment) {
  editingId.value = comment.id
  editText.value = comment.content
}

async function saveEdit(comment) {
  const content = editText.value.trim()
  if (!content) return
  try {
    const updated = await updateComment(comment.id, content)
    Object.assign(comment, updated)
    editingId.value = null
  } catch {
    showToast('댓글 수정에 실패했어요', 'error')
  }
}

async function removeComment(comment) {
  const ok = await confirmDialog({
    title: '댓글을 삭제할까요?',
    confirmText: '삭제',
    danger: true,
  })
  if (!ok) return
  try {
    await deleteComment(comment.id)
    comments.value = comments.value.filter((c) => c.id !== comment.id)
    showToast('댓글이 삭제됐어요')
  } catch {
    showToast('댓글 삭제에 실패했어요', 'error')
  }
}

function flipFrom() {
  const from = props.sourceEl.getBoundingClientRect()
  const to = cardEl.value.getBoundingClientRect()
  return {
    x: from.left - to.left,
    y: from.top - to.top,
    scaleX: from.width / to.width,
    scaleY: from.height / to.height,
  }
}

onMounted(() => {
  lockScroll()
  window.addEventListener('keydown', onKey)
  loadComments()
  if (reduced || !props.sourceEl || !cardEl.value) return
  gsap.set(cardEl.value, { transformOrigin: 'top left', ...flipFrom(), opacity: 0.5 })
  gsap.to(cardEl.value, { x: 0, y: 0, scaleX: 1, scaleY: 1, opacity: 1, duration: 0.38, ease: 'power3.out' })
  gsap.fromTo(backdropEl.value, { opacity: 0 }, { opacity: 1, duration: 0.3 })
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKey)
  unlockScroll()
})

function close() {
  if (closing) return
  closing = true
  if (reduced || !props.sourceEl || !cardEl.value) {
    emit('close')
    return
  }
  // 원래 카드 위치로 되돌아가며 축소
  gsap.to(cardEl.value, {
    ...flipFrom(),
    opacity: 0.35,
    duration: 0.3,
    ease: 'power2.in',
    onComplete: () => emit('close'),
  })
  gsap.to(backdropEl.value, { opacity: 0, duration: 0.28 })
}

function onKey(e) {
  if (e.key === 'Escape') close()
}

// 게시자·댓글 작성자 클릭 → 프로필 페이지
const route = useRoute()
const router = useRouter()

function goProfile(userId) {
  emit('close')
  if (!(route.name === 'profile' && Number(route.params.id) === userId)) {
    router.push({ name: 'profile', params: { id: userId } })
  }
}
</script>

<template>
  <div class="fixed inset-0 z-[70] flex items-center justify-center px-4 py-8">
    <div ref="backdropEl" class="absolute inset-0 bg-black/70 light:bg-slate-900/40" @click="close"></div>

    <article
      ref="cardEl"
      class="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl border p-7 shadow-2xl
             border-white/15 bg-[#121218] light:border-slate-200 light:bg-white"
      role="dialog"
      aria-modal="true"
      :aria-label="prompt.title"
    >
      <button
        class="absolute top-4 right-4 w-8 h-8 rounded-full flex items-center justify-center text-gray-400 hover:text-white light:text-slate-400 light:hover:text-slate-900 transition-colors"
        aria-label="닫기"
        @click="close"
      >
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
        </svg>
      </button>

      <header class="flex items-center gap-3 pr-10">
        <button
          class="flex items-center gap-3 min-w-0 text-left group"
          :aria-label="`${prompt.author.nickname} 프로필 보기`"
          @click="goProfile(prompt.author.id)"
        >
          <img
            v-if="prompt.author.profile_image_url"
            :src="prompt.author.profile_image_url"
            alt=""
            class="w-10 h-10 rounded-full object-cover"
          />
          <div
            v-else
            class="w-10 h-10 rounded-full bg-gradient-to-br from-accent to-purple-500 flex items-center justify-center text-sm font-bold text-white"
          >
            {{ prompt.author.nickname[0] }}
          </div>
          <div class="min-w-0">
            <p class="text-sm font-semibold group-hover:text-accent transition-colors">{{ prompt.author.nickname }}</p>
            <p class="text-xs text-gray-500 light:text-slate-400">{{ dateText }}</p>
          </div>
        </button>
        <span class="flex-1"></span>
        <span
          v-if="prompt.ai_source"
          class="shrink-0 rounded-full bg-white/10 text-gray-300 light:bg-slate-900/[0.06] light:text-slate-600 px-3 py-1 text-xs"
        >
          {{ prompt.ai_source }}
        </span>
      </header>

      <h2 class="mt-5 text-xl font-bold leading-snug">{{ prompt.title }}</h2>

      <p class="mt-3 text-[15px] text-gray-300 light:text-slate-600 whitespace-pre-wrap break-words leading-relaxed">
        <template v-for="(seg, i) in segments" :key="i">
          <span v-if="seg.isVar" class="text-accent font-semibold">{{ seg.text }}</span>
          <template v-else>{{ seg.text }}</template>
        </template>
      </p>

      <div v-if="prompt.tags.length" class="mt-4 flex flex-wrap gap-1.5">
        <span
          v-for="t in prompt.tags"
          :key="t"
          class="rounded-full bg-accent/10 text-accent/90 px-2.5 py-0.5 text-xs"
        >
          #{{ t }}
        </span>
      </div>

      <div v-if="prompt.ai_response" class="mt-5 rounded-xl border border-white/10 bg-white/[0.03] light:border-slate-200 light:bg-slate-50 p-4">
        <p class="text-[11px] font-semibold text-gray-500 light:text-slate-400 mb-2">AI 응답 결과</p>
        <p class="text-sm text-gray-400 light:text-slate-500 whitespace-pre-wrap break-words leading-relaxed">{{ prompt.ai_response }}</p>
      </div>

      <footer class="mt-6 flex items-center gap-5 text-sm text-gray-400 light:text-slate-500 border-t border-white/10 light:border-slate-200 pt-4">
        <button
          class="flex items-center gap-1.5 transition-colors"
          :class="prompt.is_liked ? 'text-red-400' : 'hover:text-red-400'"
          :aria-label="prompt.is_liked ? '좋아요 취소' : '좋아요'"
          @click="emit('like', prompt)"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" :fill="prompt.is_liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
          </svg>
          {{ prompt.like_count }}
        </button>
        <button
          class="flex items-center gap-1.5 transition-colors"
          :class="prompt.is_bookmarked ? 'text-accent' : 'hover:text-accent'"
          :aria-label="prompt.is_bookmarked ? '스크랩 취소' : '스크랩'"
          @click="emit('bookmark', prompt)"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" :fill="prompt.is_bookmarked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c.1.128.176.27.223.42.047.15.07.308.066.466v16.542a.75.75 0 0 1-1.184.611L12 18.443l-4.698 3.918a.75.75 0 0 1-1.184-.61V4.207c-.005-.158.019-.316.066-.466.047-.15.123-.292.223-.42C6.85 2.75 7.4 2.5 8 2.5h8c.6 0 1.15.25 1.593.822Z" />
          </svg>
          {{ prompt.bookmark_count }}
        </button>
        <span class="flex items-center gap-1.5" title="복사된 횟수">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
          </svg>
          {{ prompt.copy_count }}
        </span>
      </footer>

      <div class="mt-4">
        <VariableFillPanel
          :prompt-text="prompt.prompt_text"
          :variables="prompt.variables"
          @copied="emit('copied', prompt)"
        />
      </div>

      <!-- ── 댓글 ── -->
      <section class="mt-7 border-t border-white/10 light:border-slate-200 pt-5">
        <h3 class="text-sm font-bold">
          댓글 <span class="text-gray-500 light:text-slate-400">{{ comments.length }}</span>
        </h3>

        <!-- 입력 -->
        <form v-if="auth.isLoggedIn" class="mt-3 flex gap-2" @submit.prevent="postComment">
          <input
            v-model="newComment"
            maxlength="500"
            placeholder="댓글을 남겨보세요"
            class="flex-1 rounded-lg bg-white/5 border border-white/10 light:bg-white light:border-slate-300 px-3.5 py-2.5 text-sm focus:border-accent focus:outline-none"
          />
          <button
            type="submit"
            :disabled="posting || !newComment.trim()"
            class="rounded-lg bg-accent hover:bg-blue-500 transition-colors px-4 py-2 text-sm font-semibold text-white disabled:opacity-40"
          >
            등록
          </button>
        </form>
        <p v-else class="mt-3 text-sm text-gray-500 light:text-slate-400">
          <router-link to="/auth" class="text-accent hover:underline">로그인</router-link>하고 댓글을 남겨보세요
        </p>

        <!-- 목록 -->
        <p v-if="commentsLoading" class="mt-4 text-sm text-gray-500 light:text-slate-400">댓글 불러오는 중…</p>
        <ul v-else-if="comments.length" class="mt-4 space-y-4">
          <li v-for="c in comments" :key="c.id" class="flex gap-2.5">
            <button
              class="w-7 h-7 shrink-0 rounded-full bg-gradient-to-br from-accent to-purple-500 flex items-center justify-center text-[11px] font-bold text-white"
              :aria-label="`${c.author.nickname} 프로필 보기`"
              @click="goProfile(c.author.id)"
            >
              {{ c.author.nickname[0] }}
            </button>
            <div class="min-w-0 flex-1">
              <p class="text-xs text-gray-400 light:text-slate-500">
                <button
                  class="font-semibold text-gray-200 light:text-slate-700 hover:text-accent light:hover:text-accent transition-colors"
                  @click="goProfile(c.author.id)"
                >
                  {{ c.author.nickname }}
                </button>
                · {{ timeAgo(c.created_at) }}
                <span v-if="c.updated_at" class="text-gray-600 light:text-slate-400">(수정됨)</span>
              </p>

              <template v-if="editingId === c.id">
                <input
                  v-model="editText"
                  maxlength="500"
                  class="mt-1.5 w-full rounded-lg bg-white/5 border border-white/10 light:bg-white light:border-slate-300 px-3 py-2 text-sm focus:border-accent focus:outline-none"
                  @keydown.enter.prevent="saveEdit(c)"
                  @keydown.esc="editingId = null"
                />
                <div class="mt-1.5 flex gap-2 text-xs">
                  <button class="text-accent font-semibold" @click="saveEdit(c)">저장</button>
                  <button class="text-gray-500 hover:text-gray-300 light:hover:text-slate-700" @click="editingId = null">취소</button>
                </div>
              </template>
              <p v-else class="mt-1 text-sm text-gray-300 light:text-slate-600 whitespace-pre-wrap break-words">
                {{ c.content }}
              </p>
            </div>

            <div
              v-if="auth.user && c.author.id === auth.user.id && editingId !== c.id"
              class="shrink-0 flex gap-2 text-xs text-gray-500"
            >
              <button class="hover:text-white light:hover:text-slate-900" @click="startEdit(c)">수정</button>
              <button class="hover:text-red-400" @click="removeComment(c)">삭제</button>
            </div>
          </li>
        </ul>
        <p v-else class="mt-4 text-sm text-gray-600 light:text-slate-400">첫 댓글을 남겨보세요</p>
      </section>
    </article>
  </div>
</template>
