<template>
  <div v-if="layout" class="uniform-diagram">
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="diagram-svg"
      role="img"
      :aria-label="ariaLabel"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- 均布荷载顶线 + 标签 -->
      <text :x="W / 2" :y="LOAD_TOP_Y - 8" class="load-text" text-anchor="middle">
        g′ + q′ = {{ totalLoad }} kN/m
      </text>
      <line
        :x1="pad" :y1="LOAD_TOP_Y" :x2="W - pad" :y2="LOAD_TOP_Y"
        class="load"
      />
      <g class="load">
        <g v-for="(x, i) in layout.loadArrows" :key="`arrow-${i}`">
          <line :x1="x" :y1="LOAD_TOP_Y + 1" :x2="x" :y2="BEAM_Y - 5" />
          <polygon
            :points="`${x - 3},${BEAM_Y - 9} ${x + 3},${BEAM_Y - 9} ${x},${BEAM_Y - 3}`"
          />
        </g>
      </g>

      <!-- 五跨等效：中间等效跨高亮 -->
      <rect
        v-if="equivSpan"
        :x="equivSpan.x0"
        :y="BEAM_Y - 7"
        :width="equivSpan.x1 - equivSpan.x0"
        :height="BEAM_H + 14"
        class="equiv-highlight"
      />

      <!-- 梁 / 板带 -->
      <rect
        :x="pad" :y="BEAM_Y" :width="W - 2 * pad" :height="BEAM_H"
        class="member"
      />

      <!-- 支座（铰支 + 地面斜线） -->
      <g v-for="s in layout.supports" :key="`sup-${s.index}`" class="support">
        <polygon
          :points="`${s.x},${BEAM_Y + BEAM_H} ${s.x - 8},${BEAM_Y + BEAM_H + 13} ${s.x + 8},${BEAM_Y + BEAM_H + 13}`"
        />
        <line
          :x1="s.x - 12" :y1="BEAM_Y + BEAM_H + 15"
          :x2="s.x + 12" :y2="BEAM_Y + BEAM_H + 15"
        />
        <line
          :x1="s.x - 10" :y1="BEAM_Y + BEAM_H + 15"
          :x2="s.x - 6" :y2="BEAM_Y + BEAM_H + 19"
        />
        <line
          :x1="s.x - 4" :y1="BEAM_Y + BEAM_H + 15"
          :x2="s.x" :y2="BEAM_Y + BEAM_H + 19"
        />
        <line
          :x1="s.x + 2" :y1="BEAM_Y + BEAM_H + 15"
          :x2="s.x + 6" :y2="BEAM_Y + BEAM_H + 19"
        />
      </g>

      <!-- 跨度标注 -->
      <text
        v-for="(sp, i) in layout.spans"
        :key="`dim-${i}`"
        :x="sp.cx"
        :y="DIM_Y"
        class="dim-text"
        :class="{ equiv: sp.isEquiv }"
        text-anchor="middle"
      >
        {{ sp.label }}
      </text>

      <!-- 等效说明 -->
      <text
        v-if="layout.isEquiv"
        :x="W / 2" :y="EQUIV_NOTE_Y"
        class="equiv-note" text-anchor="middle"
      >
        {{ layout.equivNote }}
      </text>

      <!-- 截面缩略 + 角注 -->
      <g :transform="`translate(${pad + 4}, ${NOTE_Y - 26})`">
        <!-- 次梁：T 形截面 -->
        <template v-if="sectionType === 'beam'">
          <rect x="0" y="0" width="48" height="7" class="section-fill" />
          <rect x="16" y="7" width="16" height="22" class="section-fill" />
        </template>
        <!-- 板：板带剖面 -->
        <template v-else>
          <rect x="0" y="14" width="48" height="7" class="section-fill" />
        </template>
      </g>
      <text :x="pad + 60" :y="NOTE_Y - 12" class="note">{{ sectionLabel }}</text>
      <text :x="pad + 60" :y="NOTE_Y + 2" class="note">
        {{ sectionType === 'beam' ? '铰支于主梁 / 墙 · 跨中按 T 形、支座按矩形' : '板带宽 1 m · 铰支于次梁 / 墙' }}
      </text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import {
  DEFAULT_PAD,
  DEFAULT_WIDTH,
  layoutUniformBeam,
  type UniformBeamLayout,
} from '../../composables/useBeamLayout'

