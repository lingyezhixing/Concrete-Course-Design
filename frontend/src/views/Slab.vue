<template>
  <div class="slab">
    <PageHeader title="板计算" subtitle="内力分析与配筋设计">
      <template #action>
        <span class="save-state">{{ saving ? '自动保存中…' : '已保存' }}</span>
      </template>
    </PageHeader>

    <!-- 守卫：无活动项目 -->
    <section v-if="!isActive()" class="block">
      <EmptyState
        :icon="noProjectIcon"
        title="尚未选择项目"
        description="请先在开始页选择或新建一个项目。"
      >
        <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
      </EmptyState>
    </section>

    <!-- 守卫：未计算 -->
    <section v-else-if="!slabReady" class="block">
      <EmptyState
        :icon="noCalcIcon"
        title="尚未计算"
        description="请先在参数页填写参数并确认计算。"
      >
        <el-button type="primary" @click="router.push('/params')">前往参数页</el-button>
      </EmptyState>
    </section>

    <!-- 主体：全宽可编辑结果 -->
    <div v-else class="data">
        <!-- 荷载 -->
        <section class="block">
          <h2 class="block-title">荷载</h2>
          <div class="load-grid">
            <div class="field">
              <label class="lbl">水磨石面层 g₁（kN/m²）</label>
              <span class="val muted">{{ result.load.terrazzo }}</span>
            </div>
            <div class="field">
              <label class="lbl">钢筋混凝土板 g₂（kN/m²）</label>
              <span class="val muted">{{ result.load.concrete }}</span>
            </div>
            <div class="field">
              <label class="lbl">板底抹灰 g₃（kN/m²）</label>
              <span class="val muted">{{ result.load.plaster }}</span>
            </div>
            <div class="field">
              <label class="lbl">恒载标准值 gₖ（kN/m²）</label>
              <el-input-number
                v-model="result.load.dead_load_standard"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
            <div class="field">
              <label class="lbl">恒载设计值 g（kN/m²）</label>
              <el-input-number
                v-model="result.load.dead_load_design"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
            <div class="field">
              <label class="lbl">活载标准值 qₖ（kN/m²）</label>
              <el-input-number
                v-model="result.load.live_load_standard"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
            <div class="field">
              <label class="lbl">活载设计值 q（kN/m²）</label>
              <el-input-number
                v-model="result.load.live_load_design"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
            <!-- 折算荷载 -->
            <div class="field">
              <label class="lbl">折算恒荷载 g（kN/m）</label>
              <el-input-number
                v-model="result.converted.converted_dead"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
            <div class="field">
              <label class="lbl">折算活荷载 q（kN/m）</label>
              <el-input-number
                v-model="result.converted.converted_live"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
          </div>
        </section>

        <!-- 计算跨度 -->
        <section class="block">
          <h2 class="block-title">计算跨度</h2>
          <div class="load-grid">
            <div class="field">
              <label class="lbl">中间跨 l₀（m）</label>
              <el-input-number
                v-model="result.span.middle_span"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
            <div class="field">
              <label class="lbl">边跨 l₀（m）</label>
              <el-input-number
                v-model="result.span.edge_span"
                :precision="3"
                :controls="false"
                size="small"
                class="num"
              />
            </div>
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
              <h3 class="sub-title">弯矩 M（kN·m/m）</h3>
              <el-table
                :data="result.internal_forces.moments"
                size="small"
                class="compact-table"
                border
              >
                <el-table-column prop="name" label="截面" min-width="140" />
                <el-table-column label="弯矩值" min-width="120">
                  <template #default="{ row }">
                    <el-input-number
                      v-model="row.value"
                      :precision="3"
                      :controls="false"
                      size="small"
                      class="num"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <div class="force-table">
              <h3 class="sub-title">剪力 V（kN/m）</h3>
              <el-table
                :data="result.internal_forces.shears"
                size="small"
                class="compact-table"
                border
              >
                <el-table-column prop="name" label="截面" min-width="140" />
                <el-table-column label="剪力值" min-width="120">
                  <template #default="{ row }">
                    <el-input-number
                      v-model="row.value"
                      :precision="3"
                      :controls="false"
                      size="small"
                      class="num"
                    />
                  </template>
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

        <!-- 配筋 -->
        <section class="block">
          <h2 class="block-title">配筋</h2>
          <el-table
            :data="result.reinforcement.sections"
            size="small"
            class="compact-table"
            border
          >
            <el-table-column prop="name" label="截面" min-width="120" fixed="left" />
            <el-table-column prop="moment" label="弯矩 M" min-width="90" align="right" />
            <el-table-column prop="h0" label="h0" min-width="70" align="right" />
            <el-table-column prop="alpha_s" label="αₛ" min-width="70" align="right" />
            <el-table-column prop="xi" label="ξ" min-width="70" align="right" />
            <el-table-column prop="as_required" label="As需" min-width="90" align="right" />
            <el-table-column label="As实" min-width="100">
              <template #default="{ row }">
                <span class="val">{{ asProvided(row) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="选筋" min-width="180">
              <template #default="{ row }">
                <span v-if="!row.selected_bar" class="muted">—</span>
                <span v-else class="bar-cell">
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
                  <span class="phi">@</span>
                  <el-select
                    :model-value="row.selected_bar.spacing"
                    size="small"
                    class="bar-sel"
                    @update:model-value="(v: number) => onSpacingChange(row, v)"
                  >
                    <el-option
                      v-for="s in spaceOpts(row)"
                      :key="s"
                      :label="String(s)"
                      :value="s"
                    />
                  </el-select>
                </span>
              </template>
            </el-table-column>
            <el-table-column label="状态" min-width="90" align="center">
              <template #default="{ row }">
                <el-tag
                  :type="reinfTagType(row.status)"
                  size="small"
                  effect="plain"
                >
                  {{ reinfLabel(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
          <div v-if="rebarSections.length" style="margin-top: var(--space-4);">
            <h3 class="sub-title">截面配筋简图</h3>
            <SectionRebarDiagram :sections="rebarSections" />
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
  reinfStatus,
  slabAreaPerMeter,
  slabDiameterOptions,
  slabSpacingOptions,
} from '../config/rebarTable'
import UniformLoadBeamDiagram from '../components/diagrams/UniformLoadBeamDiagram.vue'
import SectionRebarDiagram from '../components/diagrams/SectionRebarDiagram.vue'
import InternalForceDiagram from '../components/diagrams/InternalForceDiagram.vue'

const noProjectIcon = markRaw(FolderOpen)
const noCalcIcon = markRaw(Calculator)

const router = useRouter()
const { data, saving, isActive } = useProject()

/** 本地结果类型（后端 SlabFullResult 形状）。result 字段在 API 层为 Record<string,unknown>，
 *  这里精确化以便模板获得类型安全。 */
interface SelectedBar {
  diameter: number
  spacing: number
}
interface NamedValue {
  name: string
  value: number
}
interface ReinfSection {
  name: string
  moment: number
  h0: number
  alpha_s: number
  xi: number
  as_required: number
  selected_bar: SelectedBar | null
  as_provided: number
  status: string
  candidates: unknown
}
interface SlabResult {
  load: {
    terrazzo: number
    concrete: number
    plaster: number
    dead_load_standard: number
    dead_load_design: number
    live_load_standard: number
    live_load_design: number
  }
  span: { middle_span: number; edge_span: number }
  net_span: { middle_net: number; edge_net: number }
  converted: { converted_dead: number; converted_live: number }
  internal_forces: { moments: NamedValue[]; shears: NamedValue[] }
  reinforcement: { sections: ReinfSection[] }
}

/** 结果对象（守卫 slabReady 确保渲染时已初始化，type-safe cast 兼容空状态）。 */
const result = computed<SlabResult>(() =>
  data.value?.slab.result as unknown as SlabResult ?? {} as SlabResult,
)
const slabReady = computed(() => data.value?.slab?.initialized === true)

/** 计算简图入参：跨数 / 跨度 / 折算荷载齐备时才渲染。 */
const diagram = computed(() => {
  const s = data.value?.structure
  const r = data.value?.slab?.result as
    | {
        span?: { edge_span?: number; middle_span?: number }
        converted?: { converted_dead?: number; converted_live?: number }
      }
    | undefined
  if (!s || s.slab_spans == null || s.slab_thickness == null) return null
  if (r?.span?.edge_span == null || r?.span?.middle_span == null) return null
  if (r.converted?.converted_dead == null || r.converted?.converted_live == null) return null
  return {
    rawSpans: s.slab_spans,
    edgeSpan: r.span.edge_span,
    midSpan: r.span.middle_span,
    loadDead: r.converted.converted_dead,
    loadLive: r.converted.converted_live,
    sectionType: 'slab' as const,
    sectionSize: { h: s.slab_thickness },
  }
})

/** 截面配筋简图数据（板：板带 + Φd@s）。 */
const rebarSections = computed(() => {
  const s = data.value?.structure
  const r = data.value?.slab?.result as
    | { reinforcement?: { sections?: ReinfSection[] } }
    | undefined
  if (!s || !r?.reinforcement?.sections) return []
  return r.reinforcement.sections.map((sec) => ({
    name: sec.name,
    shape: 'slab' as const,
    b: 1000,
    h: s.slab_thickness ?? 0,
    bar: {
      diameter: sec.selected_bar?.diameter ?? 0,
      spacing: sec.selected_bar?.spacing ?? 0,
    },
  }))
})

/** 弯矩 / 剪力图入参：跨数 / 跨度 / 内力齐备时才渲染。 */
const mvData = computed(() => {
  const s = data.value?.structure
  const r = data.value?.slab?.result as
    | {
        span?: { edge_span?: number; middle_span?: number }
        internal_forces?: { moments?: NamedValue[]; shears?: NamedValue[] }
      }
    | undefined
  if (!s || s.slab_spans == null) return null
  if (r?.span?.edge_span == null || r?.span?.middle_span == null) return null
  if (!r.internal_forces?.moments?.length || !r.internal_forces?.shears?.length) return null
  return {
    moments: r.internal_forces.moments,
    shears: r.internal_forces.shears,
    rawSpans: s.slab_spans,
    edgeSpan: r.span.edge_span,
    midSpan: r.span.middle_span,
  }
})

/** 给定截面的可选直径（至少存在一个间距满足 As）。 */
function diaOpts(row: ReinfSection): number[] {
  return slabDiameterOptions(row.as_required)
}

/** 给定直径下可选间距（满足 As ≥ As需）。 */
function spaceOpts(row: ReinfSection): number[] {
  if (!row.selected_bar) return []
  return slabSpacingOptions(row.selected_bar.diameter, row.as_required)
}

/** 实配面积（由选筋实时派生）。 */
function asProvided(row: ReinfSection): number {
  if (!row.selected_bar) return 0
  return Math.round(
    slabAreaPerMeter(row.selected_bar.diameter, row.selected_bar.spacing),
  )
}

/** 同步实配面积与状态到行（供保存与表格展示）。 */
function syncRow(row: ReinfSection): void {
  if (!row.selected_bar) return
  row.as_provided = asProvided(row)
  row.status = reinfStatus(row.as_required, row.as_provided)
}

/** 直径变更：若当前间距不再合法则回落到第一个合法间距。 */
function onDiameterChange(row: ReinfSection, d: number): void {
  if (!row.selected_bar) return
  row.selected_bar.diameter = d
  const opts = spaceOpts(row)
  if (!opts.includes(row.selected_bar.spacing)) {
    row.selected_bar.spacing = opts[0] ?? row.selected_bar.spacing
  }
  syncRow(row)
}

/** 间距变更。 */
function onSpacingChange(row: ReinfSection, s: number): void {
  if (!row.selected_bar) return
  row.selected_bar.spacing = s
  syncRow(row)
}
</script>

<style scoped>
.slab {
  width: 100%;
}

.sub-title {
  margin: 0 0 var(--space-2);
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--muted-foreground);
}
.force-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}
.force-table {
  min-width: 0;
}
.save-state {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
}

.data .block:first-child {
  margin-top: 0;
}

/* 荷载/跨度网格 */
.load-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-2) var(--space-6);
}
.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}
.field.full {
  grid-column: 1 / -1;
}
.lbl {
  font-size: var(--text-sm);
  color: var(--muted-foreground);
}
.val {
  font-size: var(--text-md);
}
.num {
  width: 100%;
}
.num :deep(input) {
  text-align: left;
}

/* 紧凑表格 */
.compact-table {
  font-size: var(--text-base);
}
.compact-table :deep(.el-table__cell) {
  padding: var(--space-1) 0;
}
.bar-cell {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-base);
  color: var(--foreground);
}
.bar-num {
  width: 56px;
}
.bar-num :deep(input) {
  text-align: center;
  padding-left: var(--space-1);
  padding-right: var(--space-1);
}
.bar-sel { width: 64px; }
.bar-sel :deep(.el-select__wrapper) { padding: 0 var(--space-1); }
.phi { color: var(--muted-foreground); }

/* 响应式：窄屏堆叠 */
@media (max-width: 960px) {
  .force-split {
    grid-template-columns: 1fr;
  }
}
</style>
