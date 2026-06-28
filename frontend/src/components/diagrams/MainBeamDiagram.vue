<template>
  <div class="main-beam-diagram">
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="diagram-svg"
      role="img"
      aria-label="主梁计算简图"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- 集中力总标注 -->
      <text :x="W / 2" :y="NOTE_TOP_Y" class="force-text" text-anchor="middle">
        P = G + Q = {{ totalForce }} kN（次梁传来集中力）
      </text>

      <!-- 集中力箭头（三等分，每跨 2 个） -->
      <g v-for="(p, i) in layout.pointLoads" :key="`force-${i}`" class="force">
        <line :x1="p.x" :y1="FORCE_TOP_Y" :x2="p.x" :y2="BEAM_Y - 3" />
        <polygon
          :points="`${p.x - 4},${BEAM_Y - 8} ${p.x + 4},${BEAM_Y - 8} ${p.x},${BEAM_Y - 1}`"
        />
      </g>

      <!-- 主梁 -->
      <rect :x="pad" :y="BEAM_Y" :width="W - 2 * pad" :height="BEAM_H" class="member" />

      <!-- 柱（铰支）：柱顶铰 + 柱身 + 柱底地面 -->
      <g v-for="s in layout.supports" :key="`col-${s.index}`">
        <!-- 柱顶铰（小空心圆） -->
        <circle :cx="s.x" :cy="BEAM_Y + BEAM_H + 2" r="3" class="hinge" />
        <!-- 柱身 -->
        <rect
          :x="s.x - 6" :y="BEAM_Y + BEAM_H + 5"
          :width="12" :height="26"
          class="column"
        />
        <!-- 柱底地面 -->
        <line
          :x1="s.x - 12" :y1="BEAM_Y + BEAM_H + 33"
          :x2="s.x + 12" :y2="BEAM_Y + BEAM_H + 33"
          class="ground"
        />
        <line
          :x1="s.x - 10" :y1="BEAM_Y + BEAM_H + 33"
          :x2="s.x - 6" :y2="BEAM_Y + BEAM_H + 37"
          class="ground"
        />
        <line
          :x1="s.x - 4" :y1="BEAM_Y + BEAM_H + 33"
          :x2="s.x" :y2="BEAM_Y + BEAM_H + 37"
          class="ground"
        />
        <line
          :x1="s.x + 2" :y1="BEAM_Y + BEAM_H + 33"
          :x2="s.x + 6" :y2="BEAM_Y + BEAM_H + 37"
          class="ground"
        />
      </g>

      <!-- 跨度尺寸线（虚线，连接相邻柱底） -->
      <g v-for="(sp, i) in layout.spanMarks" :key="`dim-${i}`" class="dim">
        <line
          :x1="sp.x0" :y1="DIM_Y" :x2="sp.x1" :y2="DIM_Y"
          stroke-dasharray="4 3"
        />
        <line :x1="sp.x0" :y1="DIM_Y - 4" :x2="sp.x0" :y2="DIM_Y + 4" />
        <line :x1="sp.x1" :y1="DIM_Y - 4" :x2="sp.x1" :y2="DIM_Y + 4" />
        <text :x="sp.cx" :y="DIM_Y - 6" text-anchor="middle">
          {{ i === 0 ? `l₀ = ${spanText} m` : 'l₀' }}
        </text>
      </g>

      <!-- 角注 -->
      <text :x="pad" :y="NOTE_BOTTOM_Y" class="note">
        铰支于柱 {{ fmt0(columnWidth) }} × {{ fmt0(columnWidth) }} mm · 集中力作用于三等分点（次梁位置）· 主梁 {{ fmt0(sectionSize.b) }} × {{ fmt0(sectionSize.h) }} mm
      </text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import {
  DEFAULT_PAD,
  DEFAULT_WIDTH,
  layoutMainBeam,
} from '../../composables/useBeamLayout'

interface Props {
  /** 主梁计算跨度 l₀（m），前端由 L2 / main_beam_spans 重建 */
  span: number
  /** 集中力恒载 G（kN） */
  loadG: number
  /** 集中力活载 Q（kN） */
  loadQ: number
  /** 柱宽（mm） */
  columnWidth: number
  /** 主梁截面 b × h（mm） */
  sectionSize: { b: number; h: number }
}

const props = defineProps<Props>()

const W = DEFAULT_WIDTH
const pad = DEFAULT_PAD
const H = 168
const NOTE_TOP_Y = 16
const FORCE_TOP_Y = 26
const BEAM_Y = 62
const BEAM_H = 7
const DIM_Y = 112
const NOTE_BOTTOM_Y = 150

const layout = computed(() => layoutMainBeam({ width: W, pad }))

const totalForce = computed(() => fmt(props.loadG + props.loadQ))
const spanText = computed(() => fmt(props.span))

function fmt(n: number): string {
  return Number.isFinite(n) ? n.toFixed(2) : '—'
}
function fmt0(n: number): string {
  return Number.isFinite(n) ? String(Math.round(n)) : '—'
}
</script>

<style scoped>
.main-beam-diagram {
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

/* 主梁 */
.member {
  fill: var(--foreground);
}

/* 集中力 */
.force {
  stroke: var(--destructive);
  fill: var(--destructive);
  stroke-width: 2.2;
}
.force-text {
  fill: var(--destructive);
  font-size: 11px;
}

/* 柱顶铰 */
.hinge {
  fill: var(--card);
  stroke: var(--muted-foreground);
  stroke-width: 1;
}
/* 柱身 */
.column {
  fill: color-mix(in srgb, var(--muted-foreground) 30%, transparent);
  stroke: var(--muted-foreground);
  stroke-width: 1;
}
/* 地面 */
.ground {
  stroke: var(--muted-foreground);
  stroke-width: 1;
}

/* 跨度尺寸线 */
.dim line {
  stroke: var(--muted-foreground);
  stroke-width: 1;
}
.dim text {
  fill: var(--muted-foreground);
  font-size: 11px;
}

/* 角注 */
.note {
  fill: var(--muted-foreground);
  font-size: 11px;
}

@media (max-width: 560px) {
  .main-beam-diagram {
    overflow-x: auto;
  }
  .diagram-svg {
    min-width: 520px;
  }
}
</style>
