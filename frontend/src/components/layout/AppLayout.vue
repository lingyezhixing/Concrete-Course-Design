<template>
  <el-container class="app-layout">
    <el-header class="app-header">
      <AppHeader :collapsed="isCollapsed" @toggle="toggle" />
    </el-header>
    <el-container>
      <el-aside :width="isCollapsed ? '64px' : '210px'" class="app-aside">
        <AppSidebar :collapsed="isCollapsed" />
      </el-aside>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import { useSidebar } from '../../composables/useSidebar'

const { isCollapsed, toggle } = useSidebar()
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.app-header {
  padding: 0;
  height: 56px;
  border-bottom: 1px solid var(--el-border-color);
}
.app-aside {
  border-right: 1px solid var(--el-border-color);
  transition: width 0.2s;
  overflow: hidden;
}
.app-main {
  padding: 0;
  background: var(--el-bg-color-page);
  overflow-y: auto;
}
</style>
