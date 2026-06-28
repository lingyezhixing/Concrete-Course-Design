<template>
  <div class="params">
    <PageHeader title="参数" subtitle="设计参数与确认计算" />

    <!-- 守卫：无活动项目 -->
    <section v-if="!isActive()" class="block guard">
      <p class="muted">请先在开始页选择或新建项目</p>
      <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
    </section>

    <!-- 参数表单 -->
    <template v-else>
      <!-- 材料 -->
      <section class="block">
        <h2 class="block-title">材料</h2>
        <el-form label-position="top" class="form">
          <el-form-item label="混凝土抗压 fc（N/mm²）">
            <el-input-number
              v-model="data!.materials.fc"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="板/箍筋 fy（N/mm²）">
            <el-input-number
              v-model="data!.materials.fy_slab"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="梁纵筋 fy（N/mm²）">
            <el-input-number
              v-model="data!.materials.fy_beam"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="结构系数 γd">
            <el-input-number
              v-model="data!.materials.gamma_d"
              :precision="2"
              :step="0.1"
              controls-position="right"
            />
          </el-form-item>
        </el-form>
      </section>

      <!-- 板几何 -->
      <section class="block">
        <h2 class="block-title">板几何</h2>
        <el-form label-position="top" class="form">
          <el-form-item label="板长（m）">
            <el-input-number
              v-model="data!.slab.input.length"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="板宽（m）">
            <el-input-number
              v-model="data!.slab.input.width"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="板厚（mm）">
            <el-input-number
              v-model="data!.slab.input.thickness"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="支座宽（mm）">
            <el-input-number
              v-model="data!.slab.input.support_width"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="跨数">
            <el-input-number
              v-model="data!.slab.input.spans"
              :step="1"
              :min="2"
              :precision="0"
              controls-position="right"
            />
            <span class="hint">{{ slabSpanHint }}</span>
          </el-form-item>
        </el-form>
      </section>

      <!-- 板荷载 -->
      <section class="block">
        <h2 class="block-title">板荷载</h2>
        <el-form label-position="top" class="form">
          <el-form-item label="钢筋混凝土重度（kN/m³）">
            <el-input-number
              v-model="data!.slab.input.reinforced_concrete_weight"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="水磨石（kN/m²）">
            <el-input-number
              v-model="data!.slab.input.terrazzo_surface"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="抹灰厚（mm）">
            <el-input-number
              v-model="data!.slab.input.plaster_thickness"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="抹灰重度（kN/m³）">
            <el-input-number
              v-model="data!.slab.input.plaster_weight"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
          <el-form-item label="楼面活载（kN/m²）">
            <el-input-number
              v-model="data!.slab.input.live_load"
              :precision="2"
              controls-position="right"
            />
          </el-form-item>
        </el-form>
      </section>

      <!-- 底部操作区 -->
      <section class="actions">
        <span class="muted save-state">{{ saving ? '自动保存中…' : '已保存' }}</span>
        <el-button type="primary" :loading="loading" @click="confirmCalc">确认计算</el-button>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '../components/common/PageHeader.vue'
import { useProject } from '../composables/useProject'

const router = useRouter()
const { data, saving, loading, isActive, calculate } = useProject()

const REQUIRED_MATERIALS: ReadonlyArray<'fc' | 'fy_slab' | 'gamma_d'> = [
  'fc',
  'fy_slab',
  'gamma_d',
]
const REQUIRED_SLAB: ReadonlyArray<string> = [
  'length',
  'width',
  'thickness',
  'support_width',
  'spans',
  'reinforced_concrete_weight',
  'terrazzo_surface',
  'plaster_thickness',
  'plaster_weight',
  'live_load',
]

/** 推荐板跨数：板跨度 1.7~2.5m → 跨数 = 板宽/板跨 − 1。仅推荐不强制。 */
const slabSpanHint = computed(() => {
  const w = data.value?.slab.input.width as number | undefined
  if (!w || w <= 0) return '推荐板跨数 —'
  const lo = Math.ceil(w / 2.5 - 1)
  const hi = Math.floor(w / 1.7 - 1)
  if (hi < lo) return '推荐板跨数 —'
  return `推荐板跨数 ${lo}~${hi}`
})

function missingFields(): string[] {
  const miss: string[] = []
  const m = data.value!.materials
  const s = data.value!.slab.input
  for (const k of REQUIRED_MATERIALS) {
    if (m[k] == null) miss.push(k)
  }
  for (const k of REQUIRED_SLAB) {
    const v = s[k] as unknown
    if (v == null || v === '') miss.push(k)
  }
  return miss
}

async function confirmCalc(): Promise<void> {
  if (!data.value) return
  const miss = missingFields()
  if (miss.length) {
    ElMessage.warning(`缺少：${miss.join(', ')}`)
    return
  }
  if (data.value.slab.initialized) {
    try {
      await ElMessageBox.confirm(
        '将覆盖板的计算结果，你对结果的手改会丢失。是否继续？',
        '数值覆盖',
        { type: 'warning', confirmButtonText: '确认覆盖', cancelButtonText: '取消' },
      )
    } catch {
      return
    }
  }
  try {
    await calculate('slab')
    ElMessage.success('计算完成')
    router.push('/slab')
  } catch (e: unknown) {
    const detail = (
      e as { response?: { data?: { detail?: { message?: string } | string } } }
    )?.response?.data?.detail
    const msg =
      typeof detail === 'string' ? detail : detail?.message ?? '计算失败，请检查参数'
    ElMessage.error(msg)
  }
}
</script>

<style scoped>
.params {
  max-width: 720px;
}
.block {
  margin-top: 20px;
  padding: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
}
.block-title {
  margin: 0 0 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--foreground);
}
.form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 24px;
}
.form :deep(.el-form-item) {
  margin-bottom: 8px;
}
.form :deep(.el-form-item__label) {
  color: var(--foreground);
  font-size: 13px;
  padding-bottom: 4px;
}
.form :deep(.el-input-number) {
  width: 100%;
}
.hint {
  margin-left: 10px;
  font-size: 12px;
  color: var(--muted-foreground);
  white-space: nowrap;
}
.muted {
  color: var(--muted-foreground);
  font-size: 13px;
}
/* 守卫 */
.guard {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
}
.guard .muted {
  margin: 0;
}
/* 底部操作区 */
.actions {
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
}
.save-state {
  font-size: 12px;
}
</style>
