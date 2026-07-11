<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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
