<template>
  <div v-if="sections.length" class="rebar-grid">
    <div v-for="(s, i) in sections" :key="i" class="rebar-card">
      <svg :viewBox="`0 0 ${W} ${H}`" class="section-svg" role="img" :aria-label="`${s.name} 配筋`">
        <!-- 板带截面 -->
        <template v-if="s.shape === 'slab'">
          <rect :x="pad" :y="36" :width="W - 2 * pad" :height="10" class="outline" />
          <circle v-for="(d, k) in bars(s)" :key="k" :cx="d.cx" :cy="50" :r="d.r" class="bar" />
          <!-- 板厚标注 -->
          <line :x1="W - pad + 4" :y1="36" :x2="W - pad + 4" :y2="46" class="dim" />
          <text :x="W - pad + 8" :y="44" class="dim-text">h</text>
        </template>

        <!-- T 形截面 -->
        <template v-else-if="s.shape === 't'">
          <rect :x="flangeX" :y="12" :width="flangeW" :height="8" class="outline" />
          <rect :x="webX(s.b)" :y="20" :width="webW(s.b)" :height="46" class="outline" />
          <rect :x="webX(s.b) + 3" :y="23" :width="Math.max(webW(s.b) - 6, 4)" :height="40" class="stirrup" />
          <circle v-for="(d, k) in bars(s)" :key="k" :cx="d.cx" :cy="58" :r="d.r" class="bar" />
        </template>

        <!-- 矩形截面（支座） -->
        <template v-else>
          <rect :x="rectX(s.b)" :y="14" :width="rectW(s.b)" :height="52" class="outline" />
          <rect :x="rectX(s.b) + 3" :y="17" :width="Math.max(rectW(s.b) - 6, 4)" :height="46" class="stirrup" />
          <circle v-for="(d, k) in bars(s)" :key="k" :cx="d.cx" :cy="58" :r="d.r" class="bar" />
        </template>
      </svg>
      <div class="rebar-label">
        <span class="rebar-name">{{ s.name }}</span>
        <span class="rebar-bar">{{ barText(s) }}</span>
        <span class="rebar-size">{{ sizeText(s) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface RebarBar {
  diameter: number
  spacing?: number
  count?: number
}

/** 归一化截面描述（页面把 result.reinforcement 转成此结构） */
interface RebarSection {
  name: string
  shape: 'slab' | 't' | 'rect'
  b: number
  h: number
  bar: RebarBar
}

defineProps<{
  sections: RebarSection[]
  /** 箍筋信息（梁 / 主梁用，当前仅用于角注，可不传） */
  stirrup?: { diameter: number; spacing: number; legs: number } | null
}>()

const W = 120
const H = 76
const pad = 15

/** 矩形截面像素宽（按梁宽 b 缩放，限制在画布内）。 */
function rectW(b: number): number {
  return Math.max(40, Math.min(90, (b || 200) * 0.3))
}
function rectX(b: number): number {
  return (W - rectW(b)) / 2
}

/** T 形腹板像素宽（视觉上窄于翼缘，体现 T 形比例）。 */
function webW(b: number): number {
  return Math.max(24, Math.min(36, (b || 200) * 0.15))
}
function webX(b: number): number {
  return (W - webW(b)) / 2
}

const flangeW = 100
const flangeX = (W - flangeW) / 2

/** 钢筋圆点半径：梁筋按 (d/b)×宽px 等比缩放，板按直径缩放。 */
function barRadius(d: number, b: number, widthPx: number, shape: RebarSection['shape']): number {
  if (shape === 'slab') return Math.max(1.8, Math.min(3.5, (d || 8) * 0.12))
  const r = ((d || 12) / (b || 200)) * widthPx / 2
  return Math.max(1.4, Math.min(4.5, r))
}

/** 受力筋圆点横坐标 + 半径（板按间距、梁按根数均分，依梁宽布置） */
function bars(s: RebarSection): { cx: number; r: number }[] {
  if (s.shape === 'slab') {
    const spacing = s.bar.spacing ?? 200
    const n = Math.min(Math.max(Math.round(1000 / spacing), 2), 8)
    const r = barRadius(s.bar.diameter, s.b, W - 2 * 24, s.shape)
    const x0 = 24
    const x1 = W - 24
    return Array.from({ length: n }, (_, i) => ({
      cx: n === 1 ? (x0 + x1) / 2 : x0 + ((x1 - x0) * i) / (n - 1),
      r,
    }))
  }
  const count = Math.max(s.bar.count ?? 2, 1)
  const wPx = s.shape === 't' ? webW(s.b) : rectW(s.b)
  const r = barRadius(s.bar.diameter, s.b, wPx, s.shape)
  const x0 = (W - wPx) / 2
  const margin = r + 3
  const inner0 = x0 + margin
  const inner1 = x0 + wPx - margin
  return Array.from({ length: count }, (_, i) => ({
    cx: count === 1 ? (inner0 + inner1) / 2 : inner0 + ((inner1 - inner0) * i) / (count - 1),
    r,
  }))
}

function barText(s: RebarSection): string {
  if (s.shape === 'slab') return `Φ${s.bar.diameter}@${s.bar.spacing}`
  return `${s.bar.count}Φ${s.bar.diameter}`
}

function sizeText(s: RebarSection): string {
  return s.shape === 'slab' ? `h = ${Math.round(s.h)}` : `b×h = ${Math.round(s.b)}×${Math.round(s.h)}`
}
</script>

<style scoped>
.rebar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: var(--space-3);
}
.rebar-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  background: color-mix(in srgb, var(--muted) 30%, transparent);
}
.section-svg {
  width: 100%;
  max-width: 130px;
  height: auto;
}

.outline {
  fill: color-mix(in srgb, var(--foreground) 10%, transparent);
  stroke: var(--foreground);
  stroke-width: 1.6;
}
.stirrup {
  fill: none;
  stroke: var(--muted-foreground);
  stroke-width: 1.2;
}
.bar {
  fill: var(--foreground);
}
.dim {
  stroke: var(--muted-foreground);
  stroke-width: 1;
}
.dim-text {
  fill: var(--muted-foreground);
  font-size: 9px;
}

.rebar-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  font-size: var(--text-sm);
  line-height: 1.3;
}
.rebar-name {
  font-weight: 600;
  color: var(--foreground);
}
.rebar-bar {
  color: var(--primary);
  font-weight: 600;
}
.rebar-size {
  color: var(--muted-foreground);
  font-size: var(--text-xs);
}

@media (max-width: 480px) {
  .rebar-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
}
</style>
