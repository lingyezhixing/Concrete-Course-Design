<template>
  <div class="beam">
    <PageHeader title="次梁计算" subtitle="内力分析与配筋设计">
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
    <section v-else-if="!beamReady" class="block">
      <EmptyState
        :icon="noCalcIcon"
        title="尚未计算"
        description="请先在参数页填写参数并确认计算。"
      >
        <el-button type="primary" @click="router.push('/params')">前往参数页</el-button>
      </EmptyState>
    </section>

    <div v-else class="data">
      <!-- 荷载 -->
      <section class="block">
        <h2 class="block-title">荷载</h2>
        <div class="load-grid">
          <div class="field"><label class="lbl">板传来恒载（kN/m）</label><span class="val muted">{{ result.load.from_slab_dead }}</span></div>
          <div class="field"><label class="lbl">次梁自重（kN/m）</label><span class="val muted">{{ result.load.self_weight }}</span></div>
          <div class="field"><label class="lbl">次梁粉刷（kN/m）</label><span class="val muted">{{ result.load.plaster }}</span></div>
          <div class="field"><label class="lbl">恒载标准值 gₖ（kN/m）</label>
            <el-input-number v-model="result.load.dead_load_standard" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">恒载设计值 g（kN/m）</label>
            <el-input-number v-model="result.load.dead_load_design" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">活载标准值 qₖ（kN/m）</label>
            <el-input-number v-model="result.load.live_load_standard" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">活载设计值 q（kN/m）</label>
            <el-input-number v-model="result.load.live_load_design" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field full"><label class="lbl">折算恒载 g'（kN/m）</label>
            <el-input-number v-model="result.converted.converted_dead" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field full"><label class="lbl">折算活载 q'（kN/m）</label>
            <el-input-number v-model="result.converted.converted_live" :precision="3" :controls="false" size="small" class="num" /></div>
        </div>
      </section>

      <!-- 计算跨度 -->
      <section class="block">
        <h2 class="block-title">计算跨度</h2>
        <div class="load-grid">
          <div class="field"><label class="lbl">中间跨 l₀（m）</label>
            <el-input-number v-model="result.span.middle_span" :precision="3" :controls="false" size="small" class="num" /></div>
          <div class="field"><label class="lbl">边跨 l₀（m）</label>
            <el-input-number v-model="result.span.edge_span" :precision="3" :controls="false" size="small" class="num" /></div>
        </div>
      </section>

      <!-- 计算简图 -->
      <section v-if="diagram" class="block">
        <h2 class="block-title">计算简图</h2>
        <UniformLoadBeamDiagram v-bind="diagram" />
      </section>

      <!-- 内力 -->
      <section class="block">
        <h2 class="block-title">内力</h2>
        <div class="force-split">
          <div class="force-table">
            <h3 class="sub-title">弯矩 M（kN·m）</h3>
            <el-table :data="result.internal_forces.moments" size="small" class="compact-table" border>
              <el-table-column prop="name" label="截面" min-width="120" />
              <el-table-column label="弯矩值" min-width="140">
                <template #default="{ row }"><el-input-number v-model="row.value" :precision="3" :controls="false" size="small" class="num" /></template>
              </el-table-column>
            </el-table>
          </div>
          <div class="force-table">
            <h3 class="sub-title">剪力 V（kN）</h3>
            <el-table :data="result.internal_forces.shears" size="small" class="compact-table" border>
              <el-table-column prop="name" label="截面" min-width="120" />
              <el-table-column label="剪力值" min-width="140">
                <template #default="{ row }"><el-input-number v-model="row.value" :precision="3" :controls="false" size="small" class="num" /></template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </section>

      <!-- 弯矩图 / 剪力图 -->
      <section v-if="mvData" class="block">
        <h2 class="block-title">弯矩图 / 剪力图</h2>
        <InternalForceDiagram v-bind="mvData" />
      </section>

      <!-- 抵抗弯矩图 -->
      <section v-if="rmData" class="block">
        <h2 class="block-title">抵抗弯矩图</h2>
        <ResistingMomentDiagram v-bind="rmData" />
      </section>

      <!-- 正截面配筋 -->
      <section class="block">
        <h2 class="block-title">正截面配筋</h2>
        <el-table :data="result.reinforcement.flexure" size="small" class="compact-table" border>
          <el-table-column prop="name" label="截面" min-width="80" fixed="left" />
          <el-table-column prop="section_type" label="类型" min-width="110" />
          <el-table-column prop="width_used" label="计算宽" min-width="80" align="right" />
          <el-table-column prop="moment" label="M" min-width="80" align="right" />
          <el-table-column prop="h0" label="h0" min-width="60" align="right" />
          <el-table-column prop="alpha_s" label="αₛ" min-width="60" align="right" />
          <el-table-column prop="xi" label="ξ" min-width="60" align="right" />
          <el-table-column prop="as_required" label="As需" min-width="80" align="right" />
          <el-table-column label="As实" min-width="90">
            <template #default="{ row }"><span class="val">{{ asProvided(row) }}</span></template>
          </el-table-column>
          <el-table-column label="选筋" min-width="180">
            <template #default="{ row }">
              <span v-if="!row.selected_bar" class="muted">—</span>
              <span v-else class="bar-cell">
                <el-select
                  :model-value="row.selected_bar.count"
                  size="small"
                  class="bar-sel"
                  @update:model-value="(v: number) => onCountChange(row, v)"
                >
                  <el-option v-for="n in countOpts" :key="n" :label="String(n)" :value="n" />
                </el-select>
                <span class="phi">Φ</span>
                <el-select
                  :model-value="row.selected_bar.diameter"
                  size="small"
                  class="bar-sel"
                  @update:model-value="(v: number) => onDiameterChange(row, v)"
                >
                  <el-option
                    v-for="d in diaOpts(row)"
                    :key="d"
                    :label="String(d)"
                    :value="d"
                  />
                </el-select>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="80" align="center">
            <template #default="{ row }"><el-tag :type="reinfTagType(row.status)" size="small" effect="plain">{{ reinfLabel(row.status) }}</el-tag></template>
          </el-table-column>
        </el-table>
        <div v-if="rebarSections.length" style="margin-top: var(--space-4);">
          <h3 class="sub-title">截面配筋简图</h3>
          <SectionRebarDiagram :sections="rebarSections" />
        </div>
      </section>

      <!-- 斜截面箍筋 -->
      <section class="block">
        <h2 class="block-title">斜截面箍筋</h2>
        <div class="load-grid">
          <div class="field"><label class="lbl">最大剪力（kN）</label><span class="val">{{ result.reinforcement.shear.max_shear }}</span></div>
          <div class="field"><label class="lbl">Vc 混凝土受剪（kN）</label><span class="val">{{ result.reinforcement.shear.vc }}</span></div>
          <div class="field"><label class="lbl">Asv/s（mm²/mm）</label><span class="val">{{ result.reinforcement.shear.asv_s }}</span></div>
          <div class="field"><label class="lbl">推荐间距（mm）</label><span class="val">{{ result.reinforcement.shear.recommended_spacing }}</span></div>
          <div class="field"><label class="lbl">箍筋配筋率</label><span class="val">{{ result.reinforcement.shear.stirrup_ratio }}</span></div>
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
import {
  barArea,
  countOptions,
  diameterOptions,
  reinfStatus,
} from '../config/rebarTable'
import UniformLoadBeamDiagram from '../components/diagrams/UniformLoadBeamDiagram.vue'
import SectionRebarDiagram from '../components/diagrams/SectionRebarDiagram.vue'
import InternalForceDiagram from '../components/diagrams/InternalForceDiagram.vue'
import ResistingMomentDiagram from '../components/diagrams/ResistingMomentDiagram.vue'

