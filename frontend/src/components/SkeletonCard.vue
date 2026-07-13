<script setup>
// 로딩 skeleton — PromptCard 골격 + shimmer
defineProps({
  lines: { type: Number, default: 3 },
})
</script>

<template>
  <div class="rounded-2xl border border-white/10 bg-white/[0.04] light:border-slate-200 light:bg-white p-5">
    <div class="flex items-center gap-2.5">
      <div class="sk w-8 h-8 rounded-full"></div>
      <div class="sk h-3 w-20 rounded"></div>
      <span class="flex-1"></span>
      <div class="sk h-4 w-14 rounded-full"></div>
    </div>
    <div class="sk mt-4 h-4 w-3/4 rounded"></div>
    <div class="mt-3 space-y-2">
      <div v-for="i in lines" :key="i" class="sk h-3 rounded" :class="i === lines ? 'w-1/2' : 'w-full'"></div>
    </div>
    <div class="mt-4 flex gap-3">
      <div class="sk h-3 w-8 rounded"></div>
      <div class="sk h-3 w-8 rounded"></div>
      <span class="flex-1"></span>
      <div class="sk h-6 w-12 rounded-lg"></div>
    </div>
  </div>
</template>

<style scoped>
.sk {
  background: linear-gradient(
    100deg,
    rgba(255, 255, 255, 0.06) 40%,
    rgba(255, 255, 255, 0.14) 50%,
    rgba(255, 255, 255, 0.06) 60%
  );
  background-size: 200% 100%;
  animation: sk-shimmer 1.4s ease-in-out infinite;
}
:global(.light) .sk {
  background: linear-gradient(
    100deg,
    rgba(15, 23, 42, 0.06) 40%,
    rgba(15, 23, 42, 0.12) 50%,
    rgba(15, 23, 42, 0.06) 60%
  );
  background-size: 200% 100%;
}
@keyframes sk-shimmer {
  0% { background-position: 120% 0; }
  100% { background-position: -80% 0; }
}
@media (prefers-reduced-motion: reduce) {
  .sk {
    animation: none;
  }
}
</style>
