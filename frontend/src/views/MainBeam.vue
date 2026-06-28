<template>
  <div class="main-beam">
    <PageHeader title="主梁计算" subtitle="内力分析、配筋与吊筋设计">
      <template #action>
        <span class="save-state">{{ saving ? '自动保存中…' : '已保存' }}</span>
      </template>
    </PageHeader>

    <section v-if="!isActive()" class="block">
      <EmptyState
        :icon="noProjectIcon"
        title="尚未选择项目"
        description="请先在开始页选择或新建一个项目。"
      >
        <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
      </EmptyState>
    </section>
    <section v-else-if="!mbReady" class="block">
      <EmptyState
        :icon="noCalcIcon"
        title="尚未计算"
        description="请先在参数页填写参数并确认计算。"
      >
        <el-button type="primary" @click="router.push('/params')">前往参数页</el-button>
      </EmptyState>
    </section>

    <div v-else class="data">
      <!-- 集中荷载 -->
      <section class="block">
        <h2 class="block-title">集中荷载</h2>
        <div class="load-grid">
          <div class="field"><label class="lbl">次梁传来恒载（kN）</label><span class="val muted">{{ result.load.from_beam_dead }}</span></div>
          <div class="field"><label class="lbl">主梁自重（kN）</label><span class="val muted">{{ result.load.self_weight }}</span></div>
          <div class="field"><label class="lbl">主梁粉刷（kN）</label><span class="val muted">{{ result.load.plaster }}</span></div>
          <div class="field"><label class="lbl">恒载标准值 Gk（kN）</label>
            <el-input-number v-model="result.load.dead_load_standard" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">恒载设计值 G（kN）</label>
            <el-input-number v-model="result.load.dead_load_design" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">活载标准值 Qk（kN）</label>
            <el-input-number v-model="result.load.live_load_standard" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">活载设计值 Q（kN）</label>
            <el-input-number v-model="result.load.live_load_design" :precision="3" :controls="false" size="small" class="num" /></div>
        </div>
      </section>

      <!-- 计算简图 -->
      <section v-if="diagram" class="block">
        <h2 class="block-title">计算简图</h2>
        <MainBeamDiagram v-bind="diagram" />
      </section>

      <!-- 内力 -->
      <section class="block">
        <h2 class="block-title">内力</h2>
        <h3 class="sub-title">弯矩 M（kN·m）</h3>
        <div class="load-grid">
          <div class="field"><label class="lbl">M1 跨1最大</label>
            <el-input-number v-model="result.internal_forces.M1_max" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">M_B 支座（边缘调整）</label>
            <el-input-number v-model="result.internal_forces.M_B_min" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">M2 跨2最大</label>
            <el-input-number v-model="result.internal_forces.M2_max" :precision="3" :controls="false" size="small" class="num" /></div>
        </div>
        <h3 class="sub-title">剪力 V（kN）</h3>
        <div class="load-grid">
          <div class="field"><label class="lbl">VA 端支座</label>
            <el-input-number v-model="result.internal_forces.VA_max" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">VB左</label>
            <el-input-number v-model="result.internal_forces.VBl_min" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">VB右</label>
            <el-input-number v-model="result.internal_forces.VBr_max" :precision="3" :controls="false" size="small" class="num" /></div>
        </div>
      </section>

      <!-- 正截面配筋 -->
      <section class="block">
        <h2 class="block-title">正截面配筋（T 形，翼缘宽 bf）</h2>
        <el-table :data="result.reinforcement.flexure" size="small" class="compact-table" border>
          <el-table-column prop="name" label="截面" min-width="80" fixed="left" />
          <el-table-column prop="section_type" label="类型" min-width="130" />
          <el-table-column prop="width_used" label="计算宽" min-width="80" align="right" />
          <el-table-column prop="moment" label="M" min-width="90" align="right" />
          <el-table-column prop="h0" label="h0" min-width="60" align="right" />
          <el-table-column prop="alpha_s" label="αₛ" min-width="60" align="right" />
          <el-table-column prop="xi" label="ξ" min-width="60" align="right" />
          <el-table-column prop="as_required" label="As需" min-width="90" align="right" />
          <el-table-column label="As实" min-width="90">
            <template #default="{ row }"><el-input-number v-model="row.as_provided" :precision="0" :controls="false" size="small" class="num" /></template>
          </el-table-column>
          <el-table-column label="选筋" min-width="140">
            <template #default="{ row }">
              <span v-if="!row.selected_bar" class="muted">—</span>
              <span v-else class="bar-cell">
                <el-input-number :model-value="row.selected_bar.count" :controls="false" :min="1" size="small" class="bar-num" @update:model-value="(v:number|undefined)=>updateBar(row,'count',v)" />
                Φ
                <el-input-number :model-value="row.selected_bar.diameter" :controls="false" :min="1" size="small" class="bar-num" @update:model-value="(v:number|undefined)=>updateBar(row,'diameter',v)" />
              </span>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="80" align="center">
            <template #default="{ row }"><el-tag :type="reinfTagType(row.status)" size="small" effect="plain">{{ reinfLabel(row.status) }}</el-tag></template>
          </el-table-column>
        </el-table>
      </section>

      <!-- 斜截面箍筋与吊筋 -->
      <section class="block">
        <h2 class="block-title">斜截面箍筋与吊筋</h2>
        <div class="load-grid">
          <div class="field"><label class="lbl">最大剪力（kN）</label><span class="val">{{ result.reinforcement.shear.max_shear }}</span></div>
          <div class="field"><label class="lbl">Vc 混凝土受剪（kN）</label><span class="val">{{ result.reinforcement.shear.vc }}</span></div>
          <div class="field"><label class="lbl">Asv/s（mm²/mm）</label><span class="val">{{ result.reinforcement.shear.asv_s }}</span></div>
          <div class="field"><label class="lbl">推荐间距（mm）</label><span class="val">{{ result.reinforcement.shear.recommended_spacing }}</span></div>
          <div class="field"><label class="lbl">箍筋配筋率</label><span class="val">{{ result.reinforcement.shear.stirrup_ratio }}</span></div>
          <div class="field"><label class="lbl">吊筋所需面积（mm²）</label><span class="val">{{ result.reinforcement.shear.hanger_area }}</span></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { FolderOpen, Calculator } from '@lucide/vue'
