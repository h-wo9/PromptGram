<script setup>
// zoom 전환 중 scale된 페이지가 viewport를 넘치며 scrollbar가 깜빡이는 것 방지
function lockScroll() {
  document.documentElement.style.overflow = 'hidden'
}
function unlockScroll() {
  document.documentElement.style.overflow = ''
}
</script>

<template>
  <router-view v-slot="{ Component }">
    <transition
      name="zoom"
      mode="out-in"
      @before-leave="lockScroll"
      @after-enter="unlockScroll"
      @enter-cancelled="unlockScroll"
      @leave-cancelled="unlockScroll"
    >
      <component :is="Component" />
    </transition>
  </router-view>
</template>

<style>
.zoom-enter-active,
.zoom-leave-active {
  transition: opacity 0.45s ease, transform 0.45s ease;
}
.zoom-enter-from {
  opacity: 0;
  transform: scale(1.06);
}
.zoom-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
@media (prefers-reduced-motion: reduce) {
  .zoom-enter-active,
  .zoom-leave-active {
    transition: opacity 0.2s ease;
  }
  .zoom-enter-from,
  .zoom-leave-to {
    transform: none;
  }
}
</style>
