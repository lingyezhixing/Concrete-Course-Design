import { describe, expect, it } from 'vitest'

import {
  DEFAULT_PAD,
  DEFAULT_WIDTH,
  layoutMainBeam,
  layoutUniformBeam,
} from './useBeamLayout'

describe('layoutUniformBeam', () => {
  describe('跨数钳制', () => {
    it('2~5 跨原样保留', () => {
      expect(layoutUniformBeam(2, 2, 2)?.eqSpans).toBe(2)
      expect(layoutUniformBeam(3, 2, 2)?.eqSpans).toBe(3)
      expect(layoutUniformBeam(4, 2, 2)?.eqSpans).toBe(4)
      expect(layoutUniformBeam(5, 2, 2)?.eqSpans).toBe(5)
    })

    it('>5 跨等效为 5 跨', () => {
      expect(layoutUniformBeam(6, 2, 2)?.eqSpans).toBe(5)
      expect(layoutUniformBeam(9, 2, 2)?.eqSpans).toBe(5)
    })
  })

  describe('五跨等效标志', () => {
    it('≤5 跨不触发等效', () => {
      for (let n = 2; n <= 5; n++) {
        const r = layoutUniformBeam(n, 2, 2)
        expect(r?.isEquiv).toBe(false)
        expect(r?.equivRepresents).toBe(0)
        expect(r?.equivNote).toBe('')
      }
    })

    it('>5 跨触发等效，equivRepresents = 原始跨数 − 4', () => {
      expect(layoutUniformBeam(6, 2, 2)?.equivRepresents).toBe(2)
      expect(layoutUniformBeam(7, 2, 2)?.equivRepresents).toBe(3)
      expect(layoutUniformBeam(9, 2, 2)?.equivRepresents).toBe(5)
    })

    it('9 跨等效说明文字指明代表的跨区间', () => {
      expect(layoutUniformBeam(9, 2, 2)?.equivNote).toContain('第 3 ~ 7 跨')
    })
  })

  describe('逐跨长度（等跨连续梁）', () => {
    it('5 跨：两端边跨、三个中跨', () => {
      const r = layoutUniformBeam(5, 2.2, 2.0)
      const lens = r!.spans.map((s) => s.length)
      expect(lens).toEqual([2.2, 2.0, 2.0, 2.0, 2.2])
    })

    it('2 跨：两跨均为边跨', () => {
      const r = layoutUniformBeam(2, 2.2, 2.0)
      const lens = r!.spans.map((s) => s.length)
      expect(lens).toEqual([2.2, 2.2])
    })

    it('3 跨：边-中-边', () => {
      const r = layoutUniformBeam(3, 2.2, 2.0)
      const lens = r!.spans.map((s) => s.length)
      expect(lens).toEqual([2.2, 2.0, 2.2])
    })
  })

  describe('支座', () => {
    it('支座数 = 跨数 + 1', () => {
      expect(layoutUniformBeam(2, 2, 2)?.supports.length).toBe(3)
      expect(layoutUniformBeam(5, 2, 2)?.supports.length).toBe(6)
      expect(layoutUniformBeam(9, 2, 2)?.supports.length).toBe(6) // 等效后仍 6
    })

    it('首支座位于 pad，末支座位于 width − pad', () => {
      const r = layoutUniformBeam(5, 2, 2)!
      expect(r.supports[0].x).toBeCloseTo(DEFAULT_PAD)
      expect(r.supports[r.supports.length - 1].x).toBeCloseTo(DEFAULT_WIDTH - DEFAULT_PAD)
    })

    it('支座 x 单调递增', () => {
      const r = layoutUniformBeam(5, 2.2, 2.0)!
      for (let i = 1; i < r.supports.length; i++) {
        expect(r.supports[i].x).toBeGreaterThan(r.supports[i - 1].x)
      }
    })

    it('不等跨长度按比例反映到支座间距（边跨更长）', () => {
      // edge=4, mid=2，5 跨 → 边跨像素宽应为中跨的 2 倍
      const r = layoutUniformBeam(5, 4, 2)!
      const edgePx = r.spans[0].x1 - r.spans[0].x0
      const midPx = r.spans[1].x1 - r.spans[1].x0
      expect(edgePx / midPx).toBeCloseTo(2, 5)
    })
  })

  describe('等效跨标记', () => {
    it('>5 跨时第 3 跨（索引 2）标记为等效跨，其余否', () => {
      const r = layoutUniformBeam(9, 2, 2)!
      expect(r.spans.map((s) => s.isEquiv)).toEqual([
        false,
        false,
        true,
        false,
        false,
      ])
      expect(r.spans[2].label).toBe('中间等效跨')
    })

    it('未等效时无等效跨', () => {
      const r = layoutUniformBeam(5, 2, 2)!
      expect(r.spans.every((s) => !s.isEquiv)).toBe(true)
    })

    it('跨度标注：边跨 l₀₁、中跨 l₀₂', () => {
      const r = layoutUniformBeam(5, 2, 2)!
      expect(r.spans[0].label).toBe('l₀₁')
      expect(r.spans[1].label).toBe('l₀₂')
      expect(r.spans[4].label).toBe('l₀₁')
    })
  })

  describe('均布荷载箭头', () => {
    it('非空且落在 [pad, width−pad] 内', () => {
      const r = layoutUniformBeam(3, 2, 2)!
      expect(r.loadArrows.length).toBeGreaterThan(0)
      for (const x of r.loadArrows) {
        expect(x).toBeGreaterThanOrEqual(DEFAULT_PAD)
        expect(x).toBeLessThanOrEqual(DEFAULT_WIDTH - DEFAULT_PAD)
      }
    })
  })

  describe('非法输入', () => {
    it('跨数 < 2 返回 null', () => {
      expect(layoutUniformBeam(1, 2, 2)).toBeNull()
      expect(layoutUniformBeam(0, 2, 2)).toBeNull()
    })
    it('跨度 ≤ 0 返回 null', () => {
      expect(layoutUniformBeam(5, 0, 2)).toBeNull()
      expect(layoutUniformBeam(5, 2, -1)).toBeNull()
    })
    it('非有限值返回 null', () => {
      expect(layoutUniformBeam(Number.NaN, 2, 2)).toBeNull()
    })
  })
})

