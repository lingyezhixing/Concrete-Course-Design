<template>
  <div class="slab">
    <PageHeader title="板计算" subtitle="内力分析与配筋设计">
      <template #action>
        <span class="save-state">{{ saving ? '自动保存中…' : '已保存' }}</span>
      </template>
    </PageHeader>

    <!-- 守卫：无活动项目 -->
    <section v-if="!isActive()" class="block guard">
      <p class="muted">请先在开始页选择或新建项目</p>
      <el-button type="primary" @click="router.push('/')">前往开始页</el-button>
    </section>

    <!-- 守卫：未计算 -->
    <section v-else-if="!slabReady" class="block guard">
      <p class="muted">请先在参数页确认计算</p>
      <el-button type="primary" @click="router.push('/params')">前往参数页</el-button>
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
            <div class="field full">
              <label class="lbl">总荷载设计值（kN/m）</label>
              <el-input-number
                v-model="result.load.total_load"
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

        <!-- 内力 -->
        <section class="block">
          <h2 class="block-title">内力</h2>
          <h3 class="sub-title">弯矩 M（kN·m/m）</h3>
          <el-table
            :data="result.internal_forces.moments"
            size="small"
            class="compact-table"
            border
          >
            <el-table-column prop="name" label="截面" min-width="160" />
            <el-table-column label="弯矩值" min-width="140">
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

          <h3 class="sub-title">剪力 V（kN/m）</h3>
          <el-table
            :data="result.internal_forces.shears"
            size="small"
            class="compact-table"
            border
          >
            <el-table-column prop="name" label="截面" min-width="160" />
            <el-table-column label="剪力值" min-width="140">
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
            <el-table-column prop="name" label="截面" min-width="120" />
            <el-table-column prop="moment" label="弯矩 M" min-width="90" align="right" />
            <el-table-column prop="h0" label="h0" min-width="70" align="right" />
            <el-table-column prop="alpha_s" label="αₛ" min-width="70" align="right" />
            <el-table-column prop="xi" label="ξ" min-width="70" align="right" />
            <el-table-column prop="as_required" label="As需" min-width="90" align="right" />
            <el-table-column label="As实" min-width="100">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.as_provided"
                  :precision="0"
                  :controls="false"
                  size="small"
                  class="num"
                />
              </template>
            </el-table-column>
            <el-table-column label="选筋" min-width="160">
              <template #default="{ row }">
                <span v-if="!row.selected_bar" class="muted">—</span>
                <span v-else class="bar-cell">
                  Φ
                  <el-input-number
                    :model-value="row.selected_bar.diameter"
                    :controls="false"
                    size="small"
                    class="bar-num"
                    @update:model-value="
                      (v: number | undefined) => updateBar(row, 'diameter', v)
                    "
                  />
                  @
                  <el-input-number
                    :model-value="row.selected_bar.spacing"
                    :controls="false"
                    size="small"
                    class="bar-num"
                    @update:model-value="
                      (v: number | undefined) => updateBar(row, 'spacing', v)
                    "
                  />
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
        </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../components/common/PageHeader.vue'
import { useProject } from '../composables/useProject'

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
    total_load: number
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

/** 修改选筋子字段（diameter/spacing）。 */
function updateBar(
  row: ReinfSection,
  field: 'diameter' | 'spacing',
  v: number | undefined,
): void {
  if (!row.selected_bar || v == null) return
  row.selected_bar[field] = v
}

/** 配筋状态文案。 */
function reinfLabel(status: string): string {
  if (status === 'pass' || status === 'ok') return '满足'
  if (status === 'review') return '复核'
  if (status === 'fail' || status === 'insufficient') return '不足'
  return status
}
/** 配筋状态对应 el-tag 类型。 */
function reinfTagType(status: string): 'success' | 'warning' | 'danger' {
  if (status === 'pass' || status === 'ok' || status === '推荐') return 'success'
  if (status === 'review' || status === '建议复核') return 'danger'
  return 'danger'
}
</script>

<style scoped>
.slab {
  width: 100%;
}

/* 守卫 */
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
.sub-title {
  margin: 12px 0 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--muted-foreground);
}
.muted {
  color: var(--muted-foreground);
  font-size: 13px;
}
.save-state {
  font-size: 12px;
  color: var(--muted-foreground);
}

/* 守卫卡片 */
.guard {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 14px;
}
.guard .muted {
  margin: 0;
}

/* 4:1 布局 */
.split {
  display: grid;
  grid-template-columns: 4fr 1fr;
  gap: 16px;
  align-items: start;
}
.data .block:first-child {
  margin-top: 0;
}

/* 荷载/跨度网格 */
.load-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 24px;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.field.full {
  grid-column: 1 / -1;
}
.lbl {
  font-size: 12px;
  color: var(--muted-foreground);
}
.val {
  font-size: 14px;
}
.num {
  width: 100%;
}
.num :deep(input) {
  text-align: left;
}

/* 紧凑表格 */
.compact-table {
  font-size: 13px;
}
.compact-table :deep(.el-table__cell) {
  padding: 4px 0;
}
.bar-cell {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--foreground);
}
.bar-num {
  width: 56px;
}
.bar-num :deep(input) {
  text-align: center;
  padding-left: 4px;
  padding-right: 4px;
}

/* 复核清单 */
.checks {
  position: sticky;
  top: 16px;
}
.check-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.check-item {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}
.check-icon {
  font-size: 14px;
  line-height: 1.4;
  flex-shrink: 0;
}
.check-body {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.check-name {
  font-size: 13px;
  color: var(--foreground);
}
.check-detail {
  font-size: 12px;
  line-height: 1.4;
  word-break: break-word;
}
.check-detail .clause {
  color: var(--muted-foreground);
  margin-right: 4px;
}
.empty-checks {
  margin: 0;
}

/* 响应式：窄屏堆叠 */
@media (max-width: 960px) {
  .split {
    grid-template-columns: 1fr;
  }
  .checks {
    position: static;
  }
}
</style>
