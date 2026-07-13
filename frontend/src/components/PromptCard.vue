<script setup>
import { computed, nextTick, ref } from 'vue'
import ShareCard from './ShareCard.vue'
import VariableFillPanel from './VariableFillPanel.vue'

const props = defineProps({
  prompt: { type: Object, required: true },
  showVisibility: { type: Boolean, default: false },
  editable: { type: Boolean, default: false },
})
const emit = defineEmits(['like', 'bookmark', 'copied', 'tag', 'edit', 'remove'])

const showCopy = ref(false)
const justCopied = ref(false)

const segments = computed(() => {
  const parts = []
  const regex = /\[([^\[\]\n]{1,50})\]/g
  let last = 0
  for (const m of props.prompt.prompt_text.matchAll(regex)) {
    if (m.index > last) parts.push({ text: props.prompt.prompt_text.slice(last, m.index), isVar: false })
    parts.push({ text: m[0], isVar: true })
    last = m.index + m[0].length
  }
  if (last < props.prompt.prompt_text.length)
    parts.push({ text: props.prompt.prompt_text.slice(last), isVar: false })
  return parts
})

function onCopied() {
  justCopied.value = true
  setTimeout(() => (justCopied.value = false), 1500)
  emit('copied', props.prompt)
}

// 카드 이미지 다운로드: 공유용 ShareCard를 화면 밖에 렌더해 html2canvas로 캡처
const capturing = ref(false)
const shareEl = ref(null)

async function downloadImage() {
  if (capturing.value) return
  capturing.value = true
  try {
    await nextTick()
    await document.fonts.ready
    const { default: html2canvas } = await import('html2canvas')
    const canvas = await html2canvas(shareEl.value, {
      backgroundColor: '#0A0A0A',
      scale: 2,
    })
    const a = document.createElement('a')
    a.href = canvas.toDataURL('image/png')
    a.download = `promptgram-${props.prompt.id}.png`
    a.click()
  } finally {
    capturing.value = false
  }
}
</script>

<template>
  <article
    class="rounded-2xl border border-white/10 bg-white/[0.04] light:border-slate-200 light:bg-white light:backdrop-blur-none backdrop-blur-sm p-5 transition-[border-color,box-shadow,transform] duration-300 hover:border-accent/35 hover:-translate-y-0.5 hover:shadow-[0_10px_36px_rgba(50,80,220,0.16)] motion-reduce:transition-none motion-reduce:hover:translate-y-0"
  >
    <header class="flex items-center gap-2.5">
      <img
        v-if="prompt.author.profile_image_url"
        :src="prompt.author.profile_image_url"
        alt=""
        class="w-8 h-8 rounded-full object-cover"
      />
      <div
        v-else
        class="w-8 h-8 rounded-full bg-gradient-to-br from-accent to-purple-500 flex items-center justify-center text-xs font-bold"
      >
        {{ prompt.author.nickname[0] }}
      </div>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium truncate">{{ prompt.author.nickname }}</p>
      </div>
      <span
        v-if="prompt.ai_source"
        class="shrink-0 rounded-full bg-white/10 text-gray-300 light:bg-slate-900/[0.06] light:text-slate-600 px-2.5 py-0.5 text-[11px]"
      >
        {{ prompt.ai_source }}
      </span>
      <span
        v-if="showVisibility && !prompt.is_public"
        class="shrink-0 rounded-full bg-yellow-500/20 text-yellow-300 px-2.5 py-0.5 text-[11px]"
      >
        비공개
      </span>
    </header>

    <h3 class="mt-3 font-bold leading-snug">{{ prompt.title }}</h3>

    <p class="mt-2 text-sm text-gray-300 light:text-slate-600 whitespace-pre-wrap break-words leading-relaxed">
      <template v-for="(seg, i) in segments" :key="i">
        <span v-if="seg.isVar" class="text-accent font-semibold">{{ seg.text }}</span>
        <template v-else>{{ seg.text }}</template>
      </template>
    </p>

    <div v-if="prompt.tags.length" class="mt-3 flex flex-wrap gap-1.5">
      <button
        v-for="t in prompt.tags"
        :key="t"
        class="rounded-full bg-accent/10 text-accent/90 hover:bg-accent/25 transition-colors px-2.5 py-0.5 text-xs"
        @click="emit('tag', t)"
      >
        #{{ t }}
      </button>
    </div>

    <footer class="mt-4 flex items-center gap-4 text-sm text-gray-400 light:text-slate-500">
      <button
        class="flex items-center gap-1 transition-colors"
        :class="prompt.is_liked ? 'text-red-400' : 'hover:text-red-400'"
        :aria-label="prompt.is_liked ? '좋아요 취소' : '좋아요'"
        @click="emit('like', prompt)"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" :fill="prompt.is_liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12Z" />
        </svg>
        {{ prompt.like_count }}
      </button>
      <button
        class="flex items-center gap-1 transition-colors"
        :class="prompt.is_bookmarked ? 'text-accent' : 'hover:text-accent'"
        :aria-label="prompt.is_bookmarked ? '스크랩 취소' : '스크랩'"
        @click="emit('bookmark', prompt)"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" :fill="prompt.is_bookmarked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17.593 3.322c.1.128.176.27.223.42.047.15.07.308.066.466v16.542a.75.75 0 0 1-1.184.611L12 18.443l-4.698 3.918a.75.75 0 0 1-1.184-.61V4.207c-.005-.158.019-.316.066-.466.047-.15.123-.292.223-.42C6.85 2.75 7.4 2.5 8 2.5h8c.6 0 1.15.25 1.593.822Z" />
        </svg>
        {{ prompt.bookmark_count }}
      </button>
      <span class="flex items-center gap-1" title="복사된 횟수">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
        </svg>
        {{ prompt.copy_count }}
      </span>
      <span class="flex-1"></span>
      <button
        class="transition-colors hover:text-white light:hover:text-slate-900"
        :aria-label="capturing ? '이미지 생성 중' : '카드 이미지 저장'"
        title="카드 이미지 저장"
        :disabled="capturing"
        @click="downloadImage"
      >
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
        </svg>
      </button>
      <template v-if="editable">
        <button class="hover:text-white light:hover:text-slate-900" @click="emit('edit', prompt)">수정</button>
        <button class="hover:text-red-400" @click="emit('remove', prompt)">삭제</button>
      </template>
      <button
        class="rounded-lg border border-accent/50 text-accent hover:bg-accent hover:text-white transition-colors px-3 py-1 text-xs font-semibold"
        @click="showCopy = !showCopy"
      >
        {{ justCopied ? '복사됨 ✓' : '복사' }}
      </button>
    </footer>

    <div v-if="showCopy" class="mt-3 border-t border-white/10 light:border-slate-200 pt-3">
      <VariableFillPanel
        :prompt-text="prompt.prompt_text"
        :variables="prompt.variables"
        @copied="onCopied"
      />
    </div>

    <!-- 캡처용 오프스크린 공유 카드 -->
    <div v-if="capturing" aria-hidden="true" class="fixed top-0 -left-[9999px]">
      <div ref="shareEl">
        <ShareCard :prompt="prompt" />
      </div>
    </div>
  </article>
</template>
