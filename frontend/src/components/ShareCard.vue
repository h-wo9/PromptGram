<script setup>
// 공유용 카드 — html2canvas 캡처 전용 스타일 (backdrop-filter 미지원이므로 불투명 배경 사용)
import { computed } from 'vue'

const props = defineProps({
  prompt: { type: Object, required: true },
})

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
</script>

<template>
  <div class="share-card">
    <div class="share-head">
      <span class="share-logo">Prompt<span class="share-logo-accent">Gram</span></span>
      <span v-if="prompt.ai_source" class="share-source">{{ prompt.ai_source }}</span>
    </div>
    <h2 class="share-title">{{ prompt.title }}</h2>
    <p class="share-text">
      <template v-for="(seg, i) in segments" :key="i">
        <span v-if="seg.isVar" class="share-var">{{ seg.text }}</span>
        <template v-else>{{ seg.text }}</template>
      </template>
    </p>
    <div v-if="prompt.tags.length" class="share-tags">
      <span v-for="t in prompt.tags" :key="t" class="share-tag">#{{ t }}</span>
    </div>
    <div class="share-foot">
      <span>by {{ prompt.author.nickname }}</span>
      <span class="share-var-count" v-if="prompt.variables.length">변수 {{ prompt.variables.length }}개 템플릿</span>
    </div>
  </div>
</template>

<style scoped>
.share-card {
  width: 520px;
  padding: 36px;
  background: linear-gradient(160deg, #101623 0%, #0a0a0a 55%);
  border: 1px solid rgba(0, 112, 243, 0.35);
  border-radius: 20px;
  color: #f3f4f6;
  font-family: 'Pretendard Variable', Pretendard, sans-serif;
}
.share-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.share-logo {
  font-size: 15px;
  font-weight: 800;
  letter-spacing: -0.02em;
}
.share-logo-accent {
  color: #0070f3;
}
.share-source {
  font-size: 12px;
  font-weight: 600;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.09);
  border-radius: 9999px;
  padding: 3px 12px;
}
.share-title {
  margin-top: 22px;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.3;
  word-break: keep-all;
  overflow-wrap: break-word;
}
.share-text {
  margin-top: 14px;
  font-size: 15px;
  line-height: 1.7;
  color: #cbd5e1;
  white-space: pre-wrap;
  overflow-wrap: break-word;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px 18px;
}
.share-var {
  color: #3b96ff;
  font-weight: 700;
}
.share-tags {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
/* html2canvas가 이 앱 컨텍스트에서 pill 배경 + 텍스트 baseline을 어긋나게 그리는
   버그가 있어 배경 없는 텍스트 태그로 유지 (ShareCard는 캡처 전용) */
.share-tag {
  font-size: 13px;
  font-weight: 600;
  color: #3b96ff;
}
.share-foot {
  margin-top: 22px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
}
.share-var-count {
  color: #3b96ff;
}
</style>
