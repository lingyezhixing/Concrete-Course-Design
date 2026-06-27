<template>
  <div class="theme-switcher">
    <button
      v-for="opt in OPTIONS"
      :key="opt.value"
      type="button"
      class="opt"
      :class="{ active: theme === opt.value }"
      :title="opt.label"
      @click="setTheme(opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useTheme, type Theme } from '../../composables/useTheme'

const OPTIONS: ReadonlyArray<{ value: Theme; label: string }> = [
  { value: 'dark', label: '深色' },
  { value: 'light', label: '浅色' },
  { value: 'warm', label: '暖灰' },
]

const { theme, setTheme } = useTheme()
</script>

<style scoped>
.theme-switcher {
  display: flex;
  gap: 4px;
}
.opt {
  height: 28px;
  padding: 0 10px;
  font-size: 13px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: transparent;
  color: var(--muted-foreground);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
}
.opt:hover {
  background: var(--muted);
  color: var(--foreground);
}
.opt.active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--primary-foreground);
}
</style>
