<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { suggestTags, tunePrompt } from '../api/ai'
import { createPrompt, getPrompt, updatePrompt } from '../api/prompts'
import { parseVariables } from '../utils/variables'

const route = useRoute()
const router = useRouter()
const editId = route.params.id ? Number(route.params.id) : null

const title = ref('')
const promptText = ref('')
const aiResponse = ref('')
const aiSource = ref('')
const tagInput = ref('')
const isPublic = ref(true)
const error = ref('')
const loading = ref(false)

const variables = computed(() => parseVariables(promptText.value))

// ── AI 다듬기 (개선 '제안' — 정답 아님) ──
const tuning = ref(false)
const tuneResult = ref(null) // { before, improved_prompt, reasons }
const aiError = ref('')

async function runTune() {
  if (promptText.value.trim().length < 5) return
  aiError.value = ''
  tuning.value = true
  try {
    const data = await tunePrompt(promptText.value)
    tuneResult.value = { before: promptText.value, ...data }
  } catch (e) {
    aiError.value = e.response?.status === 429
      ? 'AI 요청이 너무 잦아요. 잠시 후 다시 시도해주세요.'
      : 'AI 다듬기에 실패했어요. 잠시 후 다시 시도해주세요.'
  } finally {
    tuning.value = false
  }
}

function applyTune() {
  promptText.value = tuneResult.value.improved_prompt
  tuneResult.value = null
}

// ── AI 태그 추천: chip을 눌러 선택 ──
const suggesting = ref(false)
const suggestedTags = ref([])

async function runSuggestTags() {
  if (promptText.value.trim().length < 5) return
  aiError.value = ''
  suggesting.value = true
  try {
    const data = await suggestTags(promptText.value)
    suggestedTags.value = data.tags
  } catch (e) {
    aiError.value = e.response?.status === 429
      ? 'AI 요청이 너무 잦아요. 잠시 후 다시 시도해주세요.'
      : '태그 추천에 실패했어요. 잠시 후 다시 시도해주세요.'
  } finally {
    suggesting.value = false
  }
}

