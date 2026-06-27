<template>
  <div class="header">
    <div class="header-left">
      <el-icon class="header-btn" :size="20" @click="emit('toggle')">
        <component :is="collapsed ? Expand : Fold" />
      </el-icon>
      <span class="title">混凝土课程设计计算平台</span>
    </div>
    <div class="header-right">
      <el-tooltip :content="isOnline ? '后端在线' : '后端离线'" placement="bottom">
        <span class="health-dot" :class="{ online: isOnline }" />
      </el-tooltip>
      <el-icon class="header-btn" :size="20" @click="toggleTheme">
        <component :is="isDark ? Moon : Sunny" />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { Fold, Expand, Moon, Sunny } from '@element-plus/icons-vue'
import { useTheme } from '../../composables/useTheme'
import { useHealth } from '../../composables/useHealth'

defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ toggle: [] }>()

const { isDark, toggle: toggleTheme } = useTheme()
const { isOnline, start, stop } = useHealth()

onMounted(start)
onUnmounted(stop)
</script>

<style scoped>
.header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-btn {
  cursor: pointer;
  color: var(--el-text-color-regular);
}
.title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.health-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--el-text-color-disabled);
}
.health-dot.online {
  background: var(--el-color-success);
}
</style>
