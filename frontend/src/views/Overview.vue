<template>
  <div class="page">
    <h2 class="page-title">概览</h2>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card header="项目信息" class="card">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="项目名称">水利水电工程 - 混凝土课程设计计算平台</el-descriptions-item>
            <el-descriptions-item label="用途">辅助混凝土结构课程设计计算</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="柱网布置" class="card">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="总尺寸">L1 × L2 = 18 × 30 m</el-descriptions-item>
            <el-descriptions-item label="梁格尺寸">6 × 6 m</el-descriptions-item>
            <el-descriptions-item label="主梁">横向布置，跨度 6 m</el-descriptions-item>
            <el-descriptions-item label="次梁">纵向布置，跨度 6 m</el-descriptions-item>
            <el-descriptions-item label="柱数量">8 根</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-card header="构件截面初估" class="card">
      <el-table :data="sections" border>
        <el-table-column prop="member" label="构件" />
        <el-table-column prop="size" label="截面尺寸" />
      </el-table>
    </el-card>

    <el-card header="材料" class="card">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="混凝土">C25 – C40</el-descriptions-item>
        <el-descriptions-item label="钢筋">HPB300 – HRB500</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
const sections = [
  { member: '板', size: '厚度 120 mm' },
  { member: '次梁', size: 'b × h = 200 × 500 mm' },
  { member: '主梁', size: 'b × h = 300 × 600 mm' },
]
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
</style>
