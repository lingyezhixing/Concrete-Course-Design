<template>
  <div class="settings">
    <PageHeader title="系统设置" subtitle="主题与账户偏好" />
    <section class="block">
      <h2 class="block-title">主题外观</h2>
      <div class="theme-options">
        <button
          v-for="opt in OPTIONS"
          :key="opt.value"
          type="button"
          class="opt"
          :class="{ active: theme === opt.value }"
          @click="setTheme(opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </section>
    <section class="block">
      <h2 class="block-title">账户</h2>
      <p class="muted">当前用户：{{ currentUser?.username ?? '未登录' }}</p>
    </section>
  </div>
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
import { useTheme, type Theme } from '../composables/useTheme'
import { useAuth } from '../composables/useAuth'

const OPTIONS: ReadonlyArray<{ value: Theme; label: string }> = [
  { value: 'dark', label: '深色' },
  { value: 'light', label: '浅色' },
  { value: 'warm', label: '暖灰' },
]

const { theme, setTheme } = useTheme()
const { currentUser } = useAuth()
</script>

<style scoped>
.settings {
  max-width: 720px;
}
.block {
  margin-top: 20px;
  padding: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
.block-title {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
}
.theme-options {
  display: flex;
  gap: 8px;
}
.opt {
  height: 32px;
  padding: 0 14px;
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
.muted {
  color: var(--muted-foreground);
  font-size: 13px;
}
</style>
