<template>
  <div v-if="layout" class="if-diagram">
    <svg
      :viewBox="`0 0 ${W} ${H}`"
      class="diagram-svg"
      role="img"
      aria-label="弯矩图与剪力图"
      preserveAspectRatio="xMidYMid meet"
    >
      <!-- ════ 弯矩图 M ════ -->
      <text :x="pad" :y="12" class="axis-title">弯矩图 M（kN·m）<tspan class="hint" dx="6">— 正弯矩下（受拉侧）/ 负弯矩上</tspan></text>
      <!-- 零线 -->
      <line :x1="pad" :y1="mZeroY" :x2="W - pad" :y2="mZeroY" class="zero" />
      <!-- 量程标注 -->
      <text :x="pad - 4" :y="mTopY + 4" class="scale-text" text-anchor="end">{{ fmt(layout.moment.mMin) }}</text>
      <text :x="pad - 4" :y="mBottomY + 4" class="scale-text" text-anchor="end">{{ fmt(layout.moment.mMax) }}</text>
      <!-- 弯矩填充 + 轮廓（每跨二次贝塞尔过三点） -->
      <path :d="mFill" class="m-fill" />
      <path :d="mOutline" class="m-line" />
      <!-- 支座 -->
      <g v-for="(x, i) in layout.supportXs" :key="`ms-${i}`">
        <polygon :points="`${x},${mBottomY + 2} ${x - 4},${mBottomY + 9} ${x + 4},${mBottomY + 9}`" class="support" />
      </g>

      <!-- ════ 剪力图 V ════ -->
      <text :x="pad" :y="vTopY - 6" class="axis-title">剪力图 V（kN）<tspan class="hint" dx="6">— 正上 / 负下，支座处突变</tspan></text>
      <line :x1="pad" :y1="vZeroY" :x2="W - pad" :y2="vZeroY" class="zero" />
      <text :x="pad - 4" :y="vTopY + 4" class="scale-text" text-anchor="end">{{ fmt(layout.shear.vMax) }}</text>
      <text :x="pad - 4" :y="vBottomY + 4" class="scale-text" text-anchor="end">{{ fmt(layout.shear.vMin) }}</text>
      <!-- 剪力填充 + 折线（跨内线性，支座竖向突变） -->
      <polygon :points="vFillPoints" class="v-fill" />
      <polyline :points="vPolylinePoints" class="v-line" />
      <g v-for="(x, i) in layout.supportXs" :key="`vs-${i}`">
        <polygon :points="`${x},${vBottomY + 2} ${x - 4},${vBottomY + 9} ${x + 4},${vBottomY + 9}`" class="support" />
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { DEFAULT_PAD, DEFAULT_WIDTH } from '../../composables/useBeamLayout'
import {
  layoutInternalForce,
  type InternalForceLayout,
  type NamedValue,
} from '../../composables/useInternalForce'

interface Props {
  moments: NamedValue[]
  shears: NamedValue[]
  rawSpans: number
  edgeSpan: number
  midSpan: number
}

const props = defineProps<Props>()

const W = DEFAULT_WIDTH
const pad = DEFAULT_PAD
const H = 270
// 弯矩区
const mTopY = 20
const mBottomY = 110
// 剪力区
const vTopY = 156
const vBottomY = 246

const layout = computed<InternalForceLayout | null>(() =>
  layoutInternalForce({
    moments: props.moments,
    shears: props.shears,
    rawSpans: props.rawSpans,
    edgeSpan: props.edgeSpan,
    midSpan: props.midSpan,
    width: W,
    pad,
  }),
)

/** 弯矩值 → y（正弯矩在下、负弯矩在上） */
function yM(m: number): number {
  const L = layout.value
  if (!L) return (mTopY + mBottomY) / 2
  const span = L.moment.mMax - L.moment.mMin
  if (!(span > 0)) return (mTopY + mBottomY) / 2
  return mTopY + ((m - L.moment.mMin) / span) * (mBottomY - mTopY)
}

