<script setup>
import { reactive, computed } from 'vue'
import { substituteVariables } from '../utils/variables'

const props = defineProps({
  promptText: { type: String, required: true },
  variables: { type: Array, default: () => [] },
})
const emit = defineEmits(['copied'])

const values = reactive({})
const preview = computed(() => substituteVariables(props.promptText, values))
const allFilled = computed(() => props.variables.every((v) => values[v]?.trim()))

async function copy() {
  await navigator.clipboard.writeText(preview.value)
  emit('copied')
}
</script>

<template>
  <div class="space-y-3">
    <div v-if="variables.length" class="space-y-2">
      <label
        v-for="v in variables"
        :key="v"
        class="block"
      >
        <span class="text-xs text-accent font-semibold">[{{ v }}]</span>
        <input
          v-model="values[v]"
          type="text"
          :placeholder="`${v} 입력`"
          class="mt-1 w-full rounded-lg bg-white/5 border border-white/10 px-3 py-2 text-sm focus:border-accent focus:outline-none"
        />
      </label>
      <p class="text-xs text-gray-400 whitespace-pre-wrap break-words rounded-lg bg-white/5 p-3 max-h-40 overflow-y-auto">
        {{ preview }}
      </p>
    </div>
    <button
      class="w-full rounded-lg bg-accent hover:bg-blue-500 transition-colors px-4 py-2 text-sm font-semibold disabled:opacity-40"
      :disabled="variables.length > 0 && !allFilled"
      @click="copy"
    >
      {{ variables.length ? '변수 채워서 복사' : '복사하기' }}
    </button>
  </div>
</template>
