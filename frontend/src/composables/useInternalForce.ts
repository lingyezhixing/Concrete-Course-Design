/**
 * 弯矩图 / 剪力图布局 —— 把 result.internal_forces 的控制截面值组织成
 * 「每跨的控制点 + 量程」，供 InternalForceDiagram 绘制。
 *
 * 板 / 次梁为均布荷载等跨连续梁：
 *  - 弯矩沿跨为抛物线 → 每跨用 [左支座 M, 跨中 M, 右支座 M] 三点，组件以二次贝塞尔精确过三点
 *  - 剪力沿跨为线性   → 每跨用 [左端 V, 右端 V]，支座处突变
 * 主梁不在此列（控制点不足）。
 *
 * 详见 docs/superpowers/specs/2026-06-29-rebar-and-internal-force-diagrams-design.md。
 */

import {
  DEFAULT_PAD,
  DEFAULT_WIDTH,
  layoutUniformBeam,
} from './useBeamLayout'

export interface NamedValue {
  name: string
  value: number
}

export interface InternalForceInput {
  moments: NamedValue[]
  shears: NamedValue[]
  rawSpans: number
  edgeSpan: number
  midSpan: number
  width?: number
  pad?: number
}

/** 弯矩控制点：横坐标 + 弯矩值（kN·m） */
export interface MomentControl {
  x: number
  m: number
}

/** 单跨弯矩三点 */
export interface MomentSpan {
  left: MomentControl
  mid: MomentControl
  right: MomentControl
}

/** 单跨剪力两端 */
export interface ShearSpan {
  leftX: number
  leftV: number
  rightX: number
  rightV: number
}

export interface InternalForceLayout {
  eqSpans: number
  /** 支座 x（eqSpans + 1），与计算简图共用 */
  supportXs: number[]
  moment: {
    spans: MomentSpan[]
    /** 弯矩量程（含 0），用于统一缩放到画布 y */
    mMax: number
    mMin: number
  }
  shear: {
    spans: ShearSpan[]
    vMax: number
    vMin: number
  }
}

/**
 * 计算弯矩 / 剪力图布局。
 *
 * moments 顺序约定：`[跨1中, 支座B, 跨2中, 支座C, …, 跨n中]`（长度 2n−1）。
 * shears  顺序约定：`[VA, B左, B右, C左, C右, …, 末端左]`（长度 2n）。
 * 端支座弯矩取 0（连续板/梁边支座按铰支）。
 *
 * @returns 跨数 < 2、跨度 ≤ 0、或 moments/shears 为空时返回 `null`
 */
export function layoutInternalForce(
  input: InternalForceInput,
): InternalForceLayout | null {
  const { moments, shears, rawSpans, edgeSpan, midSpan } = input
  const width = input.width ?? DEFAULT_WIDTH
  const pad = input.pad ?? DEFAULT_PAD

  if (!Number.isFinite(rawSpans) || rawSpans < 2) return null
  if (!(edgeSpan > 0) || !(midSpan > 0)) return null
  if (!moments.length || !shears.length) return null

  const beam = layoutUniformBeam(rawSpans, edgeSpan, midSpan, { width, pad })
  if (!beam) return null
  const eqSpans = beam.eqSpans
  const supportXs = beam.supports.map((s) => s.x)
  const spanCx = beam.spans.map((s) => s.cx)

  const mVals = moments.map((m) => (Number.isFinite(m?.value) ? m.value : 0))
  const vVals = shears.map((s) => (Number.isFinite(s?.value) ? s.value : 0))

  // 弯矩：每跨 [左支座, 跨中, 右支座]
  const momentSpans: MomentSpan[] = []
  const allM: number[] = [0]
  for (let i = 0; i < eqSpans; i++) {
    const leftM = i === 0 ? 0 : (mVals[2 * i - 1] ?? 0)
    const rightM = i === eqSpans - 1 ? 0 : (mVals[2 * i + 1] ?? 0)
    const midM = mVals[2 * i] ?? 0
    momentSpans.push({
      left: { x: supportXs[i], m: leftM },
      mid: { x: spanCx[i], m: midM },
      right: { x: supportXs[i + 1], m: rightM },
    })
    allM.push(leftM, midM, rightM)
  }

  // 剪力：每跨 [左端, 右端]
  const shearSpans: ShearSpan[] = []
  const allV: number[] = [0]
  for (let i = 0; i < eqSpans; i++) {
    const leftV = vVals[2 * i] ?? 0
    const rightV = vVals[2 * i + 1] ?? 0
    shearSpans.push({
      leftX: supportXs[i],
      leftV,
      rightX: supportXs[i + 1],
      rightV,
    })
    allV.push(leftV, rightV)
  }

  return {
    eqSpans,
    supportXs,
    moment: {
      spans: momentSpans,
      mMax: Math.max(...allM),
      mMin: Math.min(...allM),
    },
    shear: {
      spans: shearSpans,
      vMax: Math.max(...allV),
      vMin: Math.min(...allV),
    },
  }
}
