<script setup>
</script>

<template>
  <router-view v-slot="{ Component }">
    <transition name="zoom" mode="out-in">
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
