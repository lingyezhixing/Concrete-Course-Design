<template>
  <div class="page">
    <h2 class="page-title">概览</h2>

    <el-card header="项目信息" class="card">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="项目名称">水利水电工程 - 混凝土课程设计计算平台</el-descriptions-item>
        <el-descriptions-item label="用途">辅助混凝土结构课程设计计算</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <p class="hint">注：设计参数（柱网、截面、材料）将在各模块页面中输入，此处暂不展示。</p>
  </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.page {
  padding: 20px;
}
.page-title {
  margin: 0 0 16px;
  font-size: 20px;
  color: var(--el-text-color-primary);
}
.card {
  margin-bottom: 16px;
}
.hint {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
