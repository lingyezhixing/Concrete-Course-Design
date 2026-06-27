<template>
  <div class="app-layout">
    <AppHeader :collapsed="isCollapsed" @toggle="toggle" />
    <div class="app-body">
      <AppSidebar :collapsed="isCollapsed" />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import { useSidebar } from '../../composables/useSidebar'

const { isCollapsed, toggle } = useSidebar()
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
}
.app-main {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  padding: 24px;
}
</style>