function toggleSuggestedTag(tag) {
  const current = tags.value
  if (current.includes(tag)) {
    tagInput.value = current.filter((t) => t !== tag).map((t) => `#${t}`).join(' ')
  } else {
    tagInput.value = [...current, tag].map((t) => `#${t}`).join(' ')
  }
}
const tags = computed(() =>
  tagInput.value
    .split(/[,\s]+/)
    .map((t) => t.replace(/^#/, '').trim())
    .filter(Boolean)
    .slice(0, 10)
)

onMounted(async () => {
  if (!editId) return
  const p = await getPrompt(editId)
  title.value = p.title
  promptText.value = p.prompt_text
  aiResponse.value = p.ai_response ?? ''
  aiSource.value = p.ai_source ?? ''
  tagInput.value = p.tags.map((t) => `#${t}`).join(' ')
  isPublic.value = p.is_public
})

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const payload = {
      title: title.value,
      prompt_text: promptText.value,
      ai_response: aiResponse.value || null,
      ai_source: aiSource.value || null,
      tags: tags.value,
      is_public: isPublic.value,
    }
    if (editId) await updatePrompt(editId, payload)
    else await createPrompt(payload)
    router.push({ name: 'feed' })
  } catch (e) {
    const detail = e.response?.data?.detail
    error.value = typeof detail === 'string' ? detail : '입력값을 확인해주세요.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen max-w-2xl mx-auto px-4 py-10">
    <div class="flex items-center justify-between">
      <h1 class="text-xl font-bold">{{ editId ? '프롬프트 수정' : '새 프롬프트' }}</h1>
      <router-link to="/feed" class="text-sm text-gray-400 hover:text-white">← 피드로</router-link>
    </div>

    <form class="mt-6 space-y-4" @submit.prevent="submit">
      <input
        v-model="title"
        required
        maxlength="100"
        placeholder="제목"
        class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-sm focus:border-accent focus:outline-none"
      />
      <div>
        <textarea
          v-model="promptText"
          required
          maxlength="5000"
          rows="7"
          placeholder="프롬프트 본문 — [변수명] 문법으로 재사용 변수를 지정할 수 있어요"
          class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-sm focus:border-accent focus:outline-none"
        ></textarea>
        <div v-if="variables.length" class="mt-2 flex flex-wrap gap-2">
          <span class="text-xs text-gray-400 self-center">감지된 변수:</span>
          <span
            v-for="v in variables"
            :key="v"
            class="rounded-full bg-accent/20 text-accent border border-accent/40 px-2.5 py-0.5 text-xs font-medium"
          >
            [{{ v }}]
          </span>
        </div>

        <div class="mt-2 flex gap-2">
          <button
            type="button"
            :disabled="tuning || promptText.trim().length < 5"
            class="ai-tune-btn rounded-lg px-3.5 py-1.5 text-xs font-semibold text-white disabled:opacity-40"
            @click="runTune"
          >
            {{ tuning ? '✦ AI가 다듬는 중…' : '✦ AI 다듬기' }}
          </button>
          <button
            type="button"
            :disabled="suggesting || promptText.trim().length < 5"
            class="rounded-lg border border-white/20 text-gray-300 hover:border-accent hover:text-accent transition-colors px-3 py-1.5 text-xs font-semibold disabled:opacity-40"
            @click="runSuggestTags"
          >
            {{ suggesting ? '태그 추천 중…' : '태그 추천' }}
          </button>
        </div>
        <p v-if="aiError" class="mt-2 text-xs text-red-400">{{ aiError }}</p>

        <!-- AI 개선 제안 (before / after + 이유) -->
        <div
          v-if="tuneResult"
          class="mt-3 rounded-xl border border-accent/30 bg-accent/5 p-4 space-y-3"
        >
          <p class="text-xs font-semibold text-accent">AI 개선 제안 — 정답이 아닌 제안이에요</p>
          <div class="grid sm:grid-cols-2 gap-3 text-xs">
            <div>
              <p class="text-gray-500 mb-1">Before</p>
              <p class="whitespace-pre-wrap break-words text-gray-400 rounded-lg bg-white/5 p-2.5">{{ tuneResult.before }}</p>
            </div>
            <div>
              <p class="text-gray-500 mb-1">After (제안)</p>
              <p class="whitespace-pre-wrap break-words text-gray-100 rounded-lg bg-white/5 p-2.5">{{ tuneResult.improved_prompt }}</p>
            </div>
          </div>
          <ul class="text-xs text-gray-400 space-y-1 list-disc list-inside">
            <li v-for="(r, i) in tuneResult.reasons" :key="i">{{ r }}</li>
          </ul>
          <div class="flex gap-2 justify-end">
            <button type="button" class="px-3 py-1.5 text-xs text-gray-400 hover:text-white" @click="tuneResult = null">
              닫기
            </button>
            <button
              type="button"
              class="rounded-lg bg-accent hover:bg-blue-500 transition-colors px-3 py-1.5 text-xs font-semibold"
              @click="applyTune"
            >
              제안 적용
            </button>
          </div>
        </div>

        <!-- AI 추천 태그 chip -->
        <div v-if="suggestedTags.length" class="mt-3 flex flex-wrap items-center gap-2">
          <span class="text-xs text-gray-400">추천 태그 (눌러서 선택):</span>
          <button
            v-for="t in suggestedTags"
            :key="t"
            type="button"
            class="rounded-full px-2.5 py-0.5 text-xs border transition-colors"
            :class="tags.includes(t)
              ? 'bg-accent text-white border-accent'
              : 'bg-white/5 text-gray-300 border-white/15 hover:border-accent hover:text-accent'"
            @click="toggleSuggestedTag(t)"
          >
            #{{ t }}
          </button>
        </div>
      </div>
      <textarea
        v-model="aiResponse"
        rows="4"
        maxlength="20000"
        placeholder="AI 응답 결과 (선택)"
        class="w-full rounded-lg bg-white/5 border border-white/10 px-4 py-3 text-sm focus:border-accent focus:outline-none"
      ></textarea>
      <div class="flex gap-3">
        <select
          v-model="aiSource"
          class="rounded-lg bg-white/5 border border-white/10 px-3 py-2.5 text-sm focus:border-accent focus:outline-none [&>option]:bg-base"
        >
          <option value="">대상 모델 (선택)</option>
          <option>ChatGPT</option>
          <option>Claude</option>
          <option>Gemini</option>
          <option>기타</option>
        </select>
        <input
          v-model="tagInput"
          placeholder="#태그 공백/쉼표 구분 (최대 10개)"
          class="flex-1 rounded-lg bg-white/5 border border-white/10 px-4 py-2.5 text-sm focus:border-accent focus:outline-none"
        />
      </div>
      <label class="flex items-center gap-2 text-sm text-gray-300">
        <input v-model="isPublic" type="checkbox" class="accent-accent w-4 h-4" />
        공개 (끄면 나만 볼 수 있어요)
      </label>
      <p v-if="error" class="text-sm text-red-400">{{ error }}</p>
      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded-lg bg-accent hover:bg-blue-500 transition-colors py-3 font-semibold disabled:opacity-50"
      >
        {{ editId ? '수정하기' : '게시하기' }}
      </button>
    </form>
  </div>
</template>

<style scoped>
/* AI 다듬기 — blue↔purple 그라데이션이 천천히 흐르는 시그니처 버튼 */
.ai-tune-btn {
  background: linear-gradient(115deg, #0070f3, #7c3aed, #0070f3);
  background-size: 220% 100%;
  animation: ai-flow 5s ease-in-out infinite;
  box-shadow: 0 0 14px rgba(100, 80, 245, 0.28);
  transition: box-shadow 0.3s ease;
}
.ai-tune-btn:hover:not(:disabled) {
  box-shadow: 0 0 24px rgba(110, 75, 250, 0.5);
}
@keyframes ai-flow {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
@media (prefers-reduced-motion: reduce) {
  .ai-tune-btn {
    animation: none;
  }
}
</style>
