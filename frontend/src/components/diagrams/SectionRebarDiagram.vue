<template>
  <div v-if="sections.length" class="rebar-grid">
    <div v-for="(s, i) in sections" :key="i" class="rebar-card">
      <svg :viewBox="`0 0 ${W} ${H}`" class="section-svg" role="img" :aria-label="`${s.name} 配筋`">
        <!-- 板带截面 -->
        <template v-if="s.shape === 'slab'">
          <rect :x="pad" :y="36" :width="W - 2 * pad" :height="10" class="outline" />
          <circle v-for="(d, k) in bars(s)" :key="k" :cx="d.cx" :cy="50" r="2.6" class="bar" />
          <!-- 板厚标注 -->
          <line :x1="W - pad + 4" :y1="36" :x2="W - pad + 4" :y2="46" class="dim" />
          <text :x="W - pad + 8" :y="44" class="dim-text">h</text>
        </template>

        <!-- T 形截面 -->
        <template v-else-if="s.shape === 't'">
          <rect :x="20" :y="18" :width="80" height="9" class="outline" />
          <rect :x="50" :y="27" width="20" height="40" class="outline" />
          <rect :x="53" :y="30" width="14" height="33" class="stirrup" />
          <circle v-for="(d, k) in bars(s)" :key="k" :cx="d.cx" :cy="62" r="3" class="bar" />
          <circle :cx="56" cy="33" r="2" class="bar" />
          <circle :cx="64" cy="33" r="2" class="bar" />
        </template>

        <!-- 矩形截面（支座） -->
        <template v-else>
          <rect :x="34" :y="16" width="52" height="50" class="outline" />
          <rect :x="38" :y="20" width="44" height="42" class="stirrup" />
          <circle v-for="(d, k) in bars(s)" :key="k" :cx="d.cx" :cy="60" r="3" class="bar" />
          <circle :cx="44" cy="23" r="2" class="bar" />
          <circle :cx="76" cy="23" r="2" class="bar" />
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

/** 受力筋圆点横坐标（板按间距、梁按根数均分） */
function bars(s: RebarSection): { cx: number }[] {
  if (s.shape === 'slab') {
    const spacing = s.bar.spacing ?? 200
    const n = Math.min(Math.max(Math.round(1000 / spacing), 2), 8)
    const x0 = 24
    const x1 = W - 24
    return Array.from({ length: n }, (_, i) => ({
      cx: n === 1 ? (x0 + x1) / 2 : x0 + ((x1 - x0) * i) / (n - 1),
    }))
  }
  const count = Math.max(s.bar.count ?? 2, 1)
  const [x0, x1] = s.shape === 't' ? [54, 66] : [42, 78]
  return Array.from({ length: count }, (_, i) => ({
    cx: count === 1 ? (x0 + x1) / 2 : x0 + ((x1 - x0) * i) / (count - 1),
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
