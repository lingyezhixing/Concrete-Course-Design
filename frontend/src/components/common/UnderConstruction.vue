<template>
  <div class="uc">
    <el-empty :description="`${title} — 建设中`">
      <template #image>
        <el-icon :size="64" class="uc-icon"><Tools /></el-icon>
      </template>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { Tools } from '@element-plus/icons-vue'

defineProps<{ title: string }>()
</script>

<style scoped>
.uc {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  padding: 40px;
}
.uc-icon {
  color: var(--el-text-color-secondary);
}
</style>
