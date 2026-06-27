<template>
  <header class="topbar">
    <div class="left">
      <span class="brand" :title="isOnline ? '后端已连接' : '后端连接中断'">
        <span class="led" :class="isOnline ? 'on' : 'off'">
          <span v-if="isOnline" class="led-dot" />
        </span>
        <span class="brand-text">混凝土课程设计计算平台</span>
      </span>
      <button
        type="button"
        class="collapse-btn"
        :aria-label="collapsed ? '展开侧栏' : '收起侧栏'"
        :title="collapsed ? '展开侧栏' : '收起侧栏'"
        @click="emit('toggle')"
      >
        <component :is="collapsed ? PanelLeftOpen : PanelLeftClose" :size="16" />
      </button>
    </div>
    <div class="right">
      <ThemeSwitcher />
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { PanelLeftClose, PanelLeftOpen } from '@lucide/vue'
import { useHealth } from '../../composables/useHealth'
import ThemeSwitcher from './ThemeSwitcher.vue'

defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ toggle: [] }>()

const { isOnline, start, stop } = useHealth()

onMounted(start)
onUnmounted(stop)
</script>

<style scoped>
.topbar {
  flex-shrink: 0;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
}
.left,
.right {
  display: flex;
  align-items: center;
}
.left {
  gap: 4px;
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 4px;
  color: var(--foreground);
}
.brand-text {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.led {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border: 2px solid var(--success);
  border-radius: 2px;
}
.led.off {
  border-color: var(--destructive);
}
.led-dot {
  width: 6px;
  height: 6px;
  border-radius: 1px;
  background: var(--success);
}
.collapse-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: var(--radius);
  color: var(--muted-foreground);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
}
.collapse-btn:hover {
  background: var(--muted);
  color: var(--foreground);
}
</style>
