<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  items: { type: Array, required: true },
})

const colCount = ref(3)
let mqCleanup = null

function updateCols() {
  const w = window.innerWidth
  colCount.value = w < 640 ? 1 : w < 1024 ? 2 : 3
}

onMounted(() => {
  updateCols()
  window.addEventListener('resize', updateCols, { passive: true })
  mqCleanup = () => window.removeEventListener('resize', updateCols)
})
onUnmounted(() => mqCleanup?.())

const columns = computed(() => {
  const cols = Array.from({ length: colCount.value }, () => [])
  props.items.forEach((item, i) => cols[i % colCount.value].push(item))
  return cols
})
</script>

<template>
  <div class="flex gap-4 items-start">
    <TransitionGroup
      v-for="(col, i) in columns"
      :key="i"
      tag="div"
      name="card"
      appear
      class="flex-1 min-w-0 space-y-4"
    >
      <div
        v-for="(item, j) in col"
        :key="item.id"
        :style="{ '--stagger': Math.min(j * 60, 300) + 'ms' }"
      >
        <slot :item="item"></slot>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
/* 카드 등장: 아래에서 살짝 떠오르며 행 단위로 stagger. 삭제 시 fade-out + 나머지 카드 move */
.card-enter-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
  transition-delay: var(--stagger, 0ms);
}
.card-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.card-move {
  transition: transform 0.35s ease;
}
.card-enter-from {
  opacity: 0;
  transform: translateY(16px);
}
.card-leave-to {
  opacity: 0;
  transform: scale(0.97);
}
@media (prefers-reduced-motion: reduce) {
  .card-enter-active,
  .card-leave-active,
  .card-move {
    transition: opacity 0.15s ease;
    transition-delay: 0ms;
  }
  .card-enter-from,
  .card-leave-to {
    transform: none;
  }
}
</style>
