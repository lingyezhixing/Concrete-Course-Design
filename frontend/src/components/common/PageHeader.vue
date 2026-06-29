<template>
  <div class="page-header">
    <div class="titles">
      <h1 class="title">{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.action" class="action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}
.title {
  margin: 0;
  font-size: var(--text-2xl);
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--foreground);
}
.subtitle {
  margin: var(--space-1) 0 0;
  font-size: var(--text-base);
  color: var(--muted-foreground);
}
.action {
  flex-shrink: 0;
}
</style>
