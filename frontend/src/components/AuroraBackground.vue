<script setup>
// 랜딩과 이어지는 대기 조명 — 앱 페이지용 (콘텐츠 가독성을 위해 랜딩보다 옅게)
</script>

<template>
  <div class="fixed inset-0 z-0 pointer-events-none overflow-hidden" aria-hidden="true">
    <div class="ab-blob ab-blob--blue"></div>
    <div class="ab-blob ab-blob--violet"></div>
  </div>
</template>

<style scoped>
.ab-blob {
  position: absolute;
  width: 60vmax;
  height: 60vmax;
  border-radius: 9999px;
  will-change: transform;
}
.ab-blob--blue {
  top: -28vmax;
  left: -18vmax;
  background: radial-gradient(closest-side, rgba(0, 112, 243, 0.2), rgba(0, 112, 243, 0.06) 50%, transparent 72%);
  animation: ab-float 18s ease-in-out infinite alternate;
}
.ab-blob--violet {
  bottom: -30vmax;
  right: -20vmax;
  background: radial-gradient(closest-side, rgba(124, 58, 237, 0.18), rgba(124, 58, 237, 0.06) 50%, transparent 72%);
  animation: ab-float 22s ease-in-out infinite alternate-reverse;
}
@keyframes ab-float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(5vmax, -4vmax) scale(1.1); }
}
@media (prefers-reduced-motion: reduce) {
  .ab-blob--blue,
  .ab-blob--violet {
    animation: none;
  }
}
</style>
