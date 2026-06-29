// 抵抗弯矩 Mu 纯函数 —— 供 ResistingMomentDiagram 与计算书 §九 使用。
// 公式：x = fy·As/(fc·b)；Mu = fc·b·x·(h0 − x/2)。
// 单位：fc/fy (N/mm²)、b/h0/As (mm) → Mu (N·mm)，返回换算为 kN·m。
// 材料默认取 report/materials（梁纵筋 HRB335）；板不绘抵抗弯矩图。

import { FC, FY_BEAM } from '../report/materials'

export interface MuInputSection {
  name: string
  as_provided: number
  h0: number
  /** 计算采用的截面宽度（第一类 T 形即 bf′） */
  width_used: number
}

export interface MuResult {
  name: string
  /** 抵抗弯矩 (kN·m) */
  mu: number
}

export function computeMu(
  sections: MuInputSection[],
  fc: number = FC,
  fy: number = FY_BEAM,
): MuResult[] {
  return sections.map((s) => {
    const b = s.width_used > 0 ? s.width_used : 0
    const x = b > 0 && fc > 0 ? (fy * s.as_provided) / (fc * b) : 0
    const muNmm = fc * b * x * (s.h0 - x / 2)
    const mu = muNmm / 1e6
    return { name: s.name, mu: Number.isFinite(mu) ? mu : 0 }
  })
}