/** 剪力值 → y（正剪力在上、负在下） */
function yV(v: number): number {
  const L = layout.value
  if (!L) return (vTopY + vBottomY) / 2
  const span = L.shear.vMax - L.shear.vMin
  if (!(span > 0)) return (vTopY + vBottomY) / 2
  return vTopY + ((L.shear.vMax - v) / span) * (vBottomY - vTopY)
}

const mZeroY = computed(() => yM(0))
const vZeroY = computed(() => yV(0))

const r = (n: number) => Math.round(n * 10) / 10

/** 弯矩轮廓：每跨二次贝塞尔，控制点反算使曲线过跨中点 */
const mOutline = computed(() => {
  const L = layout.value
  if (!L) return ''
  const spans = L.moment.spans
  let d = `M ${r(spans[0].left.x)} ${r(yM(spans[0].left.m))}`
  for (const sp of spans) {
    const p0y = yM(sp.left.m)
    const pcy = yM(sp.mid.m)
    const p2y = yM(sp.right.m)
    // 控制点 P1 = (4·Pc − P0 − P2) / 2，使二次贝塞尔在 t=0.5 过 Pc
    const cx = (4 * sp.mid.x - sp.left.x - sp.right.x) / 2
    const cy = (4 * pcy - p0y - p2y) / 2
    d += ` Q ${r(cx)} ${r(cy)} ${r(sp.right.x)} ${r(p2y)}`
  }
  return d
})

/** 弯矩填充：轮廓 + 闭合到零线 */
const mFill = computed(() => {
  const L = layout.value
  if (!L) return ''
  const spans = L.moment.spans
  const z = mZeroY.value
  return `${mOutline.value} L ${r(spans[spans.length - 1].right.x)} ${r(z)} L ${r(spans[0].left.x)} ${r(z)} Z`
})

/** 剪力折线点（相邻跨在支座处同 x 不同 y → 竖向突变） */
const vPolylinePoints = computed(() => {
  const L = layout.value
  if (!L) return ''
  return L.shear.spans
    .flatMap((sp) => [
      `${r(sp.leftX)},${r(yV(sp.leftV))}`,
      `${r(sp.rightX)},${r(yV(sp.rightV))}`,
    ])
    .join(' ')
})

/** 剪力填充：折线 + 闭合到零线 */
const vFillPoints = computed(() => {
  const L = layout.value
  if (!L) return ''
  const spans = L.shear.spans
  const z = r(vZeroY.value)
  const first = `${r(spans[0].leftX)},${z}`
  const last = `${r(spans[spans.length - 1].rightX)},${z}`
  return `${first} ${vPolylinePoints.value} ${last}`
})

function fmt(n: number): string {
  return Number.isFinite(n) ? n.toFixed(1) : '—'
}
</script>

<style scoped>
.if-diagram {
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

.axis-title {
  fill: var(--foreground);
  font-size: var(--text-sm);
  font-weight: 600;
}
.axis-title .hint {
  fill: var(--muted-foreground);
  font-weight: 400;
  font-size: var(--text-xs);
}

.zero {
  stroke: var(--border);
  stroke-width: 1;
}

.scale-text {
  fill: var(--muted-foreground);
  font-size: var(--text-xs);
}

/* 弯矩 */
.m-fill {
  fill: color-mix(in srgb, var(--primary) 16%, transparent);
  stroke: none;
}
.m-line {
  fill: none;
  stroke: var(--primary);
  stroke-width: 1.8;
}

/* 剪力 */
.v-fill {
  fill: color-mix(in srgb, var(--destructive) 14%, transparent);
  stroke: none;
}
.v-line {
  fill: none;
  stroke: var(--destructive);
  stroke-width: 1.8;
}

.support {
  fill: var(--muted-foreground);
}

@media (max-width: 560px) {
  .if-diagram {
    overflow-x: auto;
  }
  .diagram-svg {
    min-width: 520px;
  }
}
</style>
