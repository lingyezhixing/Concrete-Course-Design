<template>
  <div class="page">
    <h2 class="page-title">材料参数</h2>

    <el-card header="混凝土强度设计值 (MPa)" class="card">
      <el-table :data="concrete" border>
        <el-table-column prop="grade" label="等级" />
        <el-table-column prop="fc" label="fc（抗压）" />
        <el-table-column prop="ft" label="ft（抗拉）" />
        <el-table-column prop="ec" label="Ec（弹性模量）" />
      </el-table>
    </el-card>

    <el-card header="钢筋强度设计值 (MPa)" class="card">
      <el-table :data="steel" border>
        <el-table-column prop="grade" label="等级" />
        <el-table-column prop="fy" label="fy（屈服强度）" />
      </el-table>
    </el-card>

    <p class="hint">注：本页为静态展示，数据与后端 calc/materials.py 一致。</p>
  </div>
</template>

<script setup lang="ts">
const concrete = [
  { grade: 'C25', fc: 11.9, ft: 1.27, ec: 28000 },
  { grade: 'C30', fc: 14.3, ft: 1.43, ec: 30000 },
  { grade: 'C35', fc: 16.7, ft: 1.57, ec: 31500 },
  { grade: 'C40', fc: 19.1, ft: 1.71, ec: 32500 },
]
const steel = [
  { grade: 'HPB300', fy: 270 },
  { grade: 'HRB335', fy: 300 },
  { grade: 'HRB400', fy: 360 },
  { grade: 'HRB500', fy: 435 },
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
.hint {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
