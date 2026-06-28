<template>
  <div class="empty-state" :class="{ compact }">
    <div v-if="icon" class="empty-icon">
      <component :is="icon" :size="26" />
    </div>
    <h3 v-if="title" class="empty-title">{{ title }}</h3>
    <p v-if="description" class="empty-desc">{{ description }}</p>
    <div v-if="$slots.default" class="empty-action">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { markRaw } from 'vue'
import type { Component } from 'vue'
import { Inbox } from '@lucide/vue'

withDefaults(
  defineProps<{
    icon?: Component
    title?: string
    description?: string
    compact?: boolean
  }>(),
  {
    icon: () => markRaw(Inbox),
    title: '',
    description: '',
    compact: false,
  },
)
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: var(--space-3);
  padding: var(--space-10) var(--space-6);
}
.empty-state.compact {
  padding: var(--space-8) var(--space-6);
}
.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: var(--muted);
  color: var(--muted-foreground);
}
.empty-title {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--foreground);
}
.empty-desc {
  margin: 0;
  font-size: var(--text-base);
  color: var(--muted-foreground);
  max-width: 380px;
  line-height: 1.5;
}
.empty-action {
  margin-top: var(--space-1);
}
</style>