describe('layoutMainBeam', () => {
  it('固定 3 跨、4 个支座', () => {
    const r = layoutMainBeam()
    expect(r.spans).toBe(3)
    expect(r.supports.length).toBe(4)
  })

  it('每跨 2 个集中力，共 6 个', () => {
    const r = layoutMainBeam()
    expect(r.pointLoads.length).toBe(6)
    // 每跨恰好 2 个
    for (let i = 0; i < 3; i++) {
      const cnt = r.pointLoads.filter((p) => p.spanIndex === i).length
      expect(cnt).toBe(2)
    }
  })

  it('集中力位于各跨 1/3 与 2/3 处', () => {
    const r = layoutMainBeam({ width: 600, pad: 32 })
    const spanW = (600 - 64) / 3
    const s0 = r.supports[0].x
    // 第 0 跨的两个集中力
    expect(r.pointLoads[0].x).toBeCloseTo(s0 + spanW / 3, 5)
    expect(r.pointLoads[1].x).toBeCloseTo(s0 + (spanW * 2) / 3, 5)
  })

  it('三等跨：各跨像素宽相等', () => {
    const r = layoutMainBeam()
    const ws = r.spanMarks.map((s) => s.x1 - s.x0)
    expect(ws[0]).toBeCloseTo(ws[1], 5)
    expect(ws[1]).toBeCloseTo(ws[2], 5)
  })

  it('支座覆盖 [pad, width−pad]', () => {
    const r = layoutMainBeam({ width: 600, pad: 32 })
    expect(r.supports[0].x).toBeCloseTo(32)
    expect(r.supports[3].x).toBeCloseTo(600 - 32)
  })
})
