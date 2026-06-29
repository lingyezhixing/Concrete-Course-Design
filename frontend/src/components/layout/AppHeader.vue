<template>
  <header class="topbar">
    <div class="left">
        <span class="brand" :title="isOnline ? '后端已连接' : '后端连接中断'">
          <img src="/logo.ico" class="brand-logo" alt="logo" />
          <span class="led" :class="isOnline ? 'on' : 'off'">
            <span v-if="isOnline" class="led-dot" />
          </span>
          <span class="brand-text">混凝土课程设计计算平台</span>
        </span>
      <button
        type="button"
        class="collapse-btn"
        :aria-label="btnLabel"
        :title="btnLabel"
        @click="emit('toggle')"
      >
        <component :is="btnIcon" :size="16" />
      </button>
    </div>
    <div class="right">
      <UserDropdown />
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { PanelLeftClose, PanelLeftOpen, Menu, X } from '@lucide/vue'
import { useHealth } from '../../composables/useHealth'
import { useSidebar } from '../../composables/useSidebar'
import UserDropdown from './UserDropdown.vue'

const props = defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ toggle: [] }>()

const { isOnline, start, stop } = useHealth()
const { isMobile, mobileOpen } = useSidebar()

// 折叠按钮图标/文案随视口切换：宽屏 = 折叠侧栏；窄屏 = 抽屉开关
const btnIcon = computed(() => {
  if (isMobile.value) return mobileOpen.value ? X : Menu
  return props.collapsed ? PanelLeftOpen : PanelLeftClose
})
const btnLabel = computed(() => {
  if (isMobile.value) return mobileOpen.value ? '关闭菜单' : '打开菜单'
  return props.collapsed ? '展开侧栏' : '收起侧栏'
})

onMounted(start)
onUnmounted(stop)
</script>

<style scoped>
.topbar {
  flex-shrink: 0;
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-4);
  background: var(--card);
  border-bottom: 1px solid var(--border);
}
.left,
.right {
  display: flex;
  align-items: center;
}
.left {
  gap: var(--space-1);
  min-width: 0;
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 var(--space-1);
  color: var(--foreground);
  min-width: 0;
}
.brand-logo {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
}
.brand-text {
  font-size: var(--text-lg);
  font-weight: 600;
  letter-spacing: -0.01em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.led {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border: 2px solid var(--success);
  border-radius: var(--radius-sm);
  flex-shrink: 0;
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
  transition:
    background-color var(--duration-fast),
    color var(--duration-fast);
}
.collapse-btn:hover {
  background: var(--muted);
  color: var(--foreground);
}

@media (max-width: 899px) {
  .brand-text {
    font-size: var(--text-md);
  }
}
</style>
