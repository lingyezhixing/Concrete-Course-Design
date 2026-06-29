<template>
  <div class="report">
    <PageHeader title="计算书" subtitle="自动生成设计计算书">
      <template #action>
        <el-button type="primary" :icon="printIcon" @click="onPrint">打印 / 导出 PDF</el-button>
      </template>
    </PageHeader>

    <section v-if="!isActive()" class="block">
      <EmptyState :icon="noProjectIcon" title="尚未选择项目"
        description="请先在开始页选择或新建一个项目。">
        <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
      </EmptyState>
    </section>

    <template v-else>
      <!-- 工具条：封面信息表单 + 完整性提示 -->
      <section class="block toolbar">
        <h2 class="block-title">封面信息</h2>
        <el-form :model="cover" label-width="92px" size="small" class="cover-form">
          <div class="cover-grid">
            <el-form-item label="学院"><el-input v-model="cover.college" /></el-form-item>
            <el-form-item label="专业"><el-input v-model="cover.major" /></el-form-item>
            <el-form-item label="姓名"><el-input v-model="cover.name" /></el-form-item>
            <el-form-item label="学号"><el-input v-model="cover.student_id" /></el-form-item>
            <el-form-item label="指导教师"><el-input v-model="cover.advisor" /></el-form-item>
            <el-form-item label="完成日期"><el-input v-model="cover.date" placeholder="如 2026年6月" /></el-form-item>
          </div>
        </el-form>
        <p class="ready-hint">
          计算状态：板 {{ ready.slab ? '✓' : '✗' }}／次梁 {{ ready.beam ? '✓' : '✗' }}／主梁 {{ ready.main ? '✓' : '✗' }}。
          未计算的章节会显示提示，不影响已计算部分导出。
        </p>
      </section>

      <!-- A4 预览 -->
      <section class="block preview">
        <div class="report-document">
          <ReportDocument :doc="doc" />
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, watch, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOpen, Printer } from '@lucide/vue'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'
import ReportDocument from '../components/report/ReportDocument.vue'
import { useProject } from '../composables/useProject'
import { useAuth } from '../composables/useAuth'
import { buildReportDoc } from '../composables/useReportDocument'
import type { CoverInfo, ReportDoc } from '../report/types'

const noProjectIcon = markRaw(FolderOpen)
const printIcon = markRaw(Printer)

const router = useRouter()
const { data, isActive } = useProject()
const { currentUser } = useAuth()

/** 封面表单：单向同步。
 *  - 项目载入/切换（data 引用变化）→ 回填 cover；姓名空时预填登录用户名。
 *  - cover 改动 → 写回 data.report（触发 useProject 防抖自动保存）。
 *  不反向监听 data.report，避免 cover↔data 互相触发形成循环。 */
const cover = reactive<CoverInfo>({
  college: '', major: '', name: '', student_id: '', advisor: '', date: '',
})

watch(
  () => data.value,
  (d) => {
    const r = d?.report
    cover.college = r?.college ?? ''
    cover.major = r?.major ?? ''
    cover.name = r?.name ?? ''
    cover.student_id = r?.student_id ?? ''
    cover.advisor = r?.advisor ?? ''
    cover.date = r?.date ?? ''
    // 项目无姓名且当前未填 → 预填登录用户名（仅一次，填过不再覆盖）
    if (!cover.name && currentUser.value?.username) {
      cover.name = currentUser.value.username
    }
  },
  { immediate: true },
)

watch(
  cover,
  () => {
    if (data.value) {
      data.value.report = {
        college: cover.college, major: cover.major, name: cover.name,
        student_id: cover.student_id, advisor: cover.advisor, date: cover.date,
      }
    }
  },
  { deep: true },
)

/** 装配计算书：读 data（含已写回的 report）。无项目时返回空文档（模板由 isActive 守卫，不会渲染）。 */
const doc = computed<ReportDoc>(() =>
  data.value ? buildReportDoc(data.value) : { cover: {}, sections: [] },
)

const ready = computed(() => ({
  slab: data.value?.slab?.initialized === true,
  beam: data.value?.beam?.initialized === true,
  main: data.value?.main_beam?.initialized === true,
}))

function onPrint(): void {
  window.print()
}
</script>

<style scoped>
.report { width: 100%; }
.toolbar { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6); }
.block-title { font-size: var(--text-md); font-weight: 600; margin: 0 0 var(--space-3); }
.cover-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0 var(--space-6); }
.ready-hint { font-size: var(--text-sm); color: var(--muted-foreground); margin: var(--space-2) 0 0; }
.preview { background: var(--muted); padding: var(--space-6); border-radius: var(--radius-lg); }
.report-document { box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); border-radius: 4px; overflow: hidden; }
@media (max-width: 900px) { .cover-grid { grid-template-columns: 1fr; } }
</style>
