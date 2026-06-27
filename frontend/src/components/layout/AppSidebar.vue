<template>
  <aside class="sidebar" :class="{ collapsed }">
    <nav class="nav">
      <router-link
        v-for="item in NAV_ITEMS"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ collapsed }"
        :title="collapsed ? item.title : undefined"
      >
        <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
        <span v-if="!collapsed" class="nav-label">{{ item.title }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { NAV_ITEMS } from '../../config/nav'

defineProps<{ collapsed: boolean }>()
</script>

<style scoped>
.sidebar {
  flex-shrink: 0;
  width: 208px;
  background: var(--card);
  border-right: 1px solid var(--border);
  transition: width 0.15s ease;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 56px;
}
.nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-left: 2px solid transparent;
  border-radius: var(--radius);
  font-size: 14px;
  color: var(--muted-foreground);
  text-decoration: none;
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
}
.nav-item:hover {
  background: var(--muted);
  color: var(--foreground);
}
/* exact-active so the "/" item is only highlighted on the overview page,
   not on every page (router-link-active would prefix-match "/"). */
.nav-item.router-link-exact-active {
  border-left-color: var(--primary);
  background: var(--muted);
  color: var(--foreground);
  font-weight: 500;
}
.nav-item.collapsed {
  justify-content: center;
  padding: 8px 0;
  border-left: none;
}
.nav-item.collapsed.router-link-exact-active {
  color: var(--primary);
}
.nav-icon {
  flex-shrink: 0;
  font-size: 16px;
}
.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
