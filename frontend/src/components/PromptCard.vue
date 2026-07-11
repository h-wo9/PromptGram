<script setup>
import { computed, ref } from 'vue'
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
</script>

<template>
  <article
    class="rounded-2xl border border-white/10 bg-white/[0.04] backdrop-blur-sm p-5 transition-colors hover:border-white/20"
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
        class="shrink-0 rounded-full bg-white/10 px-2.5 py-0.5 text-[11px] text-gray-300"
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

    <p class="mt-2 text-sm text-gray-300 whitespace-pre-wrap break-words leading-relaxed">
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

    <footer class="mt-4 flex items-center gap-4 text-sm text-gray-400">
      <button
        class="flex items-center gap-1 transition-colors"
        :class="prompt.is_liked ? 'text-red-400' : 'hover:text-red-400'"
        @click="emit('like', prompt)"
      >
        <span>{{ prompt.is_liked ? '♥' : '♡' }}</span>{{ prompt.like_count }}
      </button>
      <button
        class="flex items-center gap-1 transition-colors"
        :class="prompt.is_bookmarked ? 'text-accent' : 'hover:text-accent'"
        @click="emit('bookmark', prompt)"
      >
        <span>{{ prompt.is_bookmarked ? '★' : '☆' }}</span>{{ prompt.bookmark_count }}
      </button>
      <span class="flex items-center gap-1" title="복사된 횟수">⧉ {{ prompt.copy_count }}</span>
      <span class="flex-1"></span>
      <template v-if="editable">
        <button class="hover:text-white" @click="emit('edit', prompt)">수정</button>
        <button class="hover:text-red-400" @click="emit('remove', prompt)">삭제</button>
      </template>
      <button
        class="rounded-lg border border-accent/50 text-accent hover:bg-accent hover:text-white transition-colors px-3 py-1 text-xs font-semibold"
        @click="showCopy = !showCopy"
      >
        {{ justCopied ? '복사됨 ✓' : '복사' }}
      </button>
    </footer>

    <div v-if="showCopy" class="mt-3 border-t border-white/10 pt-3">
      <VariableFillPanel
        :prompt-text="prompt.prompt_text"
        :variables="prompt.variables"
        @copied="onCopied"
      />
    </div>
  </article>
</template>
