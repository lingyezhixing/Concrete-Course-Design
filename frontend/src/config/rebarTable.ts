/**
 * 附表 3-1 钢筋的公称直径、公称截面积及理论质量
 *
 * 梁纵向受力筋按「根数 × 直径」配筋，候选方案需同时满足：
 *   1. As = n × 单根公称面积 ≥ As_required
 *   2. 净距 (b − n·d)/(n+1) ≥ 25mm（GB 50010 下部筋最小净距，单层布置）
 */

/** 梁纵向受力筋常用公称直径 (mm)，取自附表 3-1。 */
export const REBAR_DIAMETERS = [12, 14, 16, 18, 20, 22, 25, 28, 32] as const

/** 候选根数范围（单层布置）。 */
export const REBAR_COUNTS = [2, 3, 4, 5, 6, 7, 8] as const

/** 附表 3-1 单根钢筋公称截面积 (mm²)。 */
const SINGLE_BAR_AREA: Record<number, number> = {
  12: 113.1,
  14: 153.9,
  16: 201.1,
  18: 254.5,
  20: 314.2,
  22: 380.1,
  25: 490.9,
  28: 615.8,
  32: 804.2,
}

/** n 根直径 d 钢筋的总面积 (mm²)。 */
export function barArea(diameter: number, count: number): number {
  const single = SINGLE_BAR_AREA[diameter] ?? (Math.PI * diameter * diameter) / 4
  return single * count
}

/** 梁宽方向钢筋净距 (b − n·d)/(n+1) (mm)。 */
export function barClearance(beamWidth: number, count: number, diameter: number): number {
  return (beamWidth - count * diameter) / (count + 1)
}

/** 净距是否满足 ≥ 25mm。 */
export function spacingOk(beamWidth: number, count: number, diameter: number): boolean {
  return barClearance(beamWidth, count, diameter) >= 25
}

/** 给定梁宽下可选根数（至少存在一个直径满足净距要求）。 */
export function countOptions(beamWidth: number): number[] {
  return REBAR_COUNTS.filter((n) => REBAR_DIAMETERS.some((d) => spacingOk(beamWidth, n, d)))
}

/** 给定根数下可选直径（同时满足净距与 As ≥ asRequired）。 */
export function diameterOptions(
  beamWidth: number,
  count: number,
  asRequired: number,
): number[] {
  return REBAR_DIAMETERS.filter(
    (d) => spacingOk(beamWidth, count, d) && barArea(d, count) >= asRequired,
  )
}

/**
 * 配筋状态判定（与后端 flexure_status 一致）。
 * - 实配为 0 → "不足"
 * - 实配 / 需要 > 1.8 → "建议复核"
 * - 否则 → "推荐"
 */
export function reinfStatus(asRequired: number, asProvided: number): string {
  if (asProvided === 0) return '不足'
  if (asProvided / asRequired > 1.8) return '建议复核'
  return '推荐'
}

// ──────────────────────────────────────────────
// 板配筋（直径 + 间距，按每米板宽）
// ──────────────────────────────────────────────

/** 板常用钢筋直径 (mm)。 */
export const SLAB_DIAMETERS = [8, 10, 12, 14] as const

/** 板常用间距 (mm)（标准集合，已满足构造要求）。 */
export const SLAB_SPACINGS = [200, 180, 150, 120, 100, 80] as const

/** 每米板宽钢筋面积 (mm²/m)：单根面积 × (1000/s)。 */
export function slabAreaPerMeter(diameter: number, spacing: number): number {
  return (Math.PI * diameter * diameter) / 4 * (1000 / spacing)
}

/** 可选直径（至少存在一个间距满足 As ≥ asRequired）。 */
export function slabDiameterOptions(asRequired: number): number[] {
  return SLAB_DIAMETERS.filter((d) =>
    SLAB_SPACINGS.some((s) => slabAreaPerMeter(d, s) >= asRequired),
  )
}

/** 给定直径下可选间距（满足 As ≥ asRequired）。 */
export function slabSpacingOptions(diameter: number, asRequired: number): number[] {
  return SLAB_SPACINGS.filter((s) => slabAreaPerMeter(diameter, s) >= asRequired)
}