interface Props {
  /** 原始跨数（>5 触发五跨等效） */
  rawSpans: number
  /** 边跨计算跨度 l₀（m） */
  edgeSpan: number
  /** 中跨计算跨度 l₀（m） */
  midSpan: number
  /** 折算恒载 g′（kN/m） */
  loadDead: number
  /** 折算活载 q′（kN/m） */
  loadLive: number
  /** 截面类型：板 / 次梁 */
  sectionType: 'slab' | 'beam'
  /** 截面尺寸：板 { h }，次梁 { b, h }（mm） */
  sectionSize: { h: number; b?: number }
}

const props = defineProps<Props>()

// viewBox 常量（横向由布局函数决定，纵向在此固定）
const W = DEFAULT_WIDTH
const pad = DEFAULT_PAD
const H = 168
const LOAD_TOP_Y = 22
const BEAM_Y = 56
const BEAM_H = 5
const DIM_Y = 92
const EQUIV_NOTE_Y = 112
const NOTE_Y = 150

const layout = computed<UniformBeamLayout | null>(() =>
  layoutUniformBeam(props.rawSpans, props.edgeSpan, props.midSpan),
)

const equivSpan = computed(() => layout.value?.spans.find((s) => s.isEquiv) ?? null)

const totalLoad = computed(() => fmt(props.loadDead + props.loadLive))

const sectionLabel = computed(() => {
  const { h, b } = props.sectionSize
  return props.sectionType === 'beam' && b != null
    ? `T 形截面  b = ${fmt0(b)} × h = ${fmt0(h)} mm`
    : `板厚  h = ${fmt0(h)} mm`
})

const ariaLabel = computed(() =>
  props.sectionType === 'beam' ? '次梁计算简图' : '板计算简图',
)

function fmt(n: number): string {
  return Number.isFinite(n) ? n.toFixed(2) : '—'
}
function fmt0(n: number): string {
  return Number.isFinite(n) ? String(Math.round(n)) : '—'
}
</script>

<style scoped>
.uniform-diagram {
  width: 100%;
}
.diagram-svg {
  display: block;
  width: 100%;
  height: auto;
  max-width: 640px;
  margin: 0 auto;
  overflow: visible;
}

/* 梁 / 板带 */
.member {
  fill: var(--foreground);
}

/* 均布荷载 */
.load {
  stroke: var(--primary);
  fill: var(--primary);
  stroke-width: 1.3;
}
.load-text {
  fill: var(--primary);
  font-size: var(--text-xs);
}

/* 支座 + 地面 */
.support polygon {
  fill: var(--muted-foreground);
}
.support line {
  stroke: var(--muted-foreground);
  stroke-width: 1;
}

/* 跨度标注 */
.dim-text {
  fill: var(--muted-foreground);
  font-size: var(--text-xs);
}
.dim-text.equiv {
  fill: var(--warning);
  font-weight: 600;
}

/* 等效高亮 */
.equiv-highlight {
  fill: color-mix(in srgb, var(--warning) 18%, transparent);
  stroke: var(--warning);
  stroke-width: 1.2;
  stroke-dasharray: 4 3;
}
.equiv-note {
  fill: var(--warning);
  font-size: var(--text-xs);
}

/* 截面缩略 */
.section-fill {
  fill: color-mix(in srgb, var(--foreground) 12%, transparent);
  stroke: var(--muted-foreground);
  stroke-width: 1;
}

/* 角注 */
.note {
  fill: var(--muted-foreground);
  font-size: var(--text-xs);
}

/* 窄屏：简图允许横向滚动，避免标注挤压 */
@media (max-width: 560px) {
  .uniform-diagram {
    overflow-x: auto;
  }
  .diagram-svg {
    min-width: 520px;
  }
}
</style>