import PageHeader from '../components/common/PageHeader.vue'
import EmptyState from '../components/common/EmptyState.vue'
import { useProject } from '../composables/useProject'
import { reinfLabel, reinfTagType } from '../composables/useReinfStatus'
import MainBeamDiagram from '../components/diagrams/MainBeamDiagram.vue'

const noProjectIcon = markRaw(FolderOpen)
const noCalcIcon = markRaw(Calculator)

const router = useRouter()
const { data, saving, isActive } = useProject()

interface BarBundle { count: number; diameter: number }
interface Flexure {
  name: string; moment: number; h0: number; section_type: string; width_used: number
  alpha_s: number; xi: number; as_required: number
  selected_bar: BarBundle | null; as_provided: number; status: string
}
interface Shear { max_shear: number; vc: number; asv_s: number; recommended_spacing: number; stirrup_ratio: number; hanger_area: number }
interface MainBeamResult {
  load: { from_beam_dead: number; self_weight: number; plaster: number; dead_load_standard: number; dead_load_design: number; live_load_standard: number; live_load_design: number }
  internal_forces: { M1_max: number; M2_max: number; M_B_min: number; M_C_min: number; VA_max: number; VBl_min: number; VBr_max: number }
  reinforcement: { flexure: Flexure[]; shear: Shear }
}

const result = computed<MainBeamResult>(() =>
  data.value?.main_beam.result as unknown as MainBeamResult ?? {} as MainBeamResult,
)
const mbReady = computed(() => data.value?.main_beam?.initialized === true)

/** 计算简图入参：主梁跨度由 L2 / main_beam_spans 重建（result 无 span 字段）。 */
const diagram = computed(() => {
  const s = data.value?.structure
  const r = data.value?.main_beam?.result as
    | { load?: { dead_load_design?: number; live_load_design?: number } }
    | undefined
  if (!s || s.L2 == null || s.main_beam_spans == null) return null
  if (s.column_width == null || s.main_beam_width == null || s.main_beam_height == null) return null
  if (r?.load?.dead_load_design == null || r?.load?.live_load_design == null) return null
  return {
    span: s.L2 / s.main_beam_spans,
    loadG: r.load.dead_load_design,
    loadQ: r.load.live_load_design,
    columnWidth: s.column_width,
    sectionSize: { b: s.main_beam_width, h: s.main_beam_height },
  }
})

function updateBar(row: Flexure, field: 'count' | 'diameter', v: number | undefined): void {
  if (!row.selected_bar || v == null) return
  row.selected_bar[field] = v
}
</script>

<style scoped>
.main-beam { width: 100%; }

/* 连续 sub-title 需要顶部间距与上一组拉开 */
.sub-title { margin: var(--space-3) 0 var(--space-2); font-size: var(--text-base); font-weight: 600; color: var(--muted-foreground); }
.sub-title:first-child { margin-top: 0; }
.save-state { font-size: var(--text-sm); color: var(--muted-foreground); }

.data .block:first-child { margin-top: 0; }

.load-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--space-2) var(--space-6); }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.lbl { font-size: var(--text-sm); color: var(--muted-foreground); }
.val { font-size: var(--text-md); }
.num { width: 100%; }
.num :deep(input) { text-align: left; }
.compact-table { font-size: var(--text-base); }
.compact-table :deep(.el-table__cell) { padding: var(--space-1) 0; }
.bar-cell { display: inline-flex; align-items: center; gap: var(--space-1); font-size: var(--text-base); color: var(--foreground); }
.bar-num { width: 56px; }
.bar-num :deep(input) { text-align: center; padding-left: var(--space-1); padding-right: var(--space-1); }
</style>
