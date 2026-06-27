<template>
  <el-menu
    :default-active="route.path"
    :collapse="collapsed"
    :router="true"
    class="app-menu"
  >
    <el-menu-item v-for="item in NAV_ITEMS" :key="item.path" :index="item.path">
      <el-icon><component :is="item.icon" /></el-icon>
      <template #title>{{ item.title }}</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { NAV_ITEMS } from '../../config/nav'

defineProps<{ collapsed: boolean }>()

const route = useRoute()
</script>

<style scoped>
.app-menu {
  border-right: none;
  height: 100%;
}
.app-menu:not(.el-menu--collapse) {
  width: 210px;
}
</style>
