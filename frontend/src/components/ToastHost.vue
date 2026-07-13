<script setup>
import { toasts } from '../composables/toast'
</script>

<template>
  <div
    class="fixed bottom-6 inset-x-0 z-[90] flex flex-col items-center gap-2 pointer-events-none px-4"
    aria-live="polite"
  >
    <TransitionGroup name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="rounded-full border px-4 py-2 text-sm font-medium backdrop-blur-md shadow-lg
               border-white/15 bg-night/85 text-gray-100
               light:border-slate-200 light:bg-white/95 light:text-slate-700 light:backdrop-blur-none"
      >
        <span v-if="t.type === 'success'" class="text-accent mr-1.5">✓</span>
        <span v-else-if="t.type === 'error'" class="text-red-400 mr-1.5">!</span>
        {{ t.message }}
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.97);
}
.toast-move {
  transition: transform 0.25s ease;
}
@media (prefers-reduced-motion: reduce) {
  .toast-enter-active,
  .toast-leave-active,
  .toast-move {
    transition: opacity 0.15s ease;
  }
  .toast-enter-from,
  .toast-leave-to {
    transform: none;
  }
}
</style>
