<template>
  <div class="params">
    <PageHeader title="设计参数" subtitle="结构、材料与荷载参数配置" />

    <!-- 守卫：无活动项目 -->
    <section v-if="!isActive()" class="block">
      <EmptyState
        :icon="guardIcon"
        title="尚未选择项目"
        description="请先在开始页选择或新建一个项目，再配置设计参数。"
      >
        <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
      </EmptyState>
    </section>

    <template v-else>
      <!-- 第一部分：结构参数 -->
      <section class="block">
        <h2 class="block-title">① 结构参数</h2>
        <el-form label-position="top" class="form">
          <el-form-item label="平面 L1（m，平行次梁）">
            <el-input-number v-model="data!.structure.L1" :precision="2" controls-position="right" />
          </el-form-item>
          <el-form-item label="平面 L2（m，平行主梁 / 板跨方向）">
            <el-input-number v-model="data!.structure.L2" :precision="2" controls-position="right" />
          </el-form-item>
          <el-form-item label="板厚（mm）">
            <el-input-number v-model="data!.structure.slab_thickness" :precision="0" controls-position="right" />
            <span class="hint">{{ slabThickHint }}</span>
          </el-form-item>
          <el-form-item label="次梁宽 b（mm）">
            <el-input-number v-model="data!.structure.beam_width" :precision="0" controls-position="right" />
          </el-form-item>
          <el-form-item label="次梁高 h（mm）">
            <el-input-number v-model="data!.structure.beam_height" :precision="0" controls-position="right" />
            <span class="hint">{{ beamRatioHint }}</span>
          </el-form-item>
          <el-form-item label="主梁宽 b（mm）">
            <el-input-number v-model="data!.structure.main_beam_width" :precision="0" controls-position="right" />
          </el-form-item>
          <el-form-item label="主梁高 h（mm）">
            <el-input-number v-model="data!.structure.main_beam_height" :precision="0" controls-position="right" />
            <span class="hint">{{ mainBeamRatioHint }}</span>
          </el-form-item>
          <el-form-item label="柱宽（mm）">
            <el-input-number v-model="data!.structure.column_width" :precision="0" controls-position="right" />
          </el-form-item>

          <el-form-item label="板跨数">
            <el-input-number v-model="data!.structure.slab_spans" :min="2" :step="1" :precision="0" controls-position="right" />
            <span class="hint">{{ slabSpanHint }}</span>
          </el-form-item>
          <el-form-item label="次梁跨数">
            <el-input-number v-model="data!.structure.beam_spans" :min="2" :step="1" :precision="0" controls-position="right" />
            <span class="hint">{{ beamSpanHint }}</span>
          </el-form-item>
          <el-form-item label="主梁跨数">
            <el-input-number v-model="data!.structure.main_beam_spans" :min="2" :step="1" :precision="0" controls-position="right" />
            <span class="hint">{{ mainBeamSpanHint }}</span>
          </el-form-item>
          <el-form-item label="次梁箍筋直径（mm）">
            <el-input-number v-model="data!.structure.beam_stirrup_diameter" :min="1" :precision="0" controls-position="right" />
          </el-form-item>
          <el-form-item label="主梁箍筋直径（mm）">
            <el-input-number v-model="data!.structure.main_beam_stirrup_diameter" :min="1" :precision="0" controls-position="right" />
          </el-form-item>
        </el-form>
        <p class="derived muted">板单跨/次梁间距 = {{ fmt(derived.beamSpacing) }} m；次梁跨度 = {{ fmt(derived.beamSpan) }} m；主梁跨度 = {{ fmt(derived.mainBeamSpan) }} m</p>
      </section>

      <!-- 第二部分：荷载参数 -->
      <section class="block">
        <h2 class="block-title">② 荷载参数</h2>
        <p class="muted note">材料强度与分项系数已固定在后端（C20 fc=9.6，Ⅰ级 fy=270，Ⅱ级 fy=300，γd=1.2，γG=1.05，γQ=1.2）。</p>
        <el-form label-position="top" class="form">
          <el-form-item label="钢筋混凝土重度（kN/m³）">
            <el-input-number v-model="data!.loads.reinforced_concrete_weight" :precision="2" controls-position="right" />
          </el-form-item>
          <el-form-item label="水磨石面层（kN/m²）">
            <el-input-number v-model="data!.loads.terrazzo_surface" :precision="2" controls-position="right" />
          </el-form-item>
          <el-form-item label="抹灰厚（mm）">
            <el-input-number v-model="data!.loads.plaster_thickness" :precision="1" controls-position="right" />
          </el-form-item>
          <el-form-item label="抹灰重度（kN/m³）">
            <el-input-number v-model="data!.loads.plaster_weight" :precision="2" controls-position="right" />
          </el-form-item>
          <el-form-item label="楼面活载（kN/m²）">
            <el-input-number v-model="data!.loads.live_load" :precision="2" controls-position="right" />
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
import { computed, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { FolderOpen } from '@lucide/vue'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'
import { useProject } from '../composables/useProject'
import type { Loads, Structure } from '../api/projects'

const guardIcon = markRaw(FolderOpen)

const router = useRouter()
const { data, saving, loading, isActive, calculate } = useProject()

const REQUIRED_STRUCTURE: ReadonlyArray<keyof Structure> = [
  'L1', 'L2', 'slab_thickness', 'beam_width', 'beam_height',
  'main_beam_width', 'main_beam_height', 'column_width',
  'slab_spans', 'beam_spans', 'main_beam_spans',
  'beam_stirrup_diameter', 'main_beam_stirrup_diameter',
]
const REQUIRED_LOADS: ReadonlyArray<keyof Loads> = [
  'reinforced_concrete_weight', 'terrazzo_surface',
  'plaster_thickness', 'plaster_weight', 'live_load',
]

/** 由结构派生的几何（与后端 derive 一致），用于实时展示与跨数推荐。 */
const derived = computed(() => {
  const s = data.value!.structure
  const beamSpacing = (s.L2 && s.slab_spans) ? s.L2 / s.slab_spans : null
  const beamSpan = (s.L1 && s.beam_spans) ? s.L1 / s.beam_spans : null
  const mainBeamSpan = (s.L2 && s.main_beam_spans) ? s.L2 / s.main_beam_spans : null
  return { beamSpacing, beamSpan, mainBeamSpan }
})

function fmt(v: number | null): string {
  return v == null ? '—' : v.toFixed(2)
}

/** 跨数推荐：跨数 = 总长 / 单跨（单跨取规范常用范围）。 */
function spanRange(total: number | null, spanLo: number, spanHi: number): string {
  if (!total || total <= 0) return '推荐 —'
  const lo = Math.ceil(total / spanHi)   // 单跨越大 → 跨数越少
  const hi = Math.floor(total / spanLo)  // 单跨越小 → 跨数越多
  if (hi < lo) return '推荐 —'
  return `推荐 ${lo}~${hi}`
}

const slabSpanHint = computed(() => spanRange(data.value!.structure.L2, 1.7, 2.5))
const beamSpanHint = computed(() => spanRange(data.value!.structure.L1, 4, 6))
const mainBeamSpanHint = computed(() => spanRange(data.value!.structure.L2, 5, 8))

/** 截面合理性提示（灰色，仅建议不阻断）。 */
const slabThickHint = computed(() => {
  const t = data.value!.structure.slab_thickness
  if (t == null) return '建议 80~120'
  return `建议 80~120（${t >= 80 && t <= 120 ? '合理' : '偏离'}）`
})
const beamRatioHint = computed(() => {
  const s = data.value!.structure
  if (!s.beam_height || !s.beam_width || !derived.value.beamSpan) return 'h/跨 1/18~1/12，b/h 1/3~1/2'
  const hoL = s.beam_height / 1000 / derived.value.beamSpan
  const boH = s.beam_width / s.beam_height
  const hoLOk = hoL >= 1 / 18 && hoL <= 1 / 12
  const boHOk = boH >= 1 / 3 && boH <= 1 / 2
  return `h/跨=${hoL.toFixed(3)}（${hoLOk ? '✓' : '✗'} 1/18~1/12） b/h=${boH.toFixed(2)}（${boHOk ? '✓' : '✗'} 1/3~1/2）`
})
const mainBeamRatioHint = computed(() => {
  const s = data.value!.structure
  if (!s.main_beam_height || !s.main_beam_width || !derived.value.mainBeamSpan) return 'h/跨 1/15~1/10，b/h 1/3~1/2'
  const hoL = s.main_beam_height / 1000 / derived.value.mainBeamSpan
  const boH = s.main_beam_width / s.main_beam_height
  const hoLOk = hoL >= 1 / 15 && hoL <= 1 / 10
  const boHOk = boH >= 1 / 3 && boH <= 1 / 2
  return `h/跨=${hoL.toFixed(3)}（${hoLOk ? '✓' : '✗'} 1/15~1/10） b/h=${boH.toFixed(2)}（${boHOk ? '✓' : '✗'} 1/3~1/2）`
})

function missingFields(): string[] {
  const miss: string[] = []
  const s = data.value!.structure
  const l = data.value!.loads
  for (const k of REQUIRED_STRUCTURE) if (s[k] == null) miss.push(k)
  for (const k of REQUIRED_LOADS) if (l[k] == null) miss.push(k)
  return miss
}

async function confirmCalc(): Promise<void> {
  if (!data.value) return
  const miss = missingFields()
  if (miss.length) {
    ElMessage.warning(`缺少：${miss.join(', ')}`)
    return
  }
  const d = data.value
  const anyInit = d.slab.initialized || d.beam.initialized || d.main_beam.initialized
  if (anyInit) {
    try {
      await ElMessageBox.confirm(
        '将覆盖已有的计算结果，手改值会丢失。是否继续？',
        '数值覆盖',
        { type: 'warning', confirmButtonText: '确认覆盖', cancelButtonText: '取消' },
      )
    } catch {
      return
    }
  }
  try {
    // 一键级联：板 → 次梁 → 主梁（三构件独立派生，顺序仅为语义）
    await calculate('slab')
    await calculate('beam')
    await calculate('main_beam')
    ElMessage.success('全链计算完成')
    router.push('/slab')
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: { message?: string } | string } } })?.response?.data?.detail
    const msg = typeof detail === 'string' ? detail : detail?.message ?? '计算失败，请检查参数'
    ElMessage.error(msg)
  }
}
</script>

<style scoped>
.params {
  width: 100%;
}
.form {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-1) var(--space-5);
}
.form :deep(.el-form-item) {
  margin-bottom: var(--space-2);
}
.form :deep(.el-form-item__label) {
  color: var(--foreground);
  font-size: var(--text-base);
  padding-bottom: var(--space-1);
}
.form :deep(.el-input-number) {
  width: 100%;
}
.hint {
  display: block;
  font-size: var(--text-xs);
  color: var(--muted-foreground);
  margin-top: 2px;
  line-height: 1.3;
}
.derived {
  margin: var(--space-3) 0 0;
  font-size: var(--text-sm);
}
.note {
  margin: 0 0 var(--space-3);
  font-size: var(--text-sm);
}
.actions {
  margin-top: var(--space-6);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--space-3);
}
.save-state {
  font-size: var(--text-sm);
}

/* 窄屏：参数表单降为 2 列 */
@media (max-width: 899px) {
  .form {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
