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
    <div v-for="(col, i) in columns" :key="i" class="flex-1 min-w-0 space-y-4">
      <slot v-for="item in col" :key="item.id" :item="item"></slot>
    </div>
  </div>
</template>
