<!-- 次梁抵抗弯矩图：设计弯矩（primary）+ 各跨抵抗弯矩 Mu 带（success，虚线）。
     几何复用 layoutInternalForce；Mu 复用 computeMu。y 量程同时覆盖设计 M 与 Mu。 -->
<template>
  <div v-if="layout" class="rm-diagram">
    <svg :viewBox="`0 0 ${W} ${H}`" class="diagram-svg" role="img"
         aria-label="抵抗弯矩图" preserveAspectRatio="xMidYMid meet">
      <text :x="pad" :y="14" class="axis-title">抵抗弯矩图（kN·m）
        <tspan class="hint" dx="6">— 设计弯矩 / 抵抗弯矩 Mu</tspan>
      </text>
      <line :x1="pad" :y1="zeroY" :x2="W - pad" :y2="zeroY" class="zero" />
      <text :x="pad - 4" :y="topY + 4" class="scale-text" text-anchor="end">{{ fmt(mMin) }}</text>
      <text :x="pad - 4" :y="bottomY + 4" class="scale-text" text-anchor="end">{{ fmt(mMax) }}</text>
      <!-- 设计弯矩填充 + 轮廓 -->
      <path :d="mFill" class="m-fill" />
      <path :d="mOutline" class="m-line" />
      <!-- 抵抗弯矩 Mu 带（每跨水平线） -->
      <line v-for="(b, i) in muBands" :key="'mu-' + i"
            :x1="b.x0" :y1="b.y" :x2="b.x1" :y2="b.y" class="mu-line" />
      <!-- 支座 -->
      <g v-for="(x, i) in layout.supportXs" :key="'s-' + i">
        <polygon :points="`${x},${bottomY + 2} ${x - 4},${bottomY + 9} ${x + 4},${bottomY + 9}`" class="support" />
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DEFAULT_PAD, DEFAULT_WIDTH } from '../../composables/useBeamLayout'
import { layoutInternalForce, type NamedValue } from '../../composables/useInternalForce'
import { computeMu } from '../../composables/useResistingMoment'

interface FlexureRow {
  name: string
  as_provided: number
  h0: number
  width_used: number
}
interface Props {
  moments: NamedValue[]
  rawSpans: number
  edgeSpan: number
  midSpan: number
  flexure: FlexureRow[]
}
const props = defineProps<Props>()

const W = DEFAULT_WIDTH
const pad = DEFAULT_PAD
const H = 160
const topY = 22
const bottomY = 120

// layoutInternalForce 在 moments/shears 任一为空时返回 null；本图只画弯矩，
// 传与 moments 等长的零值剪力占位以满足前置校验（剪力布局计算结果本图不用）。
const layout = computed(() => layoutInternalForce({
  moments: props.moments,
  shears: props.moments.map(() => ({ name: '', value: 0 })),
  rawSpans: props.rawSpans, edgeSpan: props.edgeSpan, midSpan: props.midSpan,
  width: W, pad,
}))

/** 各设计截面 Mu（与 moments 同序：[跨1中, B, 跨2中, C, …]） */
const muList = computed(() => {
  if (!props.flexure.length) return [] as { name: string; mu: number }[]
  return computeMu(props.flexure.map((f) => ({
    name: f.name, as_provided: f.as_provided, h0: f.h0, width_used: f.width_used,
  })))
})

/** y 量程：覆盖设计 M 与 Mu */
const mMax = computed(() => {
  const ms = props.moments.map((m) => m.value)
  const mus = muList.value.map((m) => m.mu)
  return Math.max(0, ...ms, ...mus)
})
const mMin = computed(() => {
  const ms = props.moments.map((m) => m.value)
  const mus = muList.value.map((m) => m.mu)
  return Math.min(0, ...ms, ...mus)
})

function yM(m: number): number {
  const span = mMax.value - mMin.value
  if (!(span > 0)) return (topY + bottomY) / 2
  return topY + ((m - mMin.value) / span) * (bottomY - topY)
}
const zeroY = computed(() => yM(0))
const r = (n: number) => Math.round(n * 10) / 10

/** 设计弯矩轮廓：每跨二次贝塞尔过 [左支座0/支座M, 跨中, 右支座] */
const mOutline = computed(() => {
  const L = layout.value
  if (!L) return ''
  const spans = L.moment.spans
  let d = `M ${r(spans[0].left.x)} ${r(yM(spans[0].left.m))}`
  for (const sp of spans) {
    const p0y = yM(sp.left.m), pcy = yM(sp.mid.m), p2y = yM(sp.right.m)
    const cx = (4 * sp.mid.x - sp.left.x - sp.right.x) / 2
    const cy = (4 * pcy - p0y - p2y) / 2
    d += ` Q ${r(cx)} ${r(cy)} ${r(sp.right.x)} ${r(p2y)}`
  }
  return d
})
const mFill = computed(() => {
  const L = layout.value
  if (!L) return ''
  const spans = L.moment.spans
  const z = zeroY.value
  return `${mOutline.value} L ${r(spans[spans.length - 1].right.x)} ${r(z)} L ${r(spans[0].left.x)} ${r(z)} Z`
})

/** Mu 带：每跨取其「跨中」截面 Mu，画水平线覆盖该跨 */
const muBands = computed(() => {
  const L = layout.value
  if (!L || !muList.value.length) return [] as { x0: number; x1: number; y: number }[]
  const bands: { x0: number; x1: number; y: number }[] = []
  for (let i = 0; i < L.moment.spans.length; i++) {
    const sp = L.moment.spans[i]
    const muMid = muList.value[2 * i] // 跨 i 中截面
    if (muMid) bands.push({ x0: sp.left.x, x1: sp.right.x, y: yM(muMid.mu) })
  }
  return bands
})

function fmt(n: number): string {
  return Number.isFinite(n) ? n.toFixed(1) : '—'
}
</script>

<style scoped>
.rm-diagram { width: 100%; }
.diagram-svg { display: block; width: 100%; height: auto; max-width: 640px; margin: 0 auto; overflow: visible; }
.axis-title { fill: var(--foreground); font-size: var(--text-sm); font-weight: 600; }
.axis-title .hint { fill: var(--muted-foreground); font-weight: 400; font-size: var(--text-xs); }
.zero { stroke: var(--border); stroke-width: 1; }
.scale-text { fill: var(--muted-foreground); font-size: var(--text-xs); }
.m-fill { fill: color-mix(in srgb, var(--primary) 14%, transparent); stroke: none; }
.m-line { fill: none; stroke: var(--primary); stroke-width: 1.8; }
.mu-line { stroke: var(--success); stroke-width: 1.8; stroke-dasharray: 5 3; }
.support { fill: var(--muted-foreground); }
</style>
