import { describe, it, expect } from 'vitest'
import { computeMu } from './useResistingMoment'

describe('computeMu 抵抗弯矩', () => {
  it('按 Mu = fc·b·x·(h0−x/2)，x=fy·As/(fc·b) 计算，返回 kN·m', () => {
    // b=200, h0=360, As=763, fc=9.6, fy=300
    // x = 300*763/(9.6*200) = 119.21875 mm
    // Mu = 9.6*200*119.21875*(360 - 119.21875/2) = 68,759,414 N·mm ≈ 68.76 kN·m
    const r = computeMu([{ name: '1', as_provided: 763, h0: 360, width_used: 200 }])
    expect(r[0].name).toBe('1')
    expect(r[0].mu).toBeCloseTo(68.76, 1)
  })

  it('第一类 T 形用 width_used（即 bf′）作为 b', () => {
    // 同样 As/h0，b 取 bf'=1960 → x 更小、内力臂更大 → Mu 更大
    const r = computeMu([{ name: '1', as_provided: 763, h0: 360, width_used: 1960 }])
    expect(r[0].mu).toBeGreaterThan(68.76)
  })

  it('As=0 时 Mu=0', () => {
    const r = computeMu([{ name: 'B', as_provided: 0, h0: 360, width_used: 200 }])
    expect(r[0].mu).toBe(0)
  })
})
