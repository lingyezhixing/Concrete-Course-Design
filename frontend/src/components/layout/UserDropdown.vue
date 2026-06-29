<template>
  <el-dropdown trigger="click" aria-label="用户菜单" @command="onCommand">
    <span class="user">
      <span class="avatar">{{ initial }}</span>
      <span class="name">{{ username }}</span>
      <component :is="ChevronDown" :size="14" />
    </span>
    <template #dropdown>
      <el-dropdown-menu>
        <el-dropdown-item v-for="t in THEMES" :key="t.value" :command="'theme:' + t.value">
          <span :class="{ active: theme === t.value }">{{ t.label }}</span>
        </el-dropdown-item>
        <el-dropdown-item divided command="settings">系统设置</el-dropdown-item>
        <el-dropdown-item command="logout">退出登录</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { ChevronDown } from '@lucide/vue'
import { useAuth } from '../../composables/useAuth'
import { useTheme, type Theme } from '../../composables/useTheme'

const THEMES: ReadonlyArray<{ value: Theme; label: string }> = [
  { value: 'dark', label: '深色' },
  { value: 'light', label: '浅色' },
  { value: 'warm', label: '暖灰' },
]

const router = useRouter()
const { currentUser, logout } = useAuth()
const { theme, setTheme } = useTheme()

const username = computed(() => currentUser.value?.username ?? '')
const initial = computed(() => username.value.charAt(0).toUpperCase() || '?')

async function onCommand(cmd: string): Promise<void> {
  if (cmd.startsWith('theme:')) {
    setTheme(cmd.slice(6) as Theme)
  } else if (cmd === 'settings') {
    router.push('/settings')
  } else if (cmd === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '退出登录', {
        type: 'warning',
        confirmButtonText: '退出',
        cancelButtonText: '取消',
      })
    } catch {
      return // 用户取消
    }
    logout()
    router.replace('/login')
  }
}
</script>

<style scoped>
.user {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius);
  cursor: pointer;
  color: var(--foreground);
}
.user:hover {
  background: var(--muted);
}
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary);
  color: var(--primary-foreground);
  font-size: var(--text-sm);
  font-weight: 600;
}
.name {
  font-size: var(--text-base);
}
.active {
  color: var(--primary);
  font-weight: 600;
}
</style>
