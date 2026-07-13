<script setup>
import { watch, nextTick, ref, onMounted, onUnmounted } from 'vue'
import { confirmState, settleConfirm } from '../composables/confirm'

const confirmBtn = ref(null)

watch(
  () => confirmState.open,
  async (open) => {
    if (open) {
      await nextTick()
      confirmBtn.value?.focus()
    }
  }
)

function onKeydown(e) {
  if (confirmState.open && e.key === 'Escape') settleConfirm(false)
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <Transition name="dlg">
    <div
      v-if="confirmState.open"
      class="fixed inset-0 z-[80] flex items-center justify-center px-6 bg-black/60"
      @click.self="settleConfirm(false)"
    >
      <div
        role="alertdialog"
        aria-modal="true"
        :aria-label="confirmState.title"
        class="dlg-card w-full max-w-sm rounded-2xl border p-6 shadow-2xl
               border-white/15 bg-night/95 light:border-slate-200 light:bg-white"
      >
        <h2 class="font-bold">{{ confirmState.title }}</h2>
        <p v-if="confirmState.body" class="mt-2 text-sm text-gray-400 light:text-slate-500">
          {{ confirmState.body }}
        </p>
        <div class="mt-6 flex justify-end gap-2">
          <button
            class="rounded-lg px-4 py-2 text-sm text-gray-400 hover:text-white light:text-slate-500 light:hover:text-slate-900"
            @click="settleConfirm(false)"
          >
            취소
          </button>
          <button
            ref="confirmBtn"
            class="rounded-lg px-4 py-2 text-sm font-semibold text-white transition-colors"
            :class="confirmState.danger ? 'bg-red-500 hover:bg-red-600' : 'bg-accent hover:bg-blue-500'"
            @click="settleConfirm(true)"
          >
            {{ confirmState.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.dlg-enter-active,
.dlg-leave-active {
  transition: opacity 0.2s ease;
}
.dlg-enter-active .dlg-card,
.dlg-leave-active .dlg-card {
  transition: transform 0.2s ease;
}
.dlg-enter-from,
.dlg-leave-to {
  opacity: 0;
}
.dlg-enter-from .dlg-card {
  transform: scale(0.96) translateY(8px);
}
@media (prefers-reduced-motion: reduce) {
  .dlg-enter-from .dlg-card,
  .dlg-leave-to .dlg-card {
    transform: none;
  }
}
</style>