const noProjectIcon = markRaw(FolderOpen)
const noCalcIcon = markRaw(Calculator)

const router = useRouter()
const { data, saving, isActive } = useProject()

interface BarBundle { count: number; diameter: number }
interface NamedValue { name: string; value: number }
interface Flexure {
  name: string; moment: number; h0: number; section_type: string; width_used: number
  alpha_s: number; xi: number; as_required: number
  selected_bar: BarBundle | null; as_provided: number; status: string
}
interface Shear { max_shear: number; h0: number; vc: number; asv_s: number; recommended_spacing: number; stirrup_ratio: number }
interface BeamResult {
  load: { from_slab_dead: number; self_weight: number; plaster: number; dead_load_standard: number; dead_load_design: number; live_load_standard: number; live_load_design: number }
  span: { middle_span: number; edge_span: number }
  converted: { converted_dead: number; converted_live: number }
  internal_forces: { moments: NamedValue[]; shears: NamedValue[] }
  reinforcement: { flexure: Flexure[]; shear: Shear }
}

const result = computed<BeamResult>(() =>
  data.value?.beam.result as unknown as BeamResult ?? {} as BeamResult,
)
const beamReady = computed(() => data.value?.beam?.initialized === true)

/** 计算简图入参：跨数 / 跨度 / 折算荷载 / 截面齐备时才渲染。 */
const diagram = computed(() => {
  const s = data.value?.structure
  const r = data.value?.beam?.result as
    | {
        span?: { edge_span?: number; middle_span?: number }
        converted?: { converted_dead?: number; converted_live?: number }
      }
    | undefined
  if (!s || s.beam_spans == null || s.beam_width == null || s.beam_height == null) return null
  if (r?.span?.edge_span == null || r?.span?.middle_span == null) return null
  if (r.converted?.converted_dead == null || r.converted?.converted_live == null) return null
  return {
    rawSpans: s.beam_spans,
    edgeSpan: r.span.edge_span,
    midSpan: r.span.middle_span,
    loadDead: r.converted.converted_dead,
    loadLive: r.converted.converted_live,
    sectionType: 'beam' as const,
    sectionSize: { b: s.beam_width, h: s.beam_height },
  }
})

