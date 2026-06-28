<template>
  <div
    class="skeleton"
    :style="{ height, width: width ?? '100%', borderRadius: rounded }"
  />
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    height?: string
    width?: string
    rounded?: string
  }>(),
  {
    height: '14px',
    rounded: 'var(--radius-sm)',
  },
)
</script>

<style scoped>
.skeleton {
  background: var(--muted);
  border-radius: var(--radius-sm);
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
@keyframes skeleton-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
  }
}
</style>
