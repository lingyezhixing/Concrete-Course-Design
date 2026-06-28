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

function updateBar(row: Flexure, field: 'count' | 'diameter', v: number | undefined): void {
  if (!row.selected_bar || v == null) return
  row.selected_bar[field] = v
}
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

@media (max-width: 960px) {
  .force-split { grid-template-columns: 1fr; }
}
</style>