/** 截面配筋简图数据（次梁：T 形 / 矩形 + nΦd）。 */
const rebarSections = computed(() => {
  const s = data.value?.structure
  const r = data.value?.beam?.result as
    | { reinforcement?: { flexure?: Flexure[] } }
    | undefined
  if (!s || !r?.reinforcement?.flexure) return []
  return r.reinforcement.flexure.map((f) => ({
    name: f.name,
    shape: (f.section_type?.includes('T') ? 't' : 'rect') as 't' | 'rect',
    b: s.beam_width ?? 0,
    h: s.beam_height ?? 0,
    bar: { diameter: f.selected_bar?.diameter ?? 0, count: f.selected_bar?.count ?? 0 },
  }))
})

/** 梁宽（用于下拉候选过滤）。 */
const beamWidth = computed(() => data.value?.structure?.beam_width ?? 200)

/** 可选根数列表。 */
const countOpts = computed(() => countOptions(beamWidth.value))

/** 给定截面的可选直径列表（依当前根数与 As需 过滤）。 */
function diaOpts(row: Flexure): number[] {
  if (!row.selected_bar) return []
  return diameterOptions(beamWidth.value, row.selected_bar.count, row.as_required)
}

/** 实配面积（由选筋实时派生）。 */
function asProvided(row: Flexure): number {
  if (!row.selected_bar) return 0
  return Math.round(barArea(row.selected_bar.diameter, row.selected_bar.count))
}

/** 同步实配面积与状态到行（供保存与表格展示）。 */
function syncRow(row: Flexure): void {
  if (!row.selected_bar) return
  row.as_provided = asProvided(row)
  row.status = reinfStatus(row.as_required, row.as_provided)
}

