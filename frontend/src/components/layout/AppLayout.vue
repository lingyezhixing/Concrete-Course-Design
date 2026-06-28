<template>
  <div class="app-layout">
    <AppHeader :collapsed="isCollapsed" @toggle="toggle" />
    <div class="app-body">
      <AppSidebar :collapsed="isCollapsed" :mobile-open="mobileOpen" />
      <div
        class="sidebar-backdrop"
        :class="{ show: mobileOpen }"
        @click="closeMobile"
      />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import { useSidebar } from '../../composables/useSidebar'

const route = useRoute()
const { isCollapsed, mobileOpen, toggle, closeMobile } = useSidebar()

// 窄屏抽屉：导航后自动收起
watch(() => route.path, () => closeMobile())
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--background);
  color: var(--foreground);
}
.app-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  position: relative;
}
.app-main {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  padding: var(--content-pad);
}
.sidebar-backdrop {
  display: none;
}

@media (max-width: 899px) {
  .app-main {
    padding: var(--space-4);
  }
  .sidebar-backdrop {
    display: block;
    position: absolute;
    inset: 0;
    background: var(--el-mask-color);
    opacity: 0;
    pointer-events: none;
    transition: opacity var(--duration);
    z-index: var(--z-overlay);
  }
  .sidebar-backdrop.show {
    opacity: 1;
    pointer-events: auto;
  }
}
</style>
