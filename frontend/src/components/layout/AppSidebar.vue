<template>
  <aside class="sidebar" :class="{ collapsed, 'mobile-open': mobileOpen }">
    <nav class="nav">
      <div v-for="g in NAV_GROUPS" :key="g.label" class="nav-group">
        <span v-if="!collapsed" class="nav-group-label">{{ g.label }}</span>
        <router-link
          v-for="item in g.items"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ collapsed }"
          :title="collapsed ? item.title : undefined"
        >
          <component :is="item.icon" class="nav-icon" :size="16" />
          <span v-if="!collapsed" class="nav-label">{{ item.title }}</span>
        </router-link>
      </div>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { NAV_GROUPS } from '../../config/nav'

defineProps<{ collapsed: boolean; mobileOpen: boolean }>()
</script>

<style scoped>
.sidebar {
  flex-shrink: 0;
  width: var(--sidebar-width);
  background: var(--card);
  border-right: 1px solid var(--border);
  transition:
    width var(--duration-fast) var(--ease),
    transform var(--duration) var(--ease);
  overflow: hidden;
}
.sidebar.collapsed {
  width: var(--sidebar-collapsed);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-2);
  height: 100%;
  overflow-y: auto;
}
.nav-group {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-group:not(:first-child) {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid var(--border);
}
.nav-group-label {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--muted-foreground);
  letter-spacing: 0.04em;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-left: 2px solid transparent;
  border-radius: var(--radius);
  font-size: var(--text-md);
  color: var(--muted-foreground);
  text-decoration: none;
  transition:
    background-color var(--duration-fast),
    color var(--duration-fast),
    border-color var(--duration-fast);
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
  padding: var(--space-2) 0;
  border-left: none;
}
.nav-item.collapsed.router-link-exact-active {
  color: var(--primary);
}
.nav-icon {
  flex-shrink: 0;
}
.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 折叠态：隐藏分组标签，组间仅靠分隔线区分 */
.sidebar.collapsed .nav-group-label {
  display: none;
}

/* 窄屏：抽屉化（覆盖式），始终展开宽度，忽略 collapsed */
@media (max-width: 899px) {
  .sidebar {
    position: absolute;
    top: 0;
    bottom: 0;
    left: 0;
    z-index: var(--z-sidebar);
    width: var(--sidebar-width);
    transform: translateX(-100%);
    box-shadow: var(--el-box-shadow-dark);
  }
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  .sidebar.collapsed {
    width: var(--sidebar-width);
  }
  .sidebar.collapsed .nav-group-label {
    display: block;
  }
  .sidebar.collapsed .nav-item {
    justify-content: flex-start;
    padding: var(--space-2) var(--space-3);
    border-left: 2px solid transparent;
  }
}
</style>