/** 根数变更：若当前直径不再合法则回落到第一个合法直径。 */
function onCountChange(row: Flexure, n: number): void {
  if (!row.selected_bar) return
  row.selected_bar.count = n
  const opts = diaOpts(row)
  if (!opts.includes(row.selected_bar.diameter)) {
    row.selected_bar.diameter = opts[0] ?? row.selected_bar.diameter
  }
  syncRow(row)
}

/** 直径变更。 */
function onDiameterChange(row: Flexure, d: number): void {
  if (!row.selected_bar) return
  row.selected_bar.diameter = d
  syncRow(row)
}

/** 弯矩 / 剪力图入参。 */
const mvData = computed(() => {
  const s = data.value?.structure
  const r = data.value?.beam?.result as
    | {
        span?: { edge_span?: number; middle_span?: number }
        internal_forces?: { moments?: NamedValue[]; shears?: NamedValue[] }
      }
    | undefined
  if (!s || s.beam_spans == null) return null
  if (r?.span?.edge_span == null || r?.span?.middle_span == null) return null
  if (!r.internal_forces?.moments?.length || !r.internal_forces?.shears?.length) return null
  return {
    moments: r.internal_forces.moments,
    shears: r.internal_forces.shears,
    rawSpans: s.beam_spans,
    edgeSpan: r.span.edge_span,
    midSpan: r.span.middle_span,
  }
})

/** 抵抗弯矩图入参：弯矩控制点 + 跨度 + 各截面配筋（as_provided/h0/width_used）。 */
const rmData = computed(() => {
  const s = data.value?.structure
  const r = data.value?.beam?.result as
    | {
        span?: { edge_span?: number; middle_span?: number }
        internal_forces?: { moments?: NamedValue[] }
        reinforcement?: { flexure?: Flexure[] }
      }
    | undefined
  if (!s || s.beam_spans == null) return null
  if (r?.span?.edge_span == null || r?.span?.middle_span == null) return null
  if (!r.internal_forces?.moments?.length) return null
  if (!r.reinforcement?.flexure?.length) return null
  return {
    moments: r.internal_forces.moments,
    rawSpans: s.beam_spans,
    edgeSpan: r.span.edge_span,
    midSpan: r.span.middle_span,
    flexure: r.reinforcement.flexure.map((f) => ({
      name: f.name, as_provided: f.as_provided, h0: f.h0, width_used: f.width_used,
    })),
  }
})
</script>

<style scoped>
.beam { width: 100%; }

.sub-title { margin: 0 0 var(--space-2); font-size: var(--text-base); font-weight: 600; color: var(--muted-foreground); }
.force-split { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-4); }
.force-table { min-width: 0; }
.save-state { font-size: var(--text-sm); color: var(--muted-foreground); }

.data .block:first-child { margin-top: 0; }

.load-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-2) var(--space-6); }
.field { display: flex; flex-direction: column; gap: var(--space-1); }
.field.full { grid-column: 1 / -1; }
.lbl { font-size: var(--text-sm); color: var(--muted-foreground); }
.val { font-size: var(--text-md); }
.num { width: 100%; }
.num :deep(input) { text-align: left; }
.compact-table { font-size: var(--text-base); }
.compact-table :deep(.el-table__cell) { padding: var(--space-1) 0; }
.bar-cell { display: inline-flex; align-items: center; gap: var(--space-1); font-size: var(--text-base); color: var(--foreground); }
.bar-num { width: 56px; }
.bar-num :deep(input) { text-align: center; padding-left: var(--space-1); padding-right: var(--space-1); }
.bar-sel { width: 64px; }
.bar-sel :deep(.el-select__wrapper) { padding: 0 var(--space-1); }
.phi { color: var(--muted-foreground); }

@media (max-width: 960px) {
  .force-split { grid-template-columns: 1fr; }
}
</style>
